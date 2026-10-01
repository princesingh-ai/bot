import unittest
import pandas as pd
from server.core.loaders import (
    load_problem_statements,
    load_innovation_process,
    load_crieya_preincubation_hub,
    load_crieya_focus,
    load_trl_levels,
)

class TestDataLoaders(unittest.TestCase):

    def test_load_problem_statements(self):
        df = load_problem_statements()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty, "Problem statements DataFrame should not be empty")
        self.assertIn("problem_id", df.columns)
        self.assertIn("title", df.columns)

    def test_load_innovation_process(self):
        df = load_innovation_process()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty, "Innovation process DataFrame should not be empty")
        self.assertIn("process_no", df.columns)

    def test_load_text_documents(self):
        hub = load_crieya_preincubation_hub()
        self.assertIsInstance(hub, str)
        self.assertGreater(len(hub.strip()), 0)

        focus = load_crieya_focus()
        self.assertIsInstance(focus, str)
        self.assertGreater(len(focus.strip()), 0)

        trl = load_trl_levels()
        self.assertIsInstance(trl, str)
        self.assertGreater(len(trl.strip()), 0)


if __name__ == "__main__":
    unittest.main()
