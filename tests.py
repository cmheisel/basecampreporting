import unittest
from project import Project

class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.username = "apitest"
        self.password = "apitest"
        self.url = "http://apitesting.basecamphq.com/"
        self.project_id = 2849305

        self.project = Project(self.url, self.project_id, self.username, self.password)

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
        
def main():
    unittest.main()

if __name__ == "__main__":
    main()
