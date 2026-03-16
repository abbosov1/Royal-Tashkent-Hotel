with open('app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_migration = '''# Auto-migrate is_admin column for existing DBs (like on Vercel)
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE"))
        conn.commit()
except Exception as e:
    print(f"Migration error (could be SQLite or already exists): {e}")
    try:
        # Fallback for SQLite locally if needed
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
            conn.commit()
    except:
        pass'''

new_migration = '''# Auto-migrate is_admin column for existing DBs (like on Vercel)
try:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE"))
except Exception as e:
    print(f"Migration error (could be SQLite or already exists): {e}")
    try:
        # Fallback for SQLite locally if needed
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
    except:
        pass'''

if old_migration in text:
    text = text.replace(old_migration, new_migration)
    with open('app/main.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Migration logic updated safely!")
