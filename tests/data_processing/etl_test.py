import unittest
from pathlib import Path

import pandas as pd

from mediabridge.data_processing.etl import run_sqlite_child


class EtlTest(unittest.TestCase):
    def test_run_sqlite_child(self) -> None:
        run_sqlite_child(
            [
                "DROP TABLE  IF EXISTS  temp_table;",
                "CREATE TABLE temp_table AS SELECT 123 AS num, 'abc' AS alpha;",
                "DROP TABLE temp_table;",
            ]
        )

    def test_sqlite_dot_import(self) -> None:
        foo = pd.DataFrame([{"num": 123, "alpha": "abc"}])
        csv = Path("/tmp/foo.csv")
        foo.to_csv(csv, index=False)
        run_sqlite_child(
            [
                "DROP TABLE  IF EXISTS  foo;",
                ".mode csv",
                ".headers off",
                f".import {csv} foo",
            ]
        )
        csv.unlink()
