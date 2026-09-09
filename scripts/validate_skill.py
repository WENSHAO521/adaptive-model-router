#!/usr/bin/env python3
"""Offline repository/fixture integrity checks, not a model-routing evaluator.

Only this repository's simple YAML mappings are supported: plain safe strings,
JSON-style double-quoted strings, and booleans. Unsupported YAML fails closed.
"""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


RUNTIME_FILES = (
    'SKILL.md', 'README.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md',
    'agents/openai.yaml', 'references/routing-policy.md',
    'references/delegation-policy.md', 'references/paper-workflow.md',
    'references/records.md',
)
REQUIRED = (
    'SKILL.md', 'README.md', 'CHANGELOG.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md',
    'agents/openai.yaml', 'references/routing-policy.md',
    'references/delegation-policy.md', 'references/paper-workflow.md',
    'references/records.md', 'scripts/validate_skill.py',
    'tests/test_validate_skill.py', '.github/workflows/validate.yml',
    'evals/routing-cases.jsonl', 'evals/delegation-cases.jsonl',
    'evals/escalation-cases.jsonl',
    'VERSION', 'scripts/package_runtime.py', 'tests/test_package_runtime.py',
    'RELEASE_CHECKLIST.md',
)
STATES = {
    'PASS', 'PASS_WITH_LIMITATIONS', 'REPAIR_REQUIRED',
    'BLOCKED_BY_MISSING_EVIDENCE', 'BLOCKED_BY_TOOL_FAILURE',
    'ESCALATION_CANDIDATE',
}
ACTIONS = {
    'execute', 'stay_active', 'report_unavailable', 'repair', 'raise_effort',
    'escalate_tier', 'retrieve', 'fix_tool', 'request_permission',
    'reduce_context', 'expert_dispatch', 'report_limitations',
}
TIERS = {'Luna', 'Terra', 'Sol', 'Astra', 'active'}
CONTEXT = {'direct', 'inspect', 'selective', 'compact', 'partition'}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f'non-standard JSON constant: {value}')


def parse_json(text):
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def yaml_scalar(value):
    value = value.rstrip()
    if value.startswith('"'):
        result = parse_json(value)
        if not isinstance(result, str):
            raise ValueError('expected a quoted string')
        return result
    if value in ('true', 'false'):
        return value == 'true'
    # Deliberately narrow: no tags, anchors, flow collections, comments,
    # block scalars, implicit numeric/null scalars, or YAML escape variants.
    if (not re.fullmatch(r'[A-Za-z][^\n\r\t]*', value)
            or any(c in value for c in ':#{}[]&*!|>\'"')
            or value.lower() in {'null', 'yes', 'no', 'on', 'off', 'true', 'false'}):
        raise ValueError('unsupported YAML scalar; use a JSON-style quoted string')
    return value


def yaml_mapping(text):
    """Parse a two-level mapping subset; reject duplicates/unknown indentation."""
    result, section = {}, None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = re.fullmatch(r'( {0}| {2})([a-z_][a-z0-9_-]*):(?: (.*))?', line)
        if not match:
            raise ValueError(f'unsupported YAML mapping at line {number}')
        indent, key, value = match.groups()
        if indent:
            if section is None:
                raise ValueError(f'orphan YAML field at line {number}')
            target = result[section]
        else:
            target = result
            section = None
        if key in target:
            raise ValueError(f'duplicate YAML key: {key}')
        if value is None or value == '':
            if indent:
                raise ValueError('YAML nesting deeper than two levels is unsupported')
            target[key] = {}
            section = key
        else:
            target[key] = yaml_scalar(value)
    return result


def outside_fences(text):
    lines, fence_char, fence_length = [], None, 0
    for line in text.splitlines():
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if fence_char is None:
            if marker:
                fence_char, fence_length = marker[1][0], len(marker[1])
            else:
                lines.append(line)
        elif (marker and marker[1][0] == fence_char
              and len(marker[1]) >= fence_length and not marker[2].strip()):
            fence_char = None
    if fence_char:
        raise ValueError('unclosed Markdown code fence')
    return '\n'.join(lines)


def local_links(text):
    text = outside_fences(text)
    definitions = {
        key.strip().casefold(): dest
        for key, dest in re.findall(r'^\s*\[([^\]]+)\]:\s*(\S+)', text, re.M)
    }
    pattern = r"""!?\[[^\]\n]+\]\((<[^>]+>|[^\s)]+)(?:\s+(?:"[^"]*"|'[^']*'|\([^)]*\)))?\)"""
    links = re.findall(pattern, text)
    for label, key in re.findall(r'!?\[([^\]\n]+)\]\[([^\]\n]*)\]', text):
        lookup = (key or label).strip().casefold()
        if lookup not in definitions:
            raise ValueError(f'undefined Markdown reference: {lookup}')
        links.append(definitions[lookup])
    links.extend(definitions.values())
    return links


