"""Request guards. A handler receives `user` = {"id", "tenant_id", "role"} or None."""
from functools import wraps


class Denied(Exception):
    pass


def require_login(fn):
    @wraps(fn)
    def wrapper(db, user, *args):
        if user is None:
            raise Denied(401)
        return fn(db, user, *args)
    return wrapper


def require_admin(fn):
    @wraps(fn)
    def wrapper(db, user, *args):
        if user is None or user["role"] != "admin":
            raise Denied(403)
        return fn(db, user, *args)
    return wrapper


def require_invoice_owner(fn):
    @wraps(fn)
    def wrapper(db, user, invoice_id, *args):
        if user is None:
            raise Denied(401)
        row = db.execute("SELECT owner_id FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
        if row is None or row[0] != user["id"]:
            raise Denied(404)
        return fn(db, user, invoice_id, *args)
    return wrapper
