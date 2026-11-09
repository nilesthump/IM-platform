"""The published event schema must reject exactly what the recorder never produces.

The schema is the machine-verifiable authority for externally read events.jsonl
artifacts (research/README.md), so it must be at least as strict as the only
producer: tools/research/recorder.py. These checks are standard-library only.
"""
import importlib.util
import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
EVENT_SCHEMA = ROOT / "research/schema/event.schema.json"


def load_recorder():
    spec = importlib.util.spec_from_file_location(
        "recorder_schema_authority", ROOT / "tools/research/recorder.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EventSchemaAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(EVENT_SCHEMA.read_text(encoding="utf-8"))
        self.recorder = load_recorder()

    def test_events_must_be_objects(self):
        # required/properties/additionalProperties only constrain objects; without
        # an explicit "type" a scalar or null line validates as a well-formed event.
        self.assertEqual("object", self.schema.get("type"))

    def test_event_type_vocabulary_matches_recorder(self):
        enum = self.schema["properties"]["event_type"]["enum"]
        self.assertEqual(sorted(self.recorder.EVENT_TYPES), sorted(enum))

    def test_run_id_pattern_matches_recorder_fullmatch_exactly(self):
        # JSON Schema "pattern" is a search; the published form must accept exactly
        # the run ids the recorder's own fullmatch accepts, in both directions.
        pattern = self.schema["properties"]["run_id"]["pattern"]
        valid = ["R-NONMAINLINE-SCHEMA-R1", "R-a.b:c_d-e", "R-x"]
        invalid = ["R-", "R-a/b", "R-x\ninjected", "XR-1", "R-x y", "R-x/y/z"]
        for value in valid:
            self.assertEqual(value, self.recorder.validated_run_id(value))
            self.assertIsNotNone(re.search(pattern, value), value)
        for value in invalid:
            with self.assertRaises(self.recorder.RecorderError):
                self.recorder.validated_run_id(value)
            self.assertIsNone(re.search(pattern, value), value)


if __name__ == "__main__":
    unittest.main()
