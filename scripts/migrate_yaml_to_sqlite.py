#!/usr/bin/env python3
"""
Migrate knowledge from YAML files to claude_memory.db
"""
import sqlite3
import yaml
import json
from pathlib import Path

# Get repo root
repo_root = Path(__file__).parent.parent
db_file = repo_root / "claude_memory.db"

# YAML source files
agent_skills_file = repo_root / "agents" / "AGENT_SKILLS_REGISTRY.yaml"
knowledge_base_file = repo_root / "agents" / "knowledge" / "KNOWLEDGE_BASE_INDEX.yaml"
capability_matrix_file = repo_root / "agents" / "capabilities" / "CAPABILITY_MATRIX.yaml"

def load_yaml(file_path):
    """Load YAML file"""
    if not file_path.exists():
        print(f"⚠️  YAML file not found: {file_path}")
        return None

    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def format_skills_markdown(skills_data):
    """Convert skills to markdown"""
    md = "# Agent Skills\n\n"

    if not skills_data or 'skills' not in skills_data:
        return md

    for skill in skills_data['skills']:
        md += f"## {skill.get('name', 'Unnamed Skill')}\n\n"
        md += f"**ID:** `{skill.get('id')}`\n\n"
        md += f"**Domain:** {skill.get('domain')}\n\n"
        md += f"**Description:** {skill.get('description', 'No description')}\n\n"

        if 'inputs' in skill:
            md += "**Inputs:**\n"
            for inp in skill['inputs']:
                md += f"- {inp}\n"
            md += "\n"

        if 'outputs' in skill:
            md += "**Outputs:**\n"
            for out in skill['outputs']:
                md += f"- {out}\n"
            md += "\n"

        if 'tools' in skill:
            md += f"**Tools:** {', '.join(skill['tools'])}\n\n"

        if 'knowledge_refs' in skill:
            md += f"**Knowledge References:** {', '.join(skill['knowledge_refs'])}\n\n"

        md += "---\n\n"

    return md

def format_capabilities_markdown(capabilities_data):
    """Convert capabilities to markdown"""
    md = "# Agent Capabilities\n\n"
    md += "*Composite workflows combining multiple skills*\n\n"

    if not capabilities_data or 'capabilities' not in capabilities_data:
        return md

    for cap in capabilities_data['capabilities']:
        md += f"## {cap.get('name', 'Unnamed Capability')}\n\n"
        md += f"**ID:** `{cap.get('id')}`\n\n"
        md += f"**Description:** {cap.get('description', 'No description')}\n\n"

        if 'skills' in cap:
            md += "**Skills Used:**\n"
            for skill in cap['skills']:
                md += f"- {skill}\n"
            md += "\n"

        if 'features' in cap:
            md += "**Features:**\n"
            for feature in cap['features']:
                md += f"- {feature}\n"
            md += "\n"

        if 'preconditions' in cap:
            md += "**Preconditions:**\n"
            for precond in cap['preconditions']:
                md += f"- {precond}\n"
            md += "\n"

        if 'validation' in cap:
            md += "**Validation:**\n"
            for val in cap['validation']:
                md += f"- {val}\n"
            md += "\n"

        if 'knowledge_refs' in cap:
            md += f"**Knowledge References:** {', '.join(cap['knowledge_refs'])}\n\n"

        md += "---\n\n"

    return md

def format_procedures_markdown(procedures_data):
    """Convert procedures to markdown"""
    md = "# Execution Procedures\n\n"
    md += "*Step-by-step playbooks for common agent tasks*\n\n"

    if not procedures_data or 'procedures' not in procedures_data:
        return md

    for proc_name, proc_data in procedures_data['procedures'].items():
        md += f"## {proc_name.replace('_', ' ').title()}\n\n"
        md += f"**Description:** {proc_data.get('description', 'No description')}\n\n"

        if 'steps' in proc_data:
            md += "**Steps:**\n"
            for step in proc_data['steps']:
                md += f"- {step}\n"
            md += "\n"

        md += "---\n\n"

    return md

