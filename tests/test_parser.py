import datetime
import unittest
import os
import pprint

from basecampreporting.parser import parse_basecamp_xml

class ParserTests(unittest.TestCase):
    def setUp(self):
        self.parse = parse_basecamp_xml
    
    def tearDown(self):
        pass

    def assertEqual(self, expected, actual):
        msg = "\n%s != \n%s" % (pprint.pformat(expected), pprint.pformat(actual))
        super(ParserTests, self).assertEqual(expected, actual, msg)

    def fixture(self, path):
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, ".", path)
        return unicode(file(file_path, 'r').read())

    def test_project(self):
        expected = {
            u'created_on': datetime.date(year=2009, month=1, day=28),
            u'id': 2849305,
            u'last_changed_on': datetime.datetime(year=2009, month=2, day=3, hour=15, minute=3, second=14),
            u'name': u"API Testing Project",
            u'status': u'active',
            u'company': {
                u'id': 1250808,
                u'name': u"Testing",
            }
        }
        actual = self.parse(self.fixture('fixtures/project.xml'))

        self.assertEqual(expected, actual)

    def test_
        
if __name__ == "__main__":
    unittest.main()
