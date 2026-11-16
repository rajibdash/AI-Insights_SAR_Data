import contextlib
import csv
import io
import json
import math
import tempfile
import unittest
from pathlib import Path

import sar_flood


class FloodScreeningTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        self.model = self.path / "model.json"
        self.model.write_text(json.dumps({
            "bias": -4,
            "weights": {"before_db": 0, "after_db": -0.2, "delta_db": -0.3},
        }))
        self.observations = self.path / "observations.csv"

    def run_cli(self, text, *args):
        self.observations.write_text(text)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            sar_flood.main([str(self.observations), "--model", str(self.model), *args])
        return list(csv.DictReader(io.StringIO(output.getvalue())))

    def test_scoring_and_threshold(self):
        rows = self.run_cli(
            "pixel_id,latitude,longitude,before_db,after_db\n"
            "a,29,-90,-10,-20\nb,29,-90,-10,-10\n",
            "--threshold", "0.5",
        )
        self.assertAlmostEqual(float(rows[0]["flood_probability"]), 1 / (1 + math.exp(-3)), places=6)
        self.assertEqual([row["flagged"] for row in rows], ["1", "0"])

    def test_extreme_scores_are_stable(self):
        weights = {"before_db": 0, "after_db": 1, "delta_db": 0}
        self.assertEqual(sar_flood.score(0, 1000, 0, weights), 1)
        self.assertEqual(sar_flood.score(0, -1000, 0, weights), 0)

    def test_invalid_input_fails_without_partial_output(self):
        text = ("pixel_id,latitude,longitude,before_db,after_db\n"
                "a,29,-90,-10,-20\nb,91,-90,nan,-10\n")
        output, error = io.StringIO(), io.StringIO()
        self.observations.write_text(text)
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit) as exc:
                sar_flood.main([str(self.observations), "--model", str(self.model)])
        self.assertEqual(exc.exception.code, 2)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("CSV row 3", error.getvalue())

    def test_invalid_model_and_threshold(self):
        self.model.write_text('{"bias": 0, "weights": {"after_db": 1}}')
        with self.assertRaisesRegex(ValueError, "weights must contain exactly"):
            sar_flood.load_model(self.model)
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                sar_flood.main([str(self.observations), "--model", str(self.model), "--threshold", "nan"])

    def test_rejects_missing_columns_and_unsafe_ids(self):
        for text in (
            "pixel_id,latitude,longitude,before_db\na,29,-90,-10\n",
            "pixel_id,latitude,longitude,before_db,after_db\n=cmd,29,-90,-10,-20\n",
        ):
            with self.subTest(text=text), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    self.run_cli(text)


if __name__ == "__main__":
    unittest.main()
