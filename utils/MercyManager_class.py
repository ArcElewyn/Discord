# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime
from config import DATABASE_PATH


# Règles 100% centralisées
MERCY_RULES = {
    # threshold = point où la mercy commence
    # increment = % ajouté par pull
    # base = % avant threshold

    "ancient":          {"threshold": 200, "increment": 0.5,  "base": 0},
    "void":             {"threshold": 200, "increment": 0.5,  "base": 0},
    "sacred":           {"threshold": 12,  "increment": 2,    "base": 0},
    "remnant":          {"threshold": 24,  "increment": 1,    "base": 0},

    # Primal split
    "primal_legendary": {"threshold": 75,  "increment": 1,    "base": 0},
    "primal_mythical":  {"threshold": 200, "increment": 10,   "base": 0},
}


# Règles guaranteed
GUARANTEED_RULES = {
    "ancient":          {"start": 200, "increment": 5,  "base": 0.5},
    "void":             {"start": 200, "increment": 5,  "base": 0.5},
    "sacred":           {"start": 12,  "increment": 2,  "base": 6},
    "remnant":          {"start": 24,  "increment": 1,  "base": 0},

    "primal_legendary": {"start": 75,  "increment": 1,  "base": 1},
    "primal_mythical":  {"start": 200, "increment": 10, "base": 0.5},
}


class MercyManager:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        """Initialise la table des compteurs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mercy_counters (
                user_id TEXT,
                shard_type TEXT,
                pulls INTEGER DEFAULT 0,
                last_reset TIMESTAMP,
                PRIMARY KEY(user_id, shard_type)
            )
        """)
        conn.commit()
        conn.close()

    # ------------------------------
    # Basic database helpers
    # ------------------------------

    def get_pulls(self, user_id, shard_type):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""SELECT pulls FROM mercy_counters 
                       WHERE user_id = ? AND shard_type = ?""",
                    (user_id, shard_type))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else 0

    def add_pulls(self, user_id, shard_type, pulls):
        old = self.get_pulls(user_id, shard_type)
        new = old + pulls

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO mercy_counters (user_id, shard_type, pulls, last_reset)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, shard_type)
            DO UPDATE SET pulls = excluded.pulls, last_reset = excluded.last_reset
        """, (user_id, shard_type, new, datetime.utcnow()))
        conn.commit()
        conn.close()

        return new

    def reset_pulls(self, user_id, shard_type):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            UPDATE mercy_counters 
            SET pulls = 0, last_reset = ? 
            WHERE user_id = ? AND shard_type = ?
        """, (datetime.utcnow(), user_id, shard_type))
        conn.commit()
        conn.close()

    def get_all_pulls(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""SELECT shard_type, pulls 
                       FROM mercy_counters WHERE user_id = ?""", (user_id,))
        rows = dict(cur.fetchall())
        conn.close()
        return rows

    # ------------------------------
    # Mercy logic
    # ------------------------------

    def get_chance(self, shard_type, pulls):
        rule = MERCY_RULES[shard_type]
        if pulls <= rule["threshold"]:
            return rule["base"]

        return rule["base"] + (pulls - rule["threshold"]) * rule["increment"]

    def get_remaining(self, shard_type, pulls):
        rule = GUARANTEED_RULES[shard_type]
        guaranteed_at = int(rule["start"] + (100 - rule["base"]) / rule["increment"])
        remaining = guaranteed_at - pulls
        return max(remaining, 0)

    def get_display_info(self, shard_type, pulls):
        chance = self.get_chance(shard_type, pulls)
        remaining = self.get_remaining(shard_type, pulls)
        guaranteed_at = pulls + remaining
        return chance, guaranteed_at, remaining
