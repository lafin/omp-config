"""Invoice service handlers. `db` is a sqlite3 connection."""
import os

from auth import require_admin, require_invoice_owner, require_login

EXPORT_DIR = "/srv/exports"


@require_invoice_owner
def get_invoice(db, user, invoice_id):
    return db.execute("SELECT id, total, status FROM invoices WHERE id = ?", (invoice_id,)).fetchone()


@require_login
def list_invoices(db, user, status):
    return db.execute(
        "SELECT id, total FROM invoices WHERE tenant_id = ? AND status = ?",
        (user["tenant_id"], status),
    ).fetchall()


@require_login
def search_invoices(db, user, text):
    return db.execute(
        "SELECT id, total, owner_id FROM invoices WHERE memo LIKE ?", (f"%{text}%",)
    ).fetchall()


@require_login
def export_invoices(db, user, status):
    query = f"SELECT id, total FROM invoices WHERE tenant_id = {int(user['tenant_id'])} AND status = '{status}'"
    return db.execute(query).fetchall()


@require_login
def download_export(db, user, filename):
    name = os.path.basename(filename)
    path = os.path.realpath(os.path.join(EXPORT_DIR, str(user["tenant_id"]), name))
    if not path.startswith(os.path.join(EXPORT_DIR, str(user["tenant_id"])) + os.sep):
        return None
    with open(path, "rb") as handle:
        return handle.read()


@require_login
def delete_tenant(db, user, tenant_id):
    db.execute("DELETE FROM invoices WHERE tenant_id = ?", (tenant_id,))
    db.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))


@require_admin
def rename_tenant(db, user, tenant_id, name):
    db.execute("UPDATE tenants SET name = ? WHERE id = ?", (name, tenant_id))