def format_knowledge_base_markdown(kb_data):
    """Convert knowledge base index to markdown"""
    md = "# Knowledge Base Index\n\n"

    if not kb_data or 'documentation' not in kb_data:
        return md

    md += "## Documentation Sources\n\n"
    for doc in kb_data['documentation']:
        md += f"### {doc.get('title', 'Untitled')}\n\n"
        md += f"**Path:** `{doc.get('path')}`\n\n"
        md += f"**Domain:** {doc.get('domain')}\n\n"
        md += f"**Type:** {doc.get('type')}\n\n"

        if 'topics' in doc:
            md += "**Topics:**\n"
            for topic in doc['topics']:
                md += f"- {topic}\n"
            md += "\n"

        if 'agent_use' in doc:
            md += f"**Agent Use:** {doc['agent_use']}\n\n"

        md += "---\n\n"

    # Add best practices
    if 'best_practices' in kb_data:
        md += "## Best Practices\n\n"
        for domain, practices in kb_data['best_practices'].items():
            md += f"### {domain.replace('_', ' ').title()}\n\n"
            for practice in practices:
                md += f"- {practice}\n"
            md += "\n"

    return md

def main():
    print("🔄 Starting YAML to SQLite migration...\n")

    # Load YAML files
    print("📖 Loading YAML files...")
    agent_skills_data = load_yaml(agent_skills_file)
    knowledge_base_data = load_yaml(knowledge_base_file)
    capability_matrix_data = load_yaml(capability_matrix_file)

    # Connect to database
    print(f"📦 Connecting to database: {db_file}")
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()

    try:
        # Migrate skills
        if agent_skills_data:
            print("\n📝 Migrating skills...")
            skills_md = format_skills_markdown(agent_skills_data)
            cursor.execute("""
                INSERT OR REPLACE INTO sections (key, title, markdown)
                VALUES (?, ?, ?)
            """, ('agent_skills', 'Agent Skills Registry', skills_md))
            print(f"  ✅ Migrated {len(agent_skills_data.get('skills', []))} skills")

            # Migrate capabilities from skills file
            if 'capabilities' in agent_skills_data:
                print("\n📝 Migrating capabilities from skills file...")
                caps_md = format_capabilities_markdown(agent_skills_data)
                cursor.execute("""
                    INSERT OR REPLACE INTO sections (key, title, markdown)
                    VALUES (?, ?, ?)
                """, ('agent_capabilities', 'Agent Capabilities', caps_md))
                print(f"  ✅ Migrated {len(agent_skills_data.get('capabilities', []))} capabilities")

            # Migrate procedures from skills file
            if 'procedures' in agent_skills_data:
                print("\n📝 Migrating procedures from skills file...")
                proc_md = format_procedures_markdown(agent_skills_data)
                cursor.execute("""
                    INSERT OR REPLACE INTO sections (key, title, markdown)
                    VALUES (?, ?, ?)
                """, ('execution_procedures', 'Execution Procedures', proc_md))
                print(f"  ✅ Migrated {len(agent_skills_data.get('procedures', {}))} procedures")

        # Migrate capability matrix
        if capability_matrix_data:
            print("\n📝 Migrating capability matrix...")
            cap_matrix_md = format_capabilities_markdown(capability_matrix_data)
            cursor.execute("""
                INSERT OR REPLACE INTO sections (key, title, markdown)
                VALUES (?, ?, ?)
            """, ('capability_matrix', 'Capability Execution Matrix', cap_matrix_md))
            print(f"  ✅ Migrated capability matrix")

        # Migrate knowledge base
        if knowledge_base_data:
            print("\n📝 Migrating knowledge base index...")
            kb_md = format_knowledge_base_markdown(knowledge_base_data)
            cursor.execute("""
                INSERT OR REPLACE INTO sections (key, title, markdown)
                VALUES (?, ?, ?)
            """, ('knowledge_base_index', 'Knowledge Base Index', kb_md))
            print(f"  ✅ Migrated knowledge base index")

        # Commit changes
        conn.commit()

        # Verify migration
        print("\n📊 Verifying migration...")
        cursor.execute("SELECT key, title FROM sections ORDER BY key")
        sections = cursor.fetchall()
        print("\n📋 Sections in database:")
        for key, title in sections:
            print(f"  - {key}: {title}")

        print("\n✅ Migration complete!")

    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
