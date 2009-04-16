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

    def assertDict(self, o, expected):
        for key, value in expected.items():
            msg = "Key %s doesn't match.\nExpected:\n%s\n\nActual:\n%s" % (key, pprint.pformat(value), pprint.pformat(o.to_dict()[key]))
            self.assertEqual(value, o.to_dict()[key], msg)
        #msg = "Unequal data structures!\nExpected:\n%s\n\nActual:\n%s" % (pprint.pformat(expected), pprint.pformat(o.to_dict()))
        #self.assertEqual(expected, o.to_dict(), msg)


    def assertSerialization(self, o, expected):
        as_json = o.to_json()
        from_json = json.loads(as_json)

        for key, value in expected.items():
            msg = "Key %s doesn't match.\nExpected:\n%s\n\nActual:\n%s" % (key, pprint.pformat(value), pprint.pformat(from_json[key]))
            self.assertEqual(value, from_json[key], msg)

class SerializationTests(SerializationTestHelper):
    def test_message(self):
        m = self.project.messages[0]
        expected = {
            u"category": {u"type": u"PostCategory", u"id": 28605393, u"name": u"Assets"},
            u"attachments_count": 0,
            u"id": 19364228,
            u"posted_on": u'2009-01-28T14:30:18',
            u"title": u"This is the newest message"
        }
        self.assertSerialization(m, expected)

        expected[u'posted_on'] = datetime.datetime(2009, 1, 28, 14, 30, 18)
        self.assertDict(m, expected)

    def test_comment(self):
        c = self.project.comments[0]
        expected = {u'attachments_count': 0,
                    u'author_id': 3396975,
                    u'body': u'This is the latest comment',
                    u'emailed_from': None,
                    u'id': 29503849,
                    u'post_id': 19364228,
                    u'posted_on': u'2009-01-28T21:37:02'}
        self.assertSerialization(c, expected)

        expected[u'posted_on'] = datetime.datetime(2009, 1, 28, 21, 37, 2)
        self.assertDict(c, expected)

    def test_milestone(self):
        m = self.project.milestones[0]
        expected = {u'completed': False,
                    u'created_on': u'2009-01-29T21:55:43',
                    u'creator_id': 3396975,
                    u'deadline': u'2011-12-31T00:00:00',
                    u'id': 8710156,
                    u'project_id': 2849305,
                    u'responsible_party_id': 3396975,
                    u'responsible_party_type': u'Person',
                    u'title': u'Future Milestone 3',
                    u'wants_notification': False,
                    u'is_previous': False,
                    u'is_upcoming': True,
                    u'is_late': False}
        self.assertSerialization(m, expected)

        expected[u'created_on'] = datetime.datetime(2009, 1, 29, 21, 55, 43)
        expected[u'deadline'] = datetime.date(2011, 12, 31)
        self.assertDict(m, expected)

    def test_todolist(self):
        t = self.project.todo_lists[self.project.todo_lists.keys()[0]]
        expected = {u'complete': u'false',
                    u'completed_count': 0,
                    u'description': u'Bugs and errors that need to be fixed',
                    u'id': 5390843,
                    u'milestone_id': None,
                    u'name': u'Defect backlog',
                    u'position': 3,
                    u'private': False,
                    u'project_id': 2849305,
                    u'tracked': False,
                    u'uncompleted_count': 2,
                    u'is_complete': False,
                    u'is_sprint': False,
                    u'is_backlog': True}
        self.assertSerialization(t, expected)
        self.assertDict(t, expected)
            
    def test_project(self):
        p = self.project
        expected = self.generate_expected_project()
        self.assertSerialization(p, expected)

    def test_project_dict(self):
        p = self.project
        expected = self.generate_expected_project_dict()
        self.assertDict(p, expected)

    def generate_expected_project_dict(self):
        expected = {
            u'name': self.project.name,
            u'status': self.project.status,
            u'last_changed_on': datetime.datetime(2009, 2, 3, 15, 3, 14),
            u'messages': [ m.to_dict() for m in self.project.messages ],
            u'comments': [ c.to_dict() for c in self.project.comments ],
            u'milestones': [ m.to_dict() for m in self.project.milestones ],
            u'late_milestones': [ m.to_dict() for m in self.project.late_milestones ],
            u'previous_milestones': [ m.to_dict() for m in self.project.previous_milestones ],
            u'backlogged_count': self.project.backlogged_count,
            u'sprints': [ s.to_dict() for s in self.project.sprints ],
            u'current_sprint': json.loads(self.project.current_sprint.to_json()),
            u'upcoming_sprints': [ s.to_dict() for s in self.project.upcoming_sprints ],
        }

        todo_list_keys = self.project.todo_lists.keys()
        expected[u'todo_lists'] = {}
        for k in todo_list_keys:
            expected[u'todo_lists'][k] = self.project.todo_lists[k].to_dict()
        
        backlog_keys = self.project.backlogs.keys()
        expected[u'backlogs'] = {}
        for k in backlog_keys:
            expected[u'backlogs'][k] = self.project.backlogs[k].to_dict()

        return expected

    def generate_expected_project(self):
        expected = {
            u'name': self.project.name,
            u'status': self.project.status,
            u'last_changed_on': '2009-02-03T15:03:14',
            u'messages': [ json.loads(m.to_json()) for m in self.project.messages ],
            u'comments': [ json.loads(c.to_json()) for c in self.project.comments ],
            u'milestones': [ json.loads(m.to_json()) for m in self.project.milestones ],
            u'late_milestones': [ json.loads(m.to_json()) for m in self.project.late_milestones ],
            u'previous_milestones': [ json.loads(m.to_json()) for m in self.project.previous_milestones ],
            u'backlogged_count': self.project.backlogged_count,
            u'sprints': [ json.loads(s.to_json()) for s in self.project.sprints ],
            u'current_sprint': json.loads(self.project.current_sprint.to_json()),
            u'upcoming_sprints': [ json.loads(s.to_json()) for s in self.project.upcoming_sprints ],
        }

        todo_list_keys = self.project.todo_lists.keys()
        todo_list_keys.sort()

        expected[u'todo_lists'] = {}
        for k in todo_list_keys:
            expected[u'todo_lists'][k] = json.loads(self.project.todo_lists[k].to_json())
        
        backlog_keys = self.project.backlogs.keys()
        backlog_keys.sort()

        expected[u'backlogs'] = {}
        for k in backlog_keys:
            expected[u'backlogs'][k] = json.loads(self.project.backlogs[k].to_json())

        return expected

def test_suite():
    return unittest.makeSuite(SerializationTests)

if __name__ == "__main__":
    import unittest
    unittest.main()
