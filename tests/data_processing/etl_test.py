import unittest
from pathlib import Path

import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from mediabridge.data_processing.etl import run_sqlite_child
from mediabridge.db.tables import get_engine


class EtlTest(unittest.TestCase):

    def test_sqlite_dot_import(self) -> None:
        df = pd.DataFrame([{"num": 123, "alpha": "abc"}])
        csv = Path("/tmp/foo.csv")
        df.to_csv(csv, index=False)
        run_sqlite_child(
            [
                "DROP TABLE  IF EXISTS  foo;",
                ".mode csv",
                f".import {csv} foo",
            ]
        )
        Base = automap_base()
        Base.prepare(autoload_with=get_engine())
        Foo = Base.metadata.tables["foo"]

        with Session(get_engine()) as sess:
            self.assertListEqual(
                [
                    ("123", "abc"),
                ],
                list(sess.query(Foo).all()),
            )
            run_sqlite_child(
                [
                    "DELETE FROM foo;",  # NB: no DROP, this time
                    ".mode csv",
                    f".import {csv} foo",
                ]
            )
            self.assertListEqual(  # Now the .import behavior is to INSERT header as data                [
                [
                    ("num", "alpha"),
                    ("123", "abc"),
                ],
                list(sess.query(Foo).all()),
            )
        csv.unlink()
