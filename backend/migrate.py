#!/usr/bin/env python3
"""
Database migration runner for Accessify.

Usage:
    python migrate.py          # Run all pending migrations
    python migrate.py --reset  # Drop all tables and recreate from scratch
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import mysql.connector
from db import _conn_config

# Load environment variables
load_dotenv()


def get_connection():
    """Get a direct database connection."""
    return mysql.connector.connect(**_conn_config())


def create_migrations_table(conn):
    """Create migrations tracking table if it doesn't exist."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            migration_name VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_migration_name (migration_name)
        )
    """)
    conn.commit()
    cursor.close()


def get_applied_migrations(conn):
    """Get list of already applied migrations."""
    cursor = conn.cursor()
    cursor.execute("SELECT migration_name FROM schema_migrations ORDER BY id")
    applied = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return applied


def get_migration_files():
    """Get list of migration files in order."""
    migrations_dir = Path(__file__).parent / "migrations"
    if not migrations_dir.exists():
        return []
    
    migration_files = sorted(migrations_dir.glob("*.sql"))
    return migration_files


def apply_migration(conn, migration_file):
    """Apply a single migration file."""
    print(f"Applying migration: {migration_file.name}")
    
    with open(migration_file, 'r') as f:
        sql_content = f.read()
    
    # Split by semicolons but handle multi-statement blocks
    cursor = conn.cursor()
    
    try:
        # Execute the entire migration as a single script
        for statement in sql_content.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        
        conn.commit()
        
        # Record migration as applied
        cursor.execute(
            "INSERT INTO schema_migrations (migration_name) VALUES (%s)",
            (migration_file.name,)
        )
        conn.commit()
        
        print(f"✓ Successfully applied: {migration_file.name}")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Failed to apply {migration_file.name}: {e}")
        raise
    finally:
        cursor.close()


def run_migrations():
    """Run all pending migrations."""
    conn = get_connection()
    
    try:
        # Ensure migrations table exists
        create_migrations_table(conn)
        
        # Get applied migrations
        applied = get_applied_migrations(conn)
        print(f"Already applied migrations: {len(applied)}")
        
        # Get migration files
        migration_files = get_migration_files()
        print(f"Total migration files: {len(migration_files)}")
        
        # Apply pending migrations
        pending = [f for f in migration_files if f.name not in applied]
        
        if not pending:
            print("No pending migrations.")
            return
        
        print(f"\nApplying {len(pending)} pending migration(s)...")
        for migration_file in pending:
            apply_migration(conn, migration_file)
        
        print(f"\n✓ All migrations applied successfully!")
        
    finally:
        conn.close()


def reset_database():
    """Drop all tables and recreate from scratch."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("WARNING: This will drop all tables and data!")
        response = input("Are you sure? Type 'yes' to continue: ")
        
        if response.lower() != 'yes':
            print("Aborted.")
            return
        
        print("\nDropping all tables...")
        
        # Drop tables in reverse dependency order
        tables = [
            'schema_migrations',
            'audit_log',
            'issue',
            'chunk',
            'page',
            'website',
            'domain',
            'ethics_acceptance',
            'ethics_agreement',
            'session',
            'user',
            'organization'
        ]
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  Dropped: {table}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        conn.commit()
        print("\n✓ All tables dropped.")
        
        # Recreate base schema
        print("\nRecreating base schema...")
        models_sql = Path(__file__).parent / "models.sql"
        if models_sql.exists():
            with open(models_sql, 'r') as f:
                sql_content = f.read()
            
            for statement in sql_content.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    cursor.execute(statement)
            
            conn.commit()
            print("✓ Base schema created.")
        
        cursor.close()
        conn.close()
        
        # Now run migrations
        print("\nRunning migrations...")
        run_migrations()
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error during reset: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_database()
    else:
        run_migrations()
