import unittest

from test_project import ProjectTests
from test_parser import ParserTests
from test_serialization import SerializationTests

def test_suite():
    alltests = unittest.TestSuite((ProjectTests, ParserTests, SerializationTests))

if __name__ == "__main__":
    import os
    print __file__
