import aiosqlite
import os

# Railway da /tmp papkasi har doim yozish mumkin
DB_PATH = "/tmp/ecoulash.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER UNIQUE NOT NULL,
                username  TEXT,
                full_name TEXT,
                phone     TEXT,
                role      TEXT DEFAULT 'user',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                donor_id    INTEGER NOT NULL,
                item_name   TEXT NOT NULL,
                quantity    INTEGER DEFAULT 1,
                description TEXT,
                status      TEXT DEFAULT 'pending',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                item_name   TEXT NOT NULL,
                quantity    INTEGER DEFAULT 1,
                description TEXT,
                status      TEXT DEFAULT 'pending',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS volunteers (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER UNIQUE NOT NULL,
                skills       TEXT,
                availability TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                user_id    INTEGER,
                data       TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


# ── Foydalanuvchilar ──────────────────────────────────────────────────────────

async def add_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?,?,?)",
            (user_id, username, full_name)
        )
        await db.commit()


async def get_user(user_id: int):
    """
    Qaytaradi: (id, user_id, username, full_name, phone, role, joined_at, is_active)
    Indekslar:   0    1        2         3          4      5     6          7
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cur:
            return await cur.fetchone()


async def get_all_users():
    """Qaytaradi: (user_id, username, full_name, phone)"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, username, full_name, phone FROM users WHERE is_active=1"
        ) as cur:
            return await cur.fetchall()


async def get_all_active_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id FROM users WHERE is_active=1"
        ) as cur:
            rows = await cur.fetchall()
            return [r[0] for r in rows]


async def update_user_info(user_id: int, first_name: str, last_name: str, phone: str):
    full_name = first_name + " " + last_name
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET full_name=?, phone=? WHERE user_id=?",
            (full_name, phone, user_id)
        )
        await db.commit()


# ── Ehsonlar ──────────────────────────────────────────────────────────────────

async def add_donation(donor_id: int, item_name: str, quantity: int, description: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO donations (donor_id,item_name,quantity,description) VALUES (?,?,?,?)",
            (donor_id, item_name, quantity, description)
        )
        await db.commit()


async def get_donations(status: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if status:
            async with db.execute(
                "SELECT * FROM donations WHERE status=? ORDER BY created_at DESC", (status,)
            ) as cur:
                return await cur.fetchall()
        async with db.execute(
            "SELECT * FROM donations ORDER BY created_at DESC"
        ) as cur:
            return await cur.fetchall()


# ── Yordam so'rovlari ─────────────────────────────────────────────────────────

async def add_request(user_id: int, item_name: str, quantity: int, description: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO requests (user_id,item_name,quantity,description) VALUES (?,?,?,?)",
            (user_id, item_name, quantity, description)
        )
        await db.commit()


async def get_requests(status: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if status:
            async with db.execute(
                "SELECT * FROM requests WHERE status=? ORDER BY created_at DESC", (status,)
            ) as cur:
                return await cur.fetchall()
        async with db.execute(
            "SELECT * FROM requests ORDER BY created_at DESC"
        ) as cur:
            return await cur.fetchall()


# ── Ko'ngillilar ──────────────────────────────────────────────────────────────

async def add_volunteer(user_id: int, skills: str, availability: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO volunteers (user_id,skills,availability) VALUES (?,?,?)",
            (user_id, skills, availability)
        )
        await db.commit()


async def get_all_volunteers():
    """Qaytaradi: (user_id, full_name, phone, skills, availability)"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT v.user_id, u.full_name, u.phone, v.skills, v.availability
            FROM volunteers v
            LEFT JOIN users u ON v.user_id = u.user_id
            ORDER BY v.registered_at DESC
        """) as cur:
            return await cur.fetchall()


# ── Statistika ────────────────────────────────────────────────────────────────

async def log_event(event_type: str, user_id: int = None, data: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO analytics (event_type,user_id,data) VALUES (?,?,?)",
            (event_type, user_id, data)
        )
        await db.commit()


async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        stats = {}
        async with db.execute("SELECT COUNT(*) FROM users WHERE is_active=1") as c:
            stats["total_users"] = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM donations") as c:
            stats["total_donations"] = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM donations WHERE status='pending'") as c:
            stats["pending_donations"] = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM requests") as c:
            stats["total_requests"] = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM requests WHERE status='pending'") as c:
            stats["pending_requests"] = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM volunteers") as c:
            stats["total_volunteers"] = (await c.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE DATE(joined_at)=DATE('now')"
        ) as c:
            stats["new_users_today"] = (await c.fetchone())[0]
        return stats
