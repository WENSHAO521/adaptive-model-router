#!/usr/bin/env python3
"""Build and verify an allowlisted runtime ZIP; no network or dependencies."""

import argparse
import hashlib
import json
import re
import stat
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

from validate_skill import RUNTIME_FILES, release_version, safe_file, validate


NAME = 'adaptive-model-router'
SOURCE_URL = 'https://github.com/WENSHAO521/adaptive-model-router/blob'
ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def runtime_readme(text, version):
    """Keep runtime links local; point development-only links at the frozen tag."""
    def replace(match):
        dest = match[1]
        parsed = urlsplit(dest)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return match[0]
        relative = unquote(parsed.path).removeprefix('./')
        if relative in RUNTIME_FILES:
            return match[0]
        return '](' + SOURCE_URL + '/v' + version + '/' + dest
    return re.sub(r'\]\(([^\s)]+)', replace, text)


def collect_runtime(root, version):
    files = {}
    for relative in sorted(RUNTIME_FILES):
        # Newline normalization removes Windows checkout differences. All
        # allowlisted files are UTF-8 text; policies/metadata are not rewritten.
        text = safe_file(root, relative).read_text(encoding='utf-8')
        if relative == 'README.md':
            text = runtime_readme(text, version)
        files[f'{NAME}/{relative}'] = text.encode('utf-8')
    return files


def verify_archive(archive, version, expected=None):
    """Check exact members before extraction, then run shared runtime checks."""
    expected_names = {f'{NAME}/{relative}' for relative in RUNTIME_FILES}
    with zipfile.ZipFile(archive) as zipped:
        infos = zipped.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or set(names) != expected_names:
            raise ValueError('ZIP must contain exactly the nine allowlisted runtime files under one folder')
        for info in infos:
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError('ZIP symlink is forbidden')
            if info.file_size > 2_000_000:
                raise ValueError('unexpectedly large runtime text file')
        payload = {info.filename: zipped.read(info) for info in infos}
    if expected is not None and payload != expected:
        raise ValueError('ZIP payload differs from the validated source snapshot')
    readme = payload[f'{NAME}/README.md'].decode('utf-8')
    if f'Repository version: **v{version}**' not in readme:
        raise ValueError('ZIP README version does not match VERSION')
    with tempfile.TemporaryDirectory(prefix='router-runtime-check-') as temporary:
        # Names were matched against a fixed allowlist before any writes.
        folder = Path(temporary)
        for name, data in payload.items():
            target = folder / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        errors, _ = validate(folder / NAME, mode='runtime')
        if errors:
            raise ValueError('runtime validation failed: ' + '; '.join(errors))
    return {name.removeprefix(NAME + '/'): sha256(data)
            for name, data in sorted(payload.items())}


def manifest(version, archive_name, digest, hashes):
    return {
        'name': NAME, 'version': version, 'release_type': 'runtime',
        'required_entrypoint': 'SKILL.md', 'includes': sorted(RUNTIME_FILES),
        'artifact': archive_name, 'sha256': digest, 'file_sha256': hashes,
    }


def verify_artifacts(archive, root):
    archive = Path(archive)
    version = release_version(root)
    if archive.name != f'{NAME}-v{version}.zip':
        raise ValueError('artifact filename does not match VERSION')
    hashes = verify_archive(archive, version)
    digest = sha256(archive.read_bytes())
    checksum = archive.with_suffix('.zip.sha256').read_text(encoding='utf-8')
    if checksum != f'{digest}  {archive.name}\n':
        raise ValueError('checksum sidecar mismatch')
    record = json.loads((archive.parent / 'release-manifest.json').read_text(encoding='utf-8'))
    if record != manifest(version, archive.name, digest, hashes):
        raise ValueError('release manifest mismatch')
    return digest


def build(root, out_dir, version=None):
    root = Path(root).resolve()
    errors, _ = validate(root)
    if errors:
        raise ValueError('source validation failed: ' + '; '.join(errors))
    actual_version = release_version(root)
    if version is not None and version != actual_version:
        raise ValueError('--version disagrees with VERSION')
    version = actual_version
    files = collect_runtime(root, version)
    archive_name = f'{NAME}-v{version}.zip'
    # Build/validate away from final output. No partial artifact is published
    # by a failed source or extracted-runtime validation.
    with tempfile.TemporaryDirectory(prefix='router-build-') as temporary:
        candidate = Path(temporary) / archive_name
        with zipfile.ZipFile(candidate, 'w', compression=zipfile.ZIP_STORED) as zipped:
            for name, data in files.items():
                info = zipfile.ZipInfo(name, date_time=ZIP_TIME)
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                info.compress_type = zipfile.ZIP_STORED
                zipped.writestr(info, data)
        hashes = verify_archive(candidate, version, expected=files)
        data = candidate.read_bytes()
    digest = sha256(data)
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / archive_name
    archive.write_bytes(data)
    archive.with_suffix('.zip.sha256').write_bytes(f'{digest}  {archive_name}\n'.encode('utf-8'))
    record = manifest(version, archive_name, digest, hashes)
    (output / 'release-manifest.json').write_bytes(
        (json.dumps(record, indent=2, sort_keys=True) + '\n').encode('utf-8'))
    verify_artifacts(archive, root)
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out-dir', type=Path, default=Path('dist'))
    parser.add_argument('--version', help='optional assertion; must match VERSION')
    parser.add_argument('--verify', type=Path, help='verify an existing ZIP and its two sidecars')
    args = parser.parse_args()
    try:
        if args.verify:
            if args.version and args.version != release_version(args.root):
                raise ValueError('--version disagrees with VERSION')
            print('PASS: extracted runtime, manifest, and SHA-256: ' + verify_artifacts(args.verify, args.root))
        else:
            archive = build(args.root, args.out_dir, args.version)
            print(archive)
            print(archive.with_suffix('.zip.sha256'))
            print(archive.parent / 'release-manifest.json')
            print('PASS: source and extracted runtime validated; nine allowlisted files')
        return 0
    except (OSError, ValueError, UnicodeError, zipfile.BadZipFile) as exc:
        print(f'FAIL: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
