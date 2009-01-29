import datetime

try:
    import cElementTree as ElementTree
except ImportError:
    from elementtree import ElementTree

from basecamp import Basecamp

class Project(object):
    '''Represents a project in Basecamp.'''

    def __init__(self, url, id, username, password):
        self.bc = Basecamp(url, username, password)
        self.id = id
        self.cache = {}

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
