# -*- coding: utf-8 -*-
from config import DATABASE_PATH
import sqlite3, os

class DatabaseManager:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données avec les nouvelles colonnes pour les difficultés"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table principale avec toutes les difficultés
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_username TEXT UNIQUE,
            
            -- Hydra difficulties
            pb_hydra_normal INTEGER DEFAULT 0,
            pb_hydra_normal_screenshot TEXT,
            pb_hydra_normal_date TIMESTAMP,
            pb_hydra_hard INTEGER DEFAULT 0,
            pb_hydra_hard_screenshot TEXT,
            pb_hydra_hard_date TIMESTAMP,
            pb_hydra_brutal INTEGER DEFAULT 0,
            pb_hydra_brutal_screenshot TEXT,
            pb_hydra_brutal_date TIMESTAMP,
            pb_hydra_nightmare INTEGER DEFAULT 0,
            pb_hydra_nightmare_screenshot TEXT,
            pb_hydra_nightmare_date TIMESTAMP,
            
            -- Chimera difficulties
            pb_chimera_easy INTEGER DEFAULT 0,
            pb_chimera_easy_screenshot TEXT,
            pb_chimera_easy_date TIMESTAMP,
            pb_chimera_normal INTEGER DEFAULT 0,
            pb_chimera_normal_screenshot TEXT,
            pb_chimera_normal_date TIMESTAMP,
            pb_chimera_hard INTEGER DEFAULT 0,
            pb_chimera_hard_screenshot TEXT,
            pb_chimera_hard_date TIMESTAMP,
            pb_chimera_brutal INTEGER DEFAULT 0,
            pb_chimera_brutal_screenshot TEXT,
            pb_chimera_brutal_date TIMESTAMP,
            pb_chimera_nightmare INTEGER DEFAULT 0,
            pb_chimera_nightmare_screenshot TEXT,
            pb_chimera_nightmare_date TIMESTAMP,
            pb_chimera_ultra INTEGER DEFAULT 0,
            pb_chimera_ultra_screenshot TEXT,
            pb_chimera_ultra_date TIMESTAMP,
            
            -- CvC (inchangé)
            pb_cvc INTEGER DEFAULT 0,
            pb_cvc_screenshot TEXT,
            pb_cvc_date TIMESTAMP,
            
            total_attempts INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table pour l'historique global
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pb_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            boss_type TEXT,
            difficulty TEXT,
            damage INTEGER,
            screenshot_filename TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_pb(self, username, boss_type, difficulty=None):
        """Récupère le PB d'un utilisateur pour un boss et difficulté spécifique"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if difficulty:
            column_prefix = f"pb_{boss_type}_{difficulty}"
        else:
            column_prefix = f"pb_{boss_type}"
            
        cursor.execute(
            f"SELECT {column_prefix}, {column_prefix}_screenshot, {column_prefix}_date FROM users WHERE discord_username = ?",
            (username.lower(),)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result if result else (0, None, None)
    
    def update_user_pb(self, username, boss_type, damage, screenshot_filename, difficulty=None):
        """Met à jour le PB d'un utilisateur et supprime l'ancien screenshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupérer l'ancien screenshot pour le supprimer
        old_data = self.get_user_pb(username, boss_type, difficulty)
        old_screenshot = old_data[1] if old_data else None
        
        if difficulty:
            column_prefix = f"pb_{boss_type}_{difficulty}"
        else:
            column_prefix = f"pb_{boss_type}"
        
        # Créer l'utilisateur s'il n'existe pas, sinon mettre à jour
        cursor.execute(f'''
        INSERT INTO users (discord_username, {column_prefix}, {column_prefix}_screenshot, {column_prefix}_date, total_attempts)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
        ON CONFLICT(discord_username) 
        DO UPDATE SET 
            {column_prefix} = ?,
            {column_prefix}_screenshot = ?,
            {column_prefix}_date = CURRENT_TIMESTAMP,
            total_attempts = total_attempts + 1
        ''', (username.lower(), damage, screenshot_filename, damage, screenshot_filename))
        
        # Ajouter à l'historique
        cursor.execute('''
        INSERT INTO pb_history (username, boss_type, difficulty, damage, screenshot_filename)
        VALUES (?, ?, ?, ?, ?)
        ''', (username.lower(), boss_type, difficulty or 'none', damage, screenshot_filename))
        
        conn.commit()
        conn.close()
        
        return old_screenshot
    
    def get_leaderboard(self, boss_type, difficulty=None, limit=10, clan=None):
        """Récupère le classement pour un boss et difficulté spécifique"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if difficulty:
            column_prefix = f"pb_{boss_type}_{difficulty}"
        else:
            column_prefix = f"pb_{boss_type}"
        
        base_query = f'''
        SELECT discord_username, {column_prefix}, {column_prefix}_date 
        FROM users 
        WHERE {column_prefix} > 0
        '''
        
        if clan:
            base_query += ''' AND (
                discord_username LIKE '[''' + clan + '''] %' OR
                discord_username LIKE '[''' + clan + ''']%'
            )'''
        
        base_query += f' ORDER BY {column_prefix} DESC LIMIT ?'
        
        cursor.execute(base_query, (limit,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_user_all_pbs(self, username):
        """Récupère tous les PB d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupérer toutes les colonnes de PB
        cursor.execute('SELECT * FROM users WHERE discord_username = ?', (username.lower(),))
        result = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        if not result:
            return None
        
        return dict(zip(columns, result))
