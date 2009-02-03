import datetime
import re

try:
    import cElementTree as ElementTree
except ImportError:
    from elementtree import ElementTree

from basecamp import Basecamp
from pyactiveresource import activeresource

class Project(object):
    '''Represents a project in Basecamp.'''

    def __init__(self, url, id, username, password):
        self.bc = Basecamp(url, username, password)
        self.id = id
        self.cache = {}
        self._get_project_info()

    def _get_project_info(self):
        project_xml = self.bc._request("/projects/%s.xml" % self.id)
        node = ElementTree.fromstring(project_xml)
        self.name = node.findtext("name")
        self.status = node.findtext("status")
        self._last_changed_on = node.findtext("last-changed-on")

    @property
    def last_changed_on(self):
        year = int(self._last_changed_on[0:4])
        month = int(self._last_changed_on[5:7])
        day = int(self._last_changed_on[8:10])
        hour = int(self._last_changed_on[11:13])
        minute = int(self._last_changed_on[14:16])
        second = int(self._last_changed_on[17:19])

        return datetime.datetime(year=year, month=month, day=day,
                                 hour=hour, minute=minute, second=second)


    @property
    def messages(self):
        self.cache['messages'] = []
        message_xml = self.bc.message_archive(self.id)

        for post in ElementTree.fromstring(message_xml).findall("post"):
            self.cache['messages'].append(Message(post))
        return self.cache['messages']        

    @property
    def comments(self):
        '''Looks through the last 3 messages and finds the latest comment.'''
        comments = []
        for message in self.messages[0:3]:
            comment_xml = self.bc.comments(message.id)
            for comment_node in ElementTree.fromstring(comment_xml).findall("comment"):
                comments.append(Comment(comment_node))
        comments.sort()
        comments.reverse()
        return comments

    @property
    def milestones(self):
        '''Array of all milestones'''
        milestone_xml = self.bc.list_milestones(self.id)
        milestones = []
        for node in ElementTree.fromstring(milestone_xml).findall("milestone"):
            milestones.append(Milestone(node))

        milestones.sort()
        milestones.reverse()
        return milestones

    @property
    def late_milestones(self):
        '''Array of all late milestones'''
        return [m for m in self.milestones if m.is_late]

    @property
    def upcoming_milestones(self):
        return [m for m in self.milestones if m.is_upcoming]

    @property
    def previous_milestones(self):
        return [m for m in self.milestones if m.is_previous]

    @property
    def todo_lists(self):
        todo_lists_xml = self.bc.todo_lists(self.id)
        todo_lists = {}
        for node in ElementTree.fromstring(todo_lists_xml).findall("todo-list"):
            the_list = ToDoList(node)
            todo_lists[the_list.name] = the_list
        return todo_lists

    @property
    def backlogs(self):
        backlogs = {}
        lists = [tdlist for tdlist in self.todo_lists.values() if tdlist.is_backlog]
        for alist in lists:
            backlogs[alist.name] = alist
            
        return backlogs

    @property
    def backlogged_count(self):
        backlogged = 0
        for alist in self.backlogs.values(): backlogged += alist.uncompleted_count
        return backlogged

    @property
    def sprint_list_current(self):
        unfinished_sprints = [tdlist for tdlist in self.todo_lists.values() if tdlist.is_sprint and tdlist.uncompleted_count != 0 ]
        unfinished_sprints.sort()
        try:
            return unfinished_sprints[0]
        except IndexError:
            return None

class ToDoList(object):
    '''Represents a ToDo list in Basecamp'''
    def __init__(self, node):
        self.id = int(node.findtext("id"))
        self.name = node.findtext("name")
        self.project_id = int(node.findtext("project-id"))
        self._complete = node.findtext("complete")
        self.completed_count = int(node.findtext("completed-count"))
        self.uncompleted_count = int(node.findtext("uncompleted-count"))

    @property
    def is_complete(self):
        if self._complete.lower() in ['true', 'yes', 'y', 't', 1]: return True
        return False

    @property
    def is_sprint(self):
        if 'sprint' in self.name.lower(): return True
        return False

    @property
    def is_backlog(self):
        if 'backlog' in self.name.lower(): return True
        return False

    sprint_number_pattern = re.compile('(Sprint|sprint) (?P<sprint_number>[\d+])')
    @property
    def sprint_number(self):
        result = self.sprint_number_pattern.search(self.name)
        return int(result.group('sprint_number'))

    def cmp(self, other):
        if self.is_sprint and other.is_sprint:
            return cmp(self.sprint_number, other.sprint_number)
        return cmp(self.name, other.name)

class Milestone(object):
    '''Represents a milestone in Basecamp'''
    def __init__(self, node):
        self.id = int(node.findtext("id"))
        self.title = node.findtext("title")
        self._deadline = node.findtext("deadline")
        self._completed = node.findtext("completed")

    def __cmp__(self, other):
        return cmp(self.deadline, other.deadline)

    @property
    def is_previous(self):
        if self.deadline < datetime.date.today(): return True

    @property
    def is_upcoming(self):
        if self.deadline >= datetime.date.today(): return True

    @property
    def is_late(self):
        if self.completed: return False
        if self.deadline < datetime.date.today(): return True

    @property
    def completed(self):
        if self._completed.lower() in ["true", "1", "yes"]:
            return True
        return False

    @property
    def deadline(self):
        year = int(self._deadline[0:4])
        month = int(self._deadline[5:7])
        day = int(self._deadline[8:10])

        return datetime.date(year=year, month=month, day=day)

class Comment(object):
    '''Represents a comment on a message in Basecamp'''
    def __init__(self, node):
        self.id = int(node.findtext("id"))
        self.body = node.findtext("body")
        self._posted_on = node.findtext("posted-on")
        self.author_id = id(node.findtext("author-id"))

    @property
    def posted_on(self):
        year = int(self._posted_on[0:4])
        month = int(self._posted_on[5:7])
        day = int(self._posted_on[8:10])
        hour = int(self._posted_on[11:13])
        minute = int(self._posted_on[14:16])
        second = int(self._posted_on[17:19])

        return datetime.datetime(year=year, month=month, day=day,
                                 hour=hour, minute=minute, second=second)

    def __cmp__(self, other):
        value = cmp(self.posted_on, other.posted_on)
        return value

class Message(object):
    '''Represents a Message in Basecamp'''
    def __init__(self, message_element):
        self.id = int(message_element.findtext("id"))
        self.title = message_element.findtext("title")
        self.posted_on = message_element.findtext("posted-on")

if __name__ == "__main__":
    from tests import *
    main()
