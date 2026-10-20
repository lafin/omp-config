"""Notes service handlers. `user` is the authenticated username or None."""
import html

NOTES = {"n1": {"owner": "alice", "body": "hi", "shared_with": []}}


def read_note(user, note_id):
    if user is None:
        return 401, "login required"
    note = NOTES[note_id]
    if note["owner"] != user and user not in note["shared_with"]:
        return 403, "forbidden"
    return 200, note["body"]


def share_note(user, note_id, target):
    if user is None:
        return 401, "login required"
    NOTES[note_id]["shared_with"].append(target)
    return 204, ""


def render_note(user, note_id):
    status, body = read_note(user, note_id)
    if status != 200:
        return status, body
    return 200, "<p>" + html.escape(body) + "</p>"
