"""Request guards. A handler receives `user` = {"id", "org_id", "role"} or None."""
from functools import wraps


class Forbidden(Exception):
    pass


def authenticated(fn):
    @wraps(fn)
    def wrapper(db, user, *args):
        if user is None:
            raise Forbidden(401)
        return fn(db, user, *args)
    return wrapper


def org_admin(fn):
    @wraps(fn)
    def wrapper(db, user, *args):
        if user is None or user["role"] != "org_admin":
            raise Forbidden(403)
        return fn(db, user, *args)
    return wrapper


def ticket_member(fn):
    @wraps(fn)
    def wrapper(db, user, ticket_id, *args):
        if user is None:
            raise Forbidden(401)
        row = db.execute("SELECT org_id FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if row is None or row[0] != user["org_id"]:
            raise Forbidden(404)
        return fn(db, user, ticket_id, *args)
    return wrapper
