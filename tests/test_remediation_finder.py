import json
import tempfile
import unittest
from pathlib import Path

from remediation_search.remediation_finder import build_response, find_remediation, load_chunks, tokenize


class RemediationFinderTests(unittest.TestCase):
    def test_tokenize_normalizes_and_filters_short_tokens(self):
        tokens = tokenize("Pod pending in AKS, with CPU pressure")

        self.assertIn("pod", tokens)
        self.assertIn("pending", tokens)
        self.assertIn("aks", tokens)
        self.assertNotIn("in", tokens)

    def test_load_chunks_and_find_relevant_chunks(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            chunks_dir = Path(tmp_dir) / "processed_chunks"
            chunks_dir.mkdir()

            first = {
                "chunk_id": 0,
                "content": "Pod pending state can be caused by insufficient CPU.",
                "metadata": {"source": "runbook-a.md", "file_type": ".md"},
            }
            second = {
                "chunk_id": 1,
                "content": "This section describes unrelated networking topics.",
                "metadata": {"source": "runbook-b.md", "file_type": ".md"},
            }

            (chunks_dir / "chunk_000.json").write_text(json.dumps(first), encoding="utf-8")
            (chunks_dir / "chunk_001.json").write_text(json.dumps(second), encoding="utf-8")

            documents = load_chunks(chunks_dir)
            matches = find_remediation("Pod Pending State", documents, limit=2)

            self.assertEqual(2, len(documents))
            self.assertTrue(matches)
            self.assertEqual(0, matches[0]["chunk_id"])

    def test_build_response_for_no_matches(self):
        response = build_response("Pod Pending State", [])

        self.assertIn("Root Cause: Pod Pending State", response)
        self.assertIn("No matching remediation steps", response)


if __name__ == "__main__":
    unittest.main()

