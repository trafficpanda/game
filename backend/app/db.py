import aiosqlite
from typing import List, Optional

from .config import DB_PATH
from .models import User
from .rating import level_from_xp, rank_name_from_level

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    coins INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    hourly_income INTEGER DEFAULT 10,
    level INTEGER DEFAULT 1,
    rank_name TEXT DEFAULT 'Новичок',
    referred_by INTEGER
);
"""

CREATE_COURSE_PROGRESS_TABLE = """
CREATE TABLE IF NOT EXISTS course_progress (
    user_id INTEGER,
    step_id TEXT,
    is_completed INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, step_id)
);
"""

CREATE_REFERRALS_TABLE = """
CREATE TABLE IF NOT EXISTS referrals (
    inviter_id INTEGER,
    invited_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_PANDA_PURCHASES_TABLE = """
CREATE TABLE IF NOT EXISTS panda_purchases (
    user_id INTEGER,
    panda_id TEXT,
    PRIMARY KEY (user_id, panda_id)
);
"""

CREATE_USER_ACHIEVEMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS user_achievements (
    user_id INTEGER,
    achievement_id TEXT,
    earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, achievement_id)
);
"""

CREATE_STAR_PURCHASES_TABLE = """
CREATE TABLE IF NOT EXISTS star_purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    payload TEXT,
    amount INTEGER,
    product_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_USERS_TABLE)
        await db.execute(CREATE_COURSE_PROGRESS_TABLE)
        await db.execute(CREATE_REFERRALS_TABLE)
        await db.execute(CREATE_PANDA_PURCHASES_TABLE)
        await db.execute(CREATE_USER_ACHIEVEMENTS_TABLE)
        await db.execute(CREATE_STAR_PURCHASES_TABLE)
        await db.commit()


async def get_user(user_id: int, username: Optional[str] = None) -> User:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id, username, coins, xp, hourly_income, level, rank_name, referred_by "
            "FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        if row:
            return User(*row)

        level = 1
        rank_name = rank_name_from_level(level)
        hourly_income = 10
        await db.execute(
            "INSERT INTO users (user_id, username, coins, xp, hourly_income, level, rank_name) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, username, 0, 0, hourly_income, level, rank_name),
        )
        await db.commit()
        return User(
            user_id=user_id,
            username=username,
            coins=0,
            xp=0,
            hourly_income=hourly_income,
            level=level,
            rank_name=rank_name,
            referred_by=None,
        )


async def update_user(user: User):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET coins=?, xp=?, hourly_income=?, level=?, rank_name=? WHERE user_id=?",
            (user.coins, user.xp, user.hourly_income, user.level, user.rank_name, user.user_id),
        )
        await db.commit()


async def set_user_referred_by(user_id: int, inviter_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET referred_by=? WHERE user_id=?",
            (inviter_id, user_id),
        )
        await db.commit()


async def add_referral(inviter_id: int, invited_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO referrals (inviter_id, invited_id) VALUES (?, ?)",
            (inviter_id, invited_id),
        )
        await db.commit()


async def get_referrals_count(inviter_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM referrals WHERE inviter_id=?",
            (inviter_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row else 0


async def mark_step_completed(user_id: int, step_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO course_progress (user_id, step_id, is_completed) "
            "VALUES (?, ?, 1)",
            (user_id, step_id),
        )
        await db.commit()


async def is_step_completed(user_id: int, step_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT is_completed FROM course_progress WHERE user_id=? AND step_id=?",
            (user_id, step_id),
        )
        row = await cursor.fetchone()
        return bool(row and row[0])


async def get_completed_steps(user_id: int) -> List[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT step_id FROM course_progress WHERE user_id=? AND is_completed=1",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [r[0] for r in rows]


async def get_all_users() -> List[User]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id, username, coins, xp, hourly_income, level, rank_name, referred_by FROM users"
        )
        rows = await cursor.fetchall()
    return [User(*row) for row in rows]


async def add_panda_purchase(user_id: int, panda_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO panda_purchases (user_id, panda_id) VALUES (?, ?)",
            (user_id, panda_id),
        )
        await db.commit()


async def user_has_panda(user_id: int, panda_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM panda_purchases WHERE user_id=? AND panda_id=?",
            (user_id, panda_id),
        )
        row = await cursor.fetchone()
        return row is not None


async def get_user_pandas(user_id: int) -> List[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT panda_id FROM panda_purchases WHERE user_id=?",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [r[0] for r in rows]


async def add_user_achievement(user_id: int, achievement_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO user_achievements (user_id, achievement_id) VALUES (?, ?)",
            (user_id, achievement_id),
        )
        await db.commit()


async def get_user_achievements(user_id: int) -> List[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT achievement_id FROM user_achievements WHERE user_id=?",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [r[0] for r in rows]


async def add_star_purchase(user_id: int, payload: str, amount: int, product_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO star_purchases (user_id, payload, amount, product_id) VALUES (?, ?, ?, ?)",
            (user_id, payload, amount, product_id),
        )
        await db.commit()
