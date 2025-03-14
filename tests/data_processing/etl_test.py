import unittest
from pathlib import Path

import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from mediabridge.data_processing.etl import run_sqlite_child
from mediabridge.db.tables import create_tables, get_engine


class EtlTest(unittest.TestCase):

    def test_sqlite_dot_import(self) -> None:
        df = pd.DataFrame([{"num": 123, "alpha": "abc"}])
        csv = Path("/tmp/foo.csv")
        df.to_csv(csv, index=False)
        create_tables()
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

        # https://sqlite.org/cli.html
        # 7.5. Importing files as CSV or other formats
        # When .import is run, its treatment of the first input row depends upon
        # whether the target table already exists. If it does not exist, the table
        # is automatically created and the content of the first input row is used
        # to set the name of all the columns in the table. In this case, the table
        # data content is taken from the second and subsequent input rows. If the
        # target table already exists, every row of the input, including the
        # first, is taken to be actual data content. If the input file contains an
        # initial row of column labels, you can make the .import command skip that
        # initial row using the "--skip 1" option.
