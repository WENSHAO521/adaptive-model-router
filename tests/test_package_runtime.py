"""Packaging regression tests: build/verify use isolated temp roots and
temp output directories; no network or model calls, no writes under dist/."""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location('validate_skill', SCRIPTS / 'validate_skill.py')
validate_skill = importlib.util.module_from_spec(spec)
sys.modules['validate_skill'] = validate_skill
spec.loader.exec_module(validate_skill)

spec = importlib.util.spec_from_file_location('package_runtime', SCRIPTS / 'package_runtime.py')
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


class PackagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'src'
        for relative in validate_skill.REQUIRED:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        self.out_dir = Path(self.temp.name) / 'dist'
        self.version = validate_skill.release_version(self.root)

    def build(self):
        return packager.build(self.root, self.out_dir)

    def archive_path(self):
        return self.out_dir / f'adaptive-model-router-v{self.version}.zip'

    def test_build_produces_three_artifacts(self):
        archive = self.build()
        self.assertEqual(archive, self.archive_path())
        self.assertTrue(archive.is_file())
        self.assertTrue(archive.with_suffix('.zip.sha256').is_file())
        self.assertTrue((self.out_dir / 'release-manifest.json').is_file())

    def test_archive_contains_exactly_nine_allowlisted_members(self):
        archive = self.build()
        with zipfile.ZipFile(archive) as zipped:
            names = set(zipped.namelist())
        expected = {f'adaptive-model-router/{relative}' for relative in validate_skill.RUNTIME_FILES}
        self.assertEqual(names, expected)
        self.assertEqual(len(expected), 9)

    def test_build_is_deterministic_byte_for_byte(self):
        first = self.build().read_bytes()
        second_out = Path(self.temp.name) / 'dist2'
        second = packager.build(self.root, second_out).read_bytes()
        self.assertEqual(first, second)

    def test_checksum_sidecar_matches_archive(self):
        archive = self.build()
        digest = packager.sha256(archive.read_bytes())
        sidecar = archive.with_suffix('.zip.sha256').read_text(encoding='utf-8')
        self.assertEqual(sidecar, f'{digest}  {archive.name}\n')

    def test_manifest_matches_archive_and_files(self):
        archive = self.build()
        digest = packager.sha256(archive.read_bytes())
        record = json.loads((self.out_dir / 'release-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(record['version'], self.version)
        self.assertEqual(record['sha256'], digest)
        self.assertEqual(set(record['includes']), set(validate_skill.RUNTIME_FILES))
        self.assertEqual(set(record['file_sha256']), set(validate_skill.RUNTIME_FILES))

    def test_verify_artifacts_accepts_freshly_built_release(self):
        archive = self.build()
        digest = packager.verify_artifacts(archive, self.root)
        self.assertEqual(digest, packager.sha256(archive.read_bytes()))

    def test_verify_rejects_tampered_member(self):
        archive = self.build()
        with zipfile.ZipFile(archive) as zipped:
            original = {info.filename: zipped.read(info) for info in zipped.infolist()}
        tampered_payload = dict(original)
        tampered_payload['adaptive-model-router/README.md'] += b'\ntampered\n'
        tampered = self.out_dir / 'tampered.zip'
        with zipfile.ZipFile(tampered, 'w', compression=zipfile.ZIP_STORED) as zipped:
            for name, data in tampered_payload.items():
                zipped.writestr(name, data)
        with self.assertRaises(ValueError):
            packager.verify_archive(tampered, self.version, expected=original)

    def test_verify_artifacts_rejects_wrong_filename(self):
        archive = self.build()
        renamed = archive.with_name('adaptive-model-router-v9.9.9.zip')
        archive.rename(renamed)
        with self.assertRaises(ValueError):
            packager.verify_artifacts(renamed, self.root)

    def test_verify_artifacts_rejects_checksum_mismatch(self):
        archive = self.build()
        sidecar = archive.with_suffix('.zip.sha256')
        sidecar.write_text(f'0000000000000000000000000000000000000000000000000000000000000000  {archive.name}\n',
                            encoding='utf-8')
        with self.assertRaises(ValueError):
            packager.verify_artifacts(archive, self.root)

    def test_verify_artifacts_rejects_manifest_mismatch(self):
        archive = self.build()
        manifest_path = self.out_dir / 'release-manifest.json'
        record = json.loads(manifest_path.read_text(encoding='utf-8'))
        record['version'] = '9.9.9'
        manifest_path.write_text(json.dumps(record), encoding='utf-8')
        with self.assertRaises(ValueError):
            packager.verify_artifacts(archive, self.root)

    def test_build_rejects_version_mismatch_argument(self):
        with self.assertRaises(ValueError):
            packager.build(self.root, self.out_dir, version='9.9.9')

    def test_build_fails_closed_on_invalid_source(self):
        (self.root / 'references/paper-workflow.md').unlink()
        with self.assertRaises(ValueError):
            self.build()
        self.assertFalse(self.archive_path().exists())

    def test_readme_rewrites_non_runtime_links_to_tagged_source(self):
        readme = (self.root / 'README.md').read_text(encoding='utf-8')
        readme += '\n[Tests](tests/test_validate_skill.py)\n'
        rewritten = packager.runtime_readme(readme, self.version)
        self.assertIn(f'{packager.SOURCE_URL}/v{self.version}/tests/test_validate_skill.py', rewritten)

    def test_readme_preserves_runtime_relative_links(self):
        readme = (self.root / 'README.md').read_text(encoding='utf-8')
        readme += '\n[Routing policy](references/routing-policy.md)\n'
        rewritten = packager.runtime_readme(readme, self.version)
        self.assertIn('](references/routing-policy.md)', rewritten)

    def test_readme_preserves_remote_links(self):
        readme = 'See [docs](https://example.com/docs) for details.\n'
        rewritten = packager.runtime_readme(readme, self.version)
        self.assertEqual(rewritten, readme)

    def test_cli_build_then_verify_round_trip(self):
        build = subprocess.run(
            [sys.executable, str(SCRIPTS / 'package_runtime.py'),
             '--root', str(self.root), '--out-dir', str(self.out_dir)],
            capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        self.assertIn('PASS:', build.stdout)
        verify = subprocess.run(
            [sys.executable, str(SCRIPTS / 'package_runtime.py'),
             '--root', str(self.root), '--verify', str(self.archive_path())],
            capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
        self.assertIn('PASS:', verify.stdout)

    def test_cli_reports_failure_without_traceback(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / 'package_runtime.py'),
             '--root', str(self.root), '--verify', str(self.out_dir / 'missing.zip')],
            capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 1)
        self.assertIn('FAIL:', result.stdout)
        self.assertEqual(result.stderr, '')


if __name__ == '__main__':
    unittest.main()
