# The MIT License
#
# Copyright (c) 2006 Jochen Kupperschmidt <webmaster@nwsnet.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
This module provides an (almost) complete wrapper around the Basecamp API
(http://www.basecamphq.com/api/). It is written in Python and based upon the
excellent ElementTree package (http://effbot.org/zone/element-index.htm).
Requests will be made as XML, not YAML. Responses will be XML, too.

Make sure to allow access to the API (Dashboard > Account > Basecamp API) for
your projects.

Usage:

    # Import ElementTree and the Basecamp wrapper module.
    import elementtree.ElementTree as ET
    from basecamp import Basecamp

    # Prepare the interaction with Basecamp.
    bc = Basecamp('http://yourBasecamp.projectpath.com/', username, password)

    # Fetch the to-do lists of a project.
    todolists = bc.todo_lists(yourProjectID)

    # Let's use the ElementTree API to access data via path expressions:
    for name in ET.fromstring(todolists).findall('todo-list/name'):
        print name.text

    # See the ElementTree website for more information on how to use it.
"""

__author__ = 'Jochen Kupperschmidt <webmaster@nwsnet.de>'
__version__ = '0.1'
__date__ = '2006-05-21'


import base64
import urllib2

from basecampreporting.etree import ET


class Basecamp(object):

    def __init__(self, baseURL, username, password):
        self.baseURL = baseURL
        if self.baseURL[-1] == '/':
            self.baseURL = self.baseURL[:-1]

        self.opener = urllib2.build_opener()

        self.auth_string = '%s:%s' % (username, password)
        self.encoded_auth_string = base64.encodestring(self.auth_string)

        #Python 2.5, at least on Ubuntu is adding a newline when encoding,
        #which Basecamp chokes on and returns an HTTP 400
        self.encoded_auth_string = self.encoded_auth_string.replace('\n', '')
        self.headers = [
            ('Content-Type', 'application/xml'),
            ('Accept', 'application/xml'),
            ('Authorization', 'Basic %s' % self.encoded_auth_string), ]
        self.opener.addheaders = self.headers

    def _request(self, path, data=None):
        if hasattr(data, 'findall'):
            data = ET.tostring(data)
        req = urllib2.Request(url=self.baseURL + path, data=data)
        return self.opener.open(req).read()

    # ---------------------------------------------------------------- #
    # General

    def company(self, company_id):
        """
        This will return the information for the referenced company.
        """
        path = '/contacts/company/%u' % company_id
        return self._request(path)

    def file_categories(self, project_id):
        """
        This will return an alphabetical list of all file categories in the
        referenced project.
        """
        path = '/projects/%u/attachment_categories' % project_id
        return self._request(path)

    def message_categories(self, project_id):
        """
        This will return an alphabetical list of all message categories in the
        referenced project.
        """
        path = '/projects/%u/post_categories' % project_id
        return self._request(path)

    def people(self, company_id):
        """
        This will return all of the people in the given company. If a project
        id is given, it will be used to filter the set of people that are
        returned to include only those that can access the given project.
        """
        path = '/contacts/people/%u' % company_id
        return self._request(path)

    def people_per_project(self, project_id, company_id):
        """
        This will return all of the people in the given company that can
        access the given project.
        """
        path = '/projects/%u/contacts/people/%u' % (project_id, company_id)
        return self._request(path)

    def person(self, person_id):
        """
        This will return information about the referenced person.
        """
        path = '/contacts/person/%u' % person_id
        return self._request(path)

    def projects(self):
        """
        This will return a list of all active, on-hold, and archived projects
        that you have access to. The list is not ordered.
        """
        path = '/project/list'
        return self._request(path)

    # ---------------------------------------------------------------- #
    # Messages and Comments

    # Messages

    def message(self, message_ids):
        """
        This will return information about the referenced message. If the id
        is given as a comma-delimited list, one record will be returned for
        each id. In this way you can query a set of messages in a single
        request. Note that you can only give up to 25 ids per request--more
        than that will return an error.
        """
        if isinstance(message_ids, list):
            message_ids = ','.join([int(id) for id in message_ids])
        path = '/msg/get/%s' % message_ids
        return self._request(path)

    def message_archive(self, project_id, category_id=None):
        """
        This will return a summary record for each message in a project. If
        you specify a category_id, only messages in that category will be
        returned. (Note that a summary record includes only a few bits of
        information about a post, not the complete record.)
        """
        path = '/projects/%u/msg/archive' % project_id
        req = ET.Element('request')
        ET.SubElement(req, 'project-id').text = str(int(project_id))
        if category_id is not None:
            ET.SubElement(req, 'category-id').text = str(int(category_id))
        return self._request(path, req)

    def message_archive_per_category(self, project_id, category_id):
        """
        This will return a summary record for each message in a particular
        category. (Note that a summary record includes only a few bits of
        information about a post, not the complete record.)
        """
        path = '/projects/%u/msg/cat/%u/archive' % (project_id, category_id)
        return self._request(path)

    def _create_message_post_elem(self, category_id, title, body,
        extended_body, use_textile=False, private=False):
        post = ET.Element('post')
        ET.SubElement(post, 'category-id').text = str(int(category_id))
        ET.SubElement(post, 'title').text = str(title)
        ET.SubElement(post, 'body').text = str(body)
        ET.SubElement(post, 'extended-body').text = str(extended_body)
        if bool(use_textile):
            ET.SubElement(post, 'use-textile').text = '1'
        if bool(private):
            ET.SubElement(post, 'private').text = '1'
        return post

    def create_message(self, project_id, category_id, title, body,
        extended_body, use_textile=False, private=False, notify=None,
        attachments=None):
        """
        Creates a new message, optionally sending notifications to a selected
        list of people. Note that you can also upload files using this
        function, but you need to upload the files first and then attach them.
        See the description at the top of this document for more information.
        """
        path = '/projects/%u/msg/create' % project_id
        req = ET.Element('request')
        req.append(self._create_message_post_elem(category_id, title, body,
            extended_body, use_textile=False, private=False))
        if notify is not None:
            for person_id in notify:
                ET.SubElement(req, 'notify').text = str(int(person_id))
        # TODO: Implement attachments.
        if attachments is not None:
            raise NotSupportedErr('Attachments are currently not implemented.')
        ##for attachment in attachments:
        ##    attms = ET.SubElement(req, 'attachments')
        ##    if attachment['name']:
        ##        ET.SubElement(attms, 'name').text = str(attachment['name'])
        ##    file_ = ET.SubElement(attms, 'file')
        ##    ET.SubElement(file_, 'file').text = str(attachment['temp_id'])
        ##    ET.SubElement(file_, 'content-type').text \
        ##        = str(attachment['content_type'])
        ##    ET.SubElement(file_, 'original-filename').text \
        ##        = str(attachment['original_filename'])
        return self._request(path, req)

    def update_message(self, message_id, category_id, title, body,
        extended_body, use_textile=False, private=False, notify=None):
        """
        Updates an existing message, optionally sending notifications to a
        selected list of people. Note that you can also upload files using
        this function, but you have to format the request as
        multipart/form-data. (See the ruby Basecamp API wrapper for an example
        of how to do this.)
        """
        path = '/msg/update/%u' % message_id
        req = ET.Element('request')
        req.append(self._create_message_post_elem(category_id, title, body,
            extended_body, use_textile=False, private=False))
        if notify is not None:
            for person_id in notify:
                ET.SubElement(req, 'notify').text = str(int(person_id))
        return self._request(path, req)

    def delete_message(self, message_id):
        """
        Delete the specified message from the project.
        """
        path = '/msg/delete/%u' % message_id
        return self._request(path)

    # Comments

    def comments(self, message_id):
        """
        Return the list of comments associated with the specified message.
        """
        path = '/msg/comments/%u' % message_id
        req = ET.Element('request')
        return self._request(path, req)

    def comment(self, comment_id):
        """
        Retrieve a specific comment by its id.
        """
        path = '/msg/comment/%u' % comment_id
        return self._request(path)

    def create_comment(self, post_id, body):
        """
        Create a new comment, associating it with a specific message.
        """
        path = '/msg/create_comment'
        req = ET.Element('request')
        comment = ET.SubElement(req, 'comment')
        ET.SubElement(comment, 'post-id').text = str(int(post_id))
        ET.SubElement(comment, 'body').text = str(body)
        return self._request(path, req)

    def update_comment(self, comment_id, body):
        """
        Update a specific comment. This can be used to edit the content of an
        existing comment.
        """
        path = '/msg/update_comment'
        req = ET.Element('request')
        ET.SubElement(req, 'comment_id').text = str(int(comment_id))
        comment = ET.SubElement(req, 'comment')
        ET.SubElement(comment, 'body').text = str(body)
        return self._request(path, req)

    def delete_comment(self, comment_id):
        """
        Delete the comment with the given id.
        """
        path = '/msg/delete_comment/%u' % comment_id
        return self._request(path)

    # ---------------------------------------------------------------- #
    # To-do Lists and Items

    # Lists

    def todo_lists(self, project_id, complete=None):
        """
        This will return the metadata for all of the lists in a given project.
        You can further constrain the query to only return those lists that
        are "complete" (have no uncompleted items) or "uncomplete" (have
        uncompleted items remaining).
        """
        path = '/projects/%u/todos/lists' % project_id
        req = ET.Element('request')
        if complete is not None:
            ET.SubElement(req, 'complete').text = str(bool(complete)).lower()
        return self._request(path, req)

    def todo_list(self, list_id):
        """
        This will return the metadata and items for a specific list.
        """
        path = '/todos/list/%u' % list_id
        return self._request(path)

    def create_todo_list(self, project_id, milestone_id=None, private=None,
        tracked=False, name=None, description=None, template_id=None):
        """
        This will create a new, empty list. You can create the list
        explicitly, or by giving it a list template id to base the new list
        off of.
        """
        path = '/projects/%u/todos/create_list' % project_id
        req = ET.Element('request')
        if milestone_id is not None:
            ET.SubElement('milestone-id').text = str(milestone_id)
        if private is not None:
            ET.SubElement('private').text = str(bool(private)).lower()
        ET.SubElement('tracked').text = str(bool(tracked)).lower()
        if name is not None:
            ET.SubElement('name').text = str(name)
            ET.SubElement('description').text = str(description)
        if template_id is not None:
            ET.SubElement('use-template').text = 'true'
            ET.SubElement('template-id').text = str(int(template_id))
        return self._request(path, req)

    def update_todo_list(self, list_id, name, description, milestone_id=None,
        private=None, tracked=None):
        """
        With this call you can alter the metadata for a list.
        """
        path = '/todos/update_list/%u' % list_id
        req = ET.Element('request')
        list_ = ET.SubElement('list')
        ET.SubElement(list_, 'name').text = str(name)
        ET.SubElement(list_, 'description').text = str(description)
        if milestone_id is not None:
            ET.SubElement(list_, 'milestone_id').text = str(int(milestone_id))
        if private is not None:
            ET.SubElement(list_, 'private').text = str(bool(private)).lower()
        if tracked is not None:
            ET.SubElement(list_, 'tracked').text = str(bool(tracked)).lower()
        return self._request(path, req)

    def move_todo_list(self, list_id, to):
        """
        This allows you to reposition a list relative to the other lists in
        the project. A list with position 1 will show up at the top of the
        page. Moving lists around lets you prioritize. Moving a list to a
        position less than 1, or more than the number of lists in a project,
        will force the position to be between 1 and the number of lists
        (inclusive).
        """
        path = '/todos/move_list/%u' % list_id
        req = ET.Element('request')
        ET.SubElement(req, 'to').text = str(int(to))
        return self._request(path, req)

    def delete_todo_list(self, list_id):
        """
        This call will delete the entire referenced list and all items
        associated with it. Use it with caution, because a deleted list cannot
        be restored!
        """
        path = '/todos/delete_list/%u' % list_id
        return self._request(path)

    # Items

    def create_todo_item(self, list_id, content, party_id=None, notify=False):
        """
        This call lets you add an item to an existing list. The item is added
        to the bottom of the list. If a person is responsible for the item,
        give their id as the party_id value. If a company is responsible,
        prefix their company id with a 'c' and use that as the party_id value.
        If the item has a person as the responsible party, you can use the
        notify key to indicate whether an email should be sent to that person
        to tell them about the assignment.
        """
        path = '/todos/create_item/%u' % list_id
        req = ET.Element('request')
        ET.SubElement(req, 'content').text = str(content)
        if party_id is not None:
            ET.SubElement(req, 'responsible-party').text = str(party_id)
            ET.SubElement(req, 'notify').text = str(bool(notify)).lower()
        return self._request(path, req)

    def update_todo_item(self, item_id, content, party_id=None, notify=False):
        """
        Modifies an existing item. The values work much like the "create item"
        operation, so you should refer to that for a more detailed explanation.
        """
        path = '/todos/update_item/%u' % item_id
        req = ET.Element('request')
        item = ET.Element('request')
        ET.SubElement(item, 'content').text = str(content)
        if party_id is not None:
            ET.SubElement(req, 'responsible-party').text = str(party_id)
            ET.SubElement(req, 'notify').text = str(bool(notify)).lower()
        return self._request(path, req)

    def complete_todo_item(self, item_id):
        """
        Marks the specified item as "complete". If the item is already
        completed, this does nothing.
        """
        path = '/todos/complete_item/%u' % item_id
        return self._request(path)

    def uncomplete_todo_item(self, item_id):
        """
        Marks the specified item as "uncomplete". If the item is already
        uncompleted, this does nothing.
        """
        path = '/todos/uncomplete_item/%u' % item_id
        return self._request(path)

    def move_todo_item(self, item_id, to):
        """
        Changes the position of an item within its parent list. It does not
        currently support reparenting an item. Position 1 is at the top of the
        list. Moving an item beyond the end of the list puts it at the bottom
        of the list.
        """
        path = '/todos/move_item/%u' % item_id
        req = ET.Element('request')
        ET.SubElement(req, 'to').text = str(int(to))
        return self._request(path, req)

    def delete_todo_item(self, item_id):
        """
        Deletes the specified item, removing it from its parent list.
        """
        path = '/todos/delete_item/%u' % item_id
        return self._request(path)

    # ---------------------------------------------------------------- #
    # Milestones

    def list_milestones(self, project_id, find=None):
        """
        This lets you query the list of milestones for a project. You can
        either return all milestones, or only those that are late, completed,
        or upcoming.
        """
        path = '/projects/%u/milestones/list' % project_id
        req = ET.Element('request')
        if find is not None:
            ET.SubElement(req, 'find').text = str(find)
        return self._request(path, req)

    def _create_milestone_elem(self, title, deadline, party_id, notify):
        milestone = ET.Element('milestone')
        ET.SubElement(milestone, 'title').text = str(title)
        ET.SubElement(milestone, 'deadline', type='date').text = str(deadline)
        ET.SubElement(milestone, 'responsible-party').text = str(party_id)
        ET.SubElement(milestone, 'notify').text = str(bool(notify)).lower()
        return milestone

    def create_milestone(self, project_id, title, deadline, party_id, notify):
        """
        Creates a single milestone. To create multiple milestones in a single
        call, see the "create (batch)" function. To make a company responsible
        for the milestone, prefix the company id with a "c".
        """
        path = '/projects/%u/milestones/create' % project_id
        req = ET.Element('request')
        req.append(
            self._create_milestone_elem(title, deadline, party_id, notify))
        return self._request(path, req)

    def create_milestones(self, project_id, milestones):
        """
        With this function you can create multiple milestones in a single
        request. See the "create" function for a description of the individual
        fields in the milestone.
        """
        path = '/projects/%u/milestones/create' % project_id
        req = ET.Element('request')
        for milestone in milestones:
            req.append(self._create_milestone_elem(*milestone))
        return self._request(path, req)

    def update_milestone(self, milestone_id, title, deadline, party_id, notify,
        move_upcoming_milestones=None,
        move_upcoming_milestones_off_weekends=None):
        """
        Modifies a single milestone. You can use this to shift the deadline of
        a single milestone, and optionally shift the deadlines of subsequent
        milestones as well.
        """
        path = '/milestones/update/%u' % milestone_id
        req = ET.Element('request')
        req.append(
            self._create_milestone_elem(title, deadline, party_id, notify))
        if move_upcoming_milestones is not None:
            ET.SubElement(req, 'move-upcoming-milestones').text \
                = str(bool()).lower()
        if move_upcoming_milestones_off_weekends is not None:
            ET.SubElement(req, 'move-upcoming-milestones-off-weekends').text \
                = str(bool()).lower()
        return self._request(path, req)

    def complete_milestone(self, milestone_id):
        """
        Marks the specified milestone as complete.
        """
        path = '/milestones/complete/%u' % milestone_id
        return self._request(path)

    def uncomplete_milestone(self, milestone_id):
        """
        Marks the specified milestone as uncomplete.
        """
        path = '/milestones/uncomplete/%u' % milestone_id
        return self._request(path)

    def delete_milestone(self, milestone_id):
        """
        Deletes the given milestone from the project.
        """
        path = '/milestones/delete/%u' % milestone_id
        return self._request(path)
