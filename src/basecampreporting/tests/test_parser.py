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
        for key, value in expected.items():
            msg = "\n%s != \n%s" % (pprint.pformat(expected[key]), pprint.pformat(actual[key]))            
            super(ParserTests, self).assertEqual(expected[key], actual[key], msg)

    def fixture(self, path):
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, ".", "fixtures", path)
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
        actual = self.parse(self.fixture('project.xml'))

        self.assertEqual(expected, actual)

    def test_post(self):
        expected = {
            u'attachments_count': 0,
            u'author_id': 3396975,
            u'body': u'This is the newest message',
            u'category_id': 28605393,
            u'comments_count': 4,
            u'display_body': u'<p>This is the newest message</p>',
            u'display_extended_body': None,
            u'extended_body': None,
            u'id': 19364228,
            u'milestone_id': 0,
            u'posted_on': datetime.datetime(year=2009, month=1, day=28, hour=14, minute=30, second=18),
            u'private': False,
            u'project_id': 2849305,
            u'title': u'This is the newest message',
            u'use_textile': True }
        actual = self.parse(self.fixture('message.xml'))
        self.assertEqual(expected, actual)
            
def test_suite():
    return unittest.makeSuite(ParserTests)
        
if __name__ == "__main__":
    unittest.main()
