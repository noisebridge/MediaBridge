The project requires that at least one Reviewer approves what
each Author proposes to merge down to `main`.

During
[PR](https://en.wikipedia.org/wiki/Distributed_version_control#Pull_requests)
code review we ask two questions about the proposed code:

1. Is it correct?
2. Is it maintainable?

If we can identify an input which produces incorrect results,
or if a linter can, then the code is not yet ready to merge down,
and reviews should describe a specific requested code change.

If team members will have trouble with shared code maintenance,
then it is appropriate to insist on revised docstrings or
even a revised Public API prior to merging to `main`.
Adding automated
[unit tests](https://docs.python.org/3/library/unittest.html#unittest.TestCase)
can go a long way toward explaining to colleagues how
a library routine ought to be called.
Maintenance tasks include fixing buggy code,
and adding new features to existing code.
