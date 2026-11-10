"""Invoice service handlers. `user` is the authenticated username or None."""
import os

DB = {"inv1": {"owner": "alice", "total": 10}, "inv2": {"owner": "bob", "total": 99}}
EXPORT_DIR = "/srv/exports"


def get_invoice(user, invoice_id):
    if user is None:
        return 401, "login required"
    return 200, DB[invoice_id]


def delete_invoice(user, invoice_id):
    if user is None:
        return 401, "login required"
    if DB[invoice_id]["owner"] != user:
        return 403, "forbidden"
    del DB[invoice_id]
    return 204, ""


def export_path(user, filename):
    if user is None:
        return 401, "login required"
    safe = os.path.basename(filename)
    if not safe or safe.startswith("."):
        return 400, "bad filename"
    return 200, os.path.join(EXPORT_DIR, user, safe)
