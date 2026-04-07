"""Coverage parsing module for lcov/gcov files"""

from .lcov_reader import LcovReader, parse_lcov_and_merge

__all__ = ["LcovReader", "parse_lcov_and_merge"]