def release_version(root):
    version = (Path(root) / 'VERSION').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', version):
        raise ValueError('VERSION must contain a plain MAJOR.MINOR.PATCH version')
    return version


def is_junction(path):
    # Path.is_junction() requires Python 3.12+; degrade to symlink-only
    # detection on older interpreters instead of crashing.
    check = getattr(path, 'is_junction', None)
    return bool(check and check())


def safe_file(root, relative):
    """Reject links/reparse junctions and paths outside the requested root."""
    root = Path(root).resolve()
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError(f'outside repository: {relative}')
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink() or is_junction(part):
            raise ValueError(f'linked path is not allowed: {relative}')
    if not path.is_file():
        raise ValueError(f'missing required file: {relative}')
    return path


def validate(root, mode='source'):
    if mode not in {'source', 'runtime'}:
        raise ValueError('mode must be source or runtime')
    root = Path(root).resolve()
    errors, counts, seen = [], {}, set()

    def require(condition, message):
        if not condition:
            errors.append(message)

    def read(relative):
        try:
            return safe_file(root, relative).read_text(encoding='utf-8')
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f'{relative}: {exc}')
            return None

    required = REQUIRED if mode == 'source' else RUNTIME_FILES
    for relative in required:
        require((root / relative).is_file(), f'missing required file: {relative}')

    if mode == 'source':
        try:
            safe_file(root, 'VERSION')
            version = release_version(root)
            changelog, readme = read('CHANGELOG.md'), read('README.md')
            headings = re.findall(r'^## v([0-9]+\.[0-9]+\.[0-9]+)', changelog or '', re.M)
            require(bool(headings) and headings[0] == version, 'VERSION and latest CHANGELOG entry disagree')
            require(f'Repository version: **v{version}**' in (readme or ''),
                    'VERSION and README version statement disagree')
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f'version: {exc}')
    else:
        for path in root.rglob('*'):
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or is_junction(path):
                errors.append(f'linked runtime path: {relative}')
            elif path.is_file() and relative not in RUNTIME_FILES:
                errors.append(f'non-runtime file: {relative}')
            elif path.is_dir() and relative not in {'agents', 'references'}:
                errors.append(f'non-runtime directory: {relative}')

    skill = read('SKILL.md')
    if skill is not None:
        try:
            lines = skill.splitlines()
            if not lines or lines[0] != '---' or '---' not in lines[1:]:
                raise ValueError('missing YAML frontmatter delimiters')
            end = lines.index('---', 1)
            meta = yaml_mapping('\n'.join(lines[1:end]))
            require(set(meta) == {'name', 'description'},
                    'SKILL.md: this package requires name/description-only frontmatter')
            name, desc = meta.get('name'), meta.get('description')
            require(isinstance(name, str) and bool(re.fullmatch(
                r'[a-z0-9]+(?:-[a-z0-9]+)*', name)) and len(name) <= 64,
                'SKILL.md: invalid name')
            require(name == 'adaptive-model-router', 'SKILL.md: unexpected skill name')
            require(isinstance(desc, str) and 0 < len(desc.strip()) <= 1024,
                    'SKILL.md: description must be a nonempty string up to 1024 characters')
            require(bool('\n'.join(lines[end + 1:]).strip()), 'SKILL.md: empty body')
        except ValueError as exc:
            errors.append(f'SKILL.md: {exc}')

    metadata = read('agents/openai.yaml')
    if metadata is not None:
        try:
            meta = yaml_mapping(metadata)
            require(set(meta) == {'interface', 'policy'}, 'openai.yaml: unexpected sections')
            interface, policy = meta.get('interface'), meta.get('policy')
            if not isinstance(interface, dict) or not isinstance(policy, dict):
                raise ValueError('interface and policy must be mappings')
            require(set(interface) == {'display_name', 'short_description', 'default_prompt'},
                    'openai.yaml: unexpected or missing interface fields')
            require(all(isinstance(v, str) and v.strip() for v in interface.values()),
                    'openai.yaml: interface values must be nonempty strings')
            short = interface.get('short_description')
            require(isinstance(short, str) and 25 <= len(short) <= 64,
                    'openai.yaml: short_description must contain 25–64 characters')
            prompt = interface.get('default_prompt')
            require(isinstance(prompt, str) and '$adaptive-model-router' in prompt,
                    'openai.yaml: repository policy requires default_prompt to mention $adaptive-model-router')
            require(policy == {'allow_implicit_invocation': True},
                    'openai.yaml: implicit invocation must remain enabled')
        except ValueError as exc:
            errors.append(f'openai.yaml: {exc}')

    for category in (('routing', 'delegation', 'escalation') if mode == 'source' else ()):
        relative = f'evals/{category}-cases.jsonl'
        content = read(relative)
        counts[category] = 0
        if content is None:
            continue
        for number, line in enumerate(content.splitlines(), 1):
            where = f'{relative}:{number}'
            if not line.strip():
                errors.append(f'{where}: blank JSONL record')
                continue
            try:
                case = parse_json(line)
                if not isinstance(case, dict):
                    raise ValueError('record must be an object')
                for key in ('id', 'task', 'rationale'):
                    if not isinstance(case.get(key), str) or not case[key].strip():
                        raise ValueError(f'{key} must be a nonempty string')
                if case['id'] in seen:
                    raise ValueError(f'duplicate case ID: {case["id"]}')
                seen.add(case['id'])
                if not isinstance(case.get('context'), dict) or not isinstance(case.get('expect'), dict):
                    raise ValueError('context and expect must be objects')
                expect = case['expect']
                bool_fields = ('delegation',) if category == 'delegation' else ('gpt6',)
                if category == 'routing':
                    bool_fields += ('delegation',)
                for key in bool_fields:
                    if type(expect.get(key)) is not bool:
                        raise ValueError(f'expect.{key} must be boolean')
                if category != 'delegation':
                    if expect.get('action') not in ACTIONS:
                        raise ValueError('invalid or missing expect.action')
                    if (expect['action'] == 'expert_dispatch') != expect['gpt6']:
                        raise ValueError('expert_dispatch and gpt6 expectation disagree')
                if category == 'routing':
                    if expect.get('tier_ceiling') not in TIERS or expect.get('context_strategy') not in CONTEXT:
                        raise ValueError('invalid routing tier_ceiling or context_strategy')
                    if expect['gpt6'] and expect['tier_ceiling'] != 'Astra':
                        raise ValueError('gpt6 requires Astra tier ceiling')
                elif category == 'delegation':
                    count = expect.get('max_agents')
                    if type(count) is not int or not 0 <= count <= 3:
                        raise ValueError('max_agents must be an integer from 0 to 3')
                    if expect.get('write_policy') not in {'none', 'read_only', 'isolated'}:
                        raise ValueError('invalid write_policy')
                    if expect['delegation'] != (count > 0):
                        raise ValueError('delegation and max_agents disagree')
                    if (expect['write_policy'] == 'none') == expect['delegation']:
                        raise ValueError('delegation and write_policy disagree')
                elif expect.get('validation_state') not in STATES:
                    raise ValueError('invalid validation_state')
                counts[category] += 1
            except (ValueError, TypeError) as exc:
                errors.append(f'{where}: {exc}')
        require(counts[category] > 0, f'{relative}: no valid cases')
    if mode == 'source':
        require(20 <= counts.get('routing', 0) <= 40, 'routing fixtures must contain 20–40 valid cases')

    for path in root.rglob('*.md'):
        if mode == 'source' and any(part in {'.git', 'dist', '__pycache__'}
                                    for part in path.relative_to(root).parts):
            continue
        relative = str(path.relative_to(root))
        text = read(relative)
        if text is None:
            continue
        try:
            for dest in local_links(text):
                parsed = urlsplit(dest.strip('<>'))
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = (path.parent / unquote(parsed.path)).resolve()
                require(target.is_relative_to(root) and target.exists(),
                        f'{relative}: missing or outside-repository local link: {dest}')
            for block in re.findall(r'^```json\s*\n(.*?)^```\s*$', text, re.M | re.S):
                parse_json(block)
        except ValueError as exc:
            errors.append(f'{relative}: {exc}')
    return errors, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--mode', choices=('source', 'runtime'), default='source')
    args = parser.parse_args()
    errors, counts = validate(args.root, args.mode)
    if errors:
        for error in errors:
            print(f'ERROR: {error}')
        print(f'FAIL: {len(errors)} issue(s)')
        return 1
    print(f'PASS ({args.mode}): structure, YAML subset, JSON examples, and local links')
    if counts:
        print(', '.join(f'{name}={count}' for name, count in counts.items()))
        print('Policy fixtures checked; no model-quality or cost benchmark executed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
