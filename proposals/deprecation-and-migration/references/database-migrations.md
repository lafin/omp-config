# Database Migration Patterns

Provenance: adapted (modified) from `https://github.com/affaan-m/ECC` at commit
`4eb71d92a39cab44ad40ac9d8a6a5ccb4029d6c2`, path
`skills/database-migrations/SKILL.md`, MIT License; see `LICENSE-ecc`. Per-tool
command catalogs (Prisma, Drizzle, Kysely, Django, golang-migrate) were dropped;
the rename sequence was corrected so old writes stop before the drop.

Read this when the change alters a persisted schema or backfills data. It
details the database branch of the skill; the expand → backfill → verify →
cut over → contract order in `SKILL.md` stays authoritative.

## Rules

1. Every production change is a versioned migration. No manual DDL or DML in
   production.
2. Production migrations are forward-only. Roll back with a new forward
   migration or a reversible read/traffic switch, not by editing history.
3. A migration that has run anywhere shared is immutable.
4. Schema (DDL) and data (DML) changes are separate migrations.
5. Size the plan from production row counts and write rates. A migration that
   is instant on 100 rows can hold a lock for minutes on 10 million.

## Lock and timeout safety (PostgreSQL)

| Operation | Risk | Safe form |
|---|---|---|
| `ADD COLUMN ... NOT NULL` without default | Full rewrite under exclusive lock | Add nullable, backfill, then add the constraint; on PostgreSQL 11+ a constant default is metadata-only |
| `CREATE INDEX` on a live table | Blocks writes for the build | `CREATE INDEX CONCURRENTLY`; it cannot run inside a transaction block, so mark the migration non-transactional |
| `ADD CONSTRAINT ... NOT NULL` / `CHECK` / foreign key | Full scan under lock | Add as `NOT VALID`, then `VALIDATE CONSTRAINT` in a later migration |
| `RENAME COLUMN` / `DROP COLUMN` with live readers | Old application version fails | Expand-contract; drop only after no reader or writer remains |
| Any DDL behind a long transaction | Queues every later query on the table | Set `lock_timeout` (for example `SET lock_timeout = '5s'`) and retry instead of waiting |

A failed `CREATE INDEX CONCURRENTLY` leaves an `INVALID` index. Drop it and
retry; do not treat its existence as success.

## Expand-contract rename

1. Expand: add the new column, nullable.
2. Deploy code that writes both columns and still reads the old one.
3. Backfill the new column in batches (below).
4. Verify: every row matches under explicit invariants, including writes that
   arrived during the backfill.
5. Deploy code that reads the new column and still writes both.
6. After the rollback window, deploy code that stops writing the old column.
7. Contract: drop the old column in a later, dedicated migration.

Removing a column follows steps 6–7 only: remove every code reference, deploy,
then drop. ORMs that generate the drop from the model need the model change and
the database drop split across releases.

## Batched backfill

Never update every row in one statement or transaction. Use a stable cursor,
bounded batches, a commit per batch, and an idempotent predicate so a restart
skips finished rows:

```sql
-- Repeat until 0 rows are updated; run from a job, one transaction per batch.
UPDATE users
SET normalized_email = lower(email)
WHERE id IN (
  SELECT id FROM users
  WHERE normalized_email IS NULL
  ORDER BY id
  LIMIT 10000
  FOR UPDATE SKIP LOCKED
);
```

Throttle between batches, emit progress (rows remaining), and stop on
replication lag or error-rate thresholds. `SKIP LOCKED` rows are retried on the
next pass; finish with a count of remaining rows equal to zero.

## Pre-apply checklist

- Reversal is defined: a down migration, or an explicit irreversible mark plus
  the forward fix that replaces it.
- No operation in the table above runs in its unsafe form on a large table.
- Schema and backfill are separate migrations.
- Rehearsed against a production-sized copy, with measured duration and locks.
- Rollback boundary named: which step is the last one that can be undone
  without restoring data.
