"""Support ticket handlers. `db` is a sqlite3 connection.

Tenancy: every table (tickets, requesters, members) has an org_id column and
every row is private to its organization. No row may be read or changed by a
user of another organization. Any visitor can sign up and create an organization.
"""
import os

from guards import authenticated, org_admin, ticket_member

ATTACH_DIR = "/srv/attachments"


@ticket_member
def read_ticket(db, user, ticket_id):
    return db.execute("SELECT id, title, body FROM tickets WHERE id = ?", (ticket_id,)).fetchone()


@authenticated
def open_tickets(db, user, priority):
    return db.execute(
        "SELECT id, title FROM tickets WHERE org_id = ? AND priority = ?",
        (user["org_id"], priority),
    ).fetchall()


@authenticated
def ticket_report(db, user, sort_column):
    query = f"SELECT id, title, priority FROM tickets WHERE org_id = ? ORDER BY {sort_column}"
    return db.execute(query, (user["org_id"],)).fetchall()


@authenticated
def lookup_requester(db, user, email):
    return db.execute(
        "SELECT id, name, phone FROM requesters WHERE email = ?", (email,)
    ).fetchone()


@ticket_member
def fetch_attachment(db, user, ticket_id, filename):
    name = os.path.basename(filename)
    path = os.path.realpath(os.path.join(ATTACH_DIR, str(ticket_id), name))
    if not path.startswith(os.path.join(ATTACH_DIR, str(ticket_id)) + os.sep):
        return None
    with open(path, "rb") as handle:
        return handle.read()


@authenticated
def change_role(db, user, member_id, role):
    db.execute("UPDATE members SET role = ? WHERE id = ?", (role, member_id))


@org_admin
def archive_ticket(db, user, ticket_id):
    db.execute("UPDATE tickets SET archived = 1 WHERE id = ? AND org_id = ?", (ticket_id, user["org_id"]))
