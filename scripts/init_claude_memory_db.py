#!/usr/bin/env python3
"""
Initialize claude_memory.db from schema file
"""
import sqlite3
import sys
from pathlib import Path

# Get repo root
repo_root = Path(__file__).parent.parent
schema_file = repo_root / "schema" / "claude_memory_schema.sql"
db_file = repo_root / "claude_memory.db"

# Read schema
if not schema_file.exists():
    print(f"❌ Schema file not found: {schema_file}")
    sys.exit(1)

with open(schema_file, 'r') as f:
    schema_sql = f.read()

# Create database
print(f"📦 Creating database: {db_file}")
conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

# Execute schema
try:
    cursor.executescript(schema_sql)
    conn.commit()
    print("✅ Database initialized successfully")

    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"\n📋 Tables created:")
    for table in tables:
        print(f"  - {table[0]}")

    # Verify seed data
    cursor.execute("SELECT COUNT(*) FROM sections")
    section_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM facts")
    fact_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM file_notes")
    file_note_count = cursor.fetchone()[0]

    print(f"\n📊 Seed data loaded:")
    print(f"  - Sections: {section_count}")
    print(f"  - Facts: {fact_count}")
    print(f"  - File notes: {file_note_count}")

except Exception as e:
    print(f"❌ Error initializing database: {e}")
    sys.exit(1)
finally:
    conn.close()

print(f"\n✅ Database ready at: {db_file}")
