# Database Migrations

This directory contains SQL migration files for the Accessify database schema.

## Migration Files

Migrations are numbered sequentially and should be named with the format:
```
NNN_description.sql
```

For example:
- `001_add_auth_and_org_tables.sql`
- `002_add_new_feature.sql`

## Running Migrations

### Apply All Pending Migrations

From the `backend` directory:

```bash
python migrate.py
```

This will:
1. Create a `schema_migrations` table if it doesn't exist
2. Check which migrations have already been applied
3. Apply any pending migrations in order
4. Record each migration in the tracking table

### Reset Database (Development Only)

**WARNING**: This will drop all tables and data!

```bash
python migrate.py --reset
```

This will:
1. Drop all existing tables
2. Recreate the base schema from `models.sql`
3. Run all migrations from scratch

## Creating New Migrations

1. Create a new `.sql` file in this directory with the next sequential number
2. Write your SQL statements (CREATE TABLE, ALTER TABLE, etc.)
3. Make migrations idempotent when possible using `IF NOT EXISTS` or similar checks
4. Test the migration on a development database
5. Run `python migrate.py` to apply

## Migration Tracking

Applied migrations are tracked in the `schema_migrations` table:

```sql
CREATE TABLE schema_migrations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    migration_name VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Best Practices

1. **Never modify applied migrations** - Create a new migration instead
2. **Make migrations reversible** when possible (though we don't currently support rollback)
3. **Test migrations** on development data before production
4. **Use transactions** where appropriate (though some DDL statements auto-commit)
5. **Document complex migrations** with comments in the SQL file
