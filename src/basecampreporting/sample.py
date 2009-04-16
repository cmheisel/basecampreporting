"""Silly command line dump of the status of a project, provided as a sample of how you might use the module."""

from project import Project

def main(url, project_id, username, password):
    p = Project(url, project_id, username, password)

    try:
        p.name
    except Exception:
        print "Couldn't access %s/projects/%s/project/log/ -- does the user %s have access?" % (url, project_id, username)
        return None

    try:
        previous_milestone = p.previous_milestones[0]
        previous_milestone_completed = "Progress"
        if previous_milestone.completed: previous_milestone_completed = "Complete"
    except IndexError:
        previous_milestone = None

    try:
        next_milestone = p.upcoming_milestones[0]
    except IndexError:
        next_milestone = None

    try:
        last_message = p.messages[0]
    except IndexError:
        last_message = None

    try:
        last_comment = p.comments[0]
        last_communique = last_comment
        if last_message and last_message.posted_on > last_comment.posted_on:
            last_communique = last_comment
    except IndexError:
        last_comment = None
        last_communique = None

    backlog_count = len(p.backlogs.keys())

    late_milestones = p.late_milestones

    if p.current_sprint:
        print "%s -- %s" % (p.name, p.current_sprint.name)
    else:
        print p.name

    if previous_milestone:
        print "Prev milestone: %s (%s)" % (previous_milestone.title, previous_milestone_completed)

    if next_milestone:
        print "Next milestone: %s on %s" % (next_milestone.title, next_milestone.deadline)

    if not next_milestone:
        print "No new milestones planned"

    if len(late_milestones):
        print "Late milestones: %s" % (len(late_milestones))

    if last_communique:
        print "Last message/comment: %s" % (last_communique.posted_on)

    print "%s items in %s backlogs" % (p.backlogged_count, backlog_count)
    print "%s upcoming sprints planned" % (len(p.upcoming_sprints))
    print "Last changed at: %s" % (p.last_changed_on)
    print ""