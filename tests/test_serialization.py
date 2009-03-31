import os
import pprint
import unittest
import datetime

from basecampreporting.serialization import json, BasecampObjectEncoder
from basecampreporting.mocks import TestProject

class SerializationTestHelper(unittest.TestCase):
    def setUp(self):
        self.username = "FAKE"
        self.password = "FAKE"
        self.url = "http://FAKE.basecamphq.com/"
        self.project_id = 2849305

        base_path = os.path.dirname(os.path.abspath(__file__))
        self.fixtures_path = os.path.join(base_path, ".", "fixtures", "project.recorded.json")


        self.project = TestProject(self.url, self.project_id,
                               self.username, self.password, self.fixtures_path)

        self.project.bc.load_test_fixtures(self.fixtures_path)

class MessageSerializationTests(SerializationTestHelper):
    def test_serialization(self):
        m = self.project.messages[0]
        as_json = m.to_json()

        from_json = json.loads(as_json)
        expected = {
            "category": {"type": "PostCategory", "id": 28605393, "name": "Assets"},
            "attachments_count": 0,
            "id": 19364228,
            "posted_on": '2009-01-28T14:30:18',
            "title": "This is the newest message"
        }

        self.assertEqual(expected, from_json)

if __name__ == "__main__":
    import unittest
    unittest.main()
