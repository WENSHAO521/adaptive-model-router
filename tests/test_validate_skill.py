"""Negative-path checks use isolated copies; no network or model calls."""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validate_skill', ROOT / 'scripts/validate_skill.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in validator.REQUIRED:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)

    def edit(self, relative, transform):
        path = self.root / relative
        path.write_text(transform(path.read_text(encoding='utf-8')), encoding='utf-8')

    def reject(self, message):
        errors, _ = validator.validate(self.root)
        self.assertTrue(any(message in error for error in errors), errors)

    def change_case(self, category, mutate):
        def change(text):
            lines = text.splitlines()
            case = json.loads(lines[0])
            mutate(case)
            lines[0] = json.dumps(case)
            return '\n'.join(lines) + '\n'
        self.edit(f'evals/{category}-cases.jsonl', change)

    def test_clean_repository(self):
        errors, counts = validator.validate(self.root)
        self.assertEqual(errors, [])
        self.assertGreaterEqual(counts['routing'], 20)

    def test_missing_required_file(self):
        (self.root / 'references/paper-workflow.md').unlink()
        self.reject('missing required file')

    def test_missing_description(self):
        self.edit('SKILL.md', lambda text: '\n'.join(
            line for line in text.splitlines() if not line.startswith('description:')))
        self.reject('description must be')

    def test_broken_yaml_quote(self):
        self.edit('SKILL.md', lambda text: text.replace(
            'name: adaptive-model-router', 'name: "adaptive-model-router'))
        self.reject('SKILL.md:')

    def test_duplicate_yaml_key(self):
        self.edit('SKILL.md', lambda text: text.replace(
            'name: adaptive-model-router', 'name: adaptive-model-router\nname: other'))
        self.reject('duplicate YAML key')

    def test_trailing_space_null_description(self):
        self.edit('SKILL.md', lambda text: '\n'.join(
            'description: null ' if line.startswith('description:') else line
            for line in text.splitlines()))
        self.reject('unsupported YAML scalar')

    def test_trailing_space_boolean_description(self):
        self.edit('SKILL.md', lambda text: '\n'.join(
            'description: true ' if line.startswith('description:') else line
            for line in text.splitlines()))
        self.reject('description must be')

    def test_metadata_boolean_not_string(self):
        self.edit('agents/openai.yaml', lambda text: text.replace(
            'allow_implicit_invocation: true', 'allow_implicit_invocation: "true"'))
        self.reject('implicit invocation')

    def test_malformed_jsonl(self):
        self.edit('evals/routing-cases.jsonl', lambda text: '{broken}\n' + text)
        self.reject('evals/routing-cases.jsonl:1')

    def test_duplicate_id_across_files(self):
        self.change_case('delegation', lambda case: case.update(id='route-001'))
        self.reject('duplicate case ID')

    def test_missing_expect_field(self):
        self.change_case('routing', lambda case: case['expect'].pop('gpt6'))
        self.reject('expect.gpt6 must be boolean')

    def test_string_boolean_rejected(self):
        self.change_case('routing', lambda case: case['expect'].update(gpt6='false'))
        self.reject('expect.gpt6 must be boolean')

    def test_inconsistent_delegation(self):
        self.change_case('delegation', lambda case: case['expect'].update(max_agents=2))
        self.reject('delegation and max_agents disagree')

    def test_invalid_escalation_state(self):
        self.change_case('escalation', lambda case: case['expect'].update(validation_state='MAYBE'))
        self.reject('invalid validation_state')

    def test_missing_local_link(self):
        self.edit('README.md', lambda text: text + '\n[Missing](references/not-here.md)\n')
        self.reject('missing or outside-repository local link')

    def test_reference_style_link(self):
        self.edit('README.md', lambda text: text + '\n[Missing][ref]\n[ref]: absent.md\n')
        self.reject('missing or outside-repository local link')

    def test_inline_link_titles(self):
        for title in ('"Title"', "'Title'", '(Title)'):
            with self.subTest(title=title):
                (self.root / 'title-links.md').write_text(
                    f'[Missing](absent.md {title})\n', encoding='utf-8')
                self.reject('missing or outside-repository local link')

    def test_undefined_reference(self):
        self.edit('README.md', lambda text: text + '\n[Missing][no-definition]\n')
        self.reject('undefined Markdown reference')

    def test_fenced_example_not_a_link(self):
        self.edit('README.md', lambda text: text + '\n```text\n[Example](absent.md)\n```\n')
        self.assertEqual(validator.validate(self.root)[0], [])

    def test_invalid_json_example(self):
        self.edit('references/records.md', lambda text: text + '\n```json\n{"cost": NaN}\n```\n')
        self.reject('non-standard JSON constant')

    def test_failure_exit_code(self):
        (self.root / 'agents/openai.yaml').unlink()
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/validate_skill.py'), '--root', str(self.root)],
            capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 1)
        self.assertIn('FAIL:', result.stdout)


if __name__ == '__main__':
    unittest.main()
