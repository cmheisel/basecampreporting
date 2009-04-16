import os
import pprint
import unittest

from basecampreporting.etree import ET
from basecampreporting.mocks import TestProject

class ProjectTests(unittest.TestCase):
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

    def tearDown(self):
        self.project.bc.save_test_fixtures(self.fixtures_path)
        
    def test_latest_message(self):
        self.assertEqual("This is the newest message",
                         self.project.messages[0].title)

    def test_latest_comment(self):
        self.assertEqual("This is the latest comment",
                         self.project.comments[0].body)

    def test_late_milestones(self):
        self.assertEqual(3, len(self.project.late_milestones))

    def test_upcoming_milestones(self):
        self.assertEqual(3, len(self.project.upcoming_milestones))

    def test_previous_milestones(self):
        self.assertEqual(6, len(self.project.previous_milestones))

    def test_backlogs(self):
        self.assertEqual(2, len(self.project.backlogs))

        self.assertEqual(3, self.project.backlogs['Product backlog'].uncompleted_count)
        self.assertEqual(2, self.project.backlogs['Defect backlog'].uncompleted_count)
        self.assertEqual(5, self.project.backlogged_count)

    def test_sprints(self):
        expected = [0, 1, 2]
        actual = [sprint.sprint_number for sprint in self.project.sprints]
        self.assertEqual(expected, actual)
        
        self.assertEqual(1, self.project.current_sprint.sprint_number)
        self.assertEqual("Sprint 1", self.project.current_sprint.name)
        self.assertEqual(1, len(self.project.upcoming_sprints))

    def test_project_title(self):
        self.assertEqual("API Testing Project", self.project.name)

def test_suite():
    return unittest.makeSuite(ProjectTests)
        
def main():
    unittest.main()

if __name__ == "__main__":
    main()
