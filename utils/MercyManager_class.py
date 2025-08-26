# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime
from config import DATABASE_PATH

# Règles de mercy pour stockage
MERCY_RULES = {
    "ancient": {"threshold": 200, "increment": 0.5, "base": 0},
    "void": {"threshold": 200, "increment": 0.5, "base": 0},
    "sacred": {"threshold": 12, "increment": 2, "base": 0},
    "primal_legendary": {"threshold": 75, "increment": 1, "base": 0},
    "primal_mythical": {"threshold": 200, "increment": 10, "base": 0},
    "remnant": {"threshold": 24, "increment": 1, "base": 0},
}

class MercyManager:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_table()

    def init_table(self):
        """Initialise la table des compteurs de mercy"""
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

    def get_pulls(self, user_id, shard_type):
        """Retourne le nombre de pulls actuels pour un utilisateur et un type de shard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pulls FROM mercy_counters WHERE user_id = ? AND shard_type = ?",
            (user_id, shard_type)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0

    def add_pulls(self, user_id, shard_type, pulls):
        """Ajoute des pulls pour un utilisateur en gérant correctement l'INSERT/UPDATE"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Vérifie si l'enregistrement existe
        cursor.execute(
            "SELECT pulls FROM mercy_counters WHERE user_id = ? AND shard_type = ?",
            (user_id, shard_type)
        )
        row = cursor.fetchone()

        if row:
            new_pulls = row[0] + pulls
            cursor.execute(
                "UPDATE mercy_counters SET pulls = ?, last_reset = ? WHERE user_id = ? AND shard_type = ?",
                (new_pulls, datetime.utcnow(), user_id, shard_type)
            )
        else:
            new_pulls = pulls
            cursor.execute(
                "INSERT INTO mercy_counters (user_id, shard_type, pulls, last_reset) VALUES (?, ?, ?, ?)",
                (user_id, shard_type, new_pulls, datetime.utcnow())
            )

        conn.commit()
        conn.close()
        return new_pulls

    def reset_pulls(self, user_id, shard_type):
        """Réinitialise les pulls d'un utilisateur pour un shard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE mercy_counters SET pulls = 0, last_reset = ? WHERE user_id = ? AND shard_type = ?",
            (datetime.utcnow(), user_id, shard_type)
        )
        conn.commit()
        conn.close()

    def get_all_pulls(self, user_id):
        """Retourne tous les pulls d'un utilisateur pour tous les shards"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT shard_type, pulls FROM mercy_counters WHERE user_id = ?",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return {shard_type: pulls for shard_type, pulls in rows}

    def get_mercy_chance(self, shard_type, pulls):
        """Calcule la probabilité de mercy selon le nombre de pulls"""
        rule = MERCY_RULES[shard_type]
        if pulls <= rule["threshold"]:
            return rule["base"]
        return rule["base"] + (pulls - rule["threshold"]) * rule["increment"]

    def pulls_until_guaranteed(self, shard_type, pulls):
        """Retourne combien de pulls restent avant un loot garanti"""
        rules = {
            "ancient": {"start": 200, "increment": 5, "base": 0.5},
            "void": {"start": 200, "increment": 5, "base": 0.5},
            "sacred": {"start": 12, "increment": 2, "base": 6},
            "primal_legendary": {"start": 75, "increment": 1, "base": 1},
            "primal_mythical": {"start": 200, "increment": 10, "base": 0.5},
            "remnant": {"start": 24, "increment": 1, "base": 0},
        }
        if shard_type not in rules:
            return None
        rule = rules[shard_type]
        guaranteed_pull = int(rule["start"] + (100 - rule["base"]) / rule["increment"])
        remaining = guaranteed_pull - pulls
        return remaining if remaining > 0 else 0
