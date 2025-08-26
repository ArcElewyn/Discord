# -*- coding: utf-8 -*-
import sqlite3, os
import aiohttp
from datetime import datetime
from config import SCREENSHOTS_BASE_PATH, BOSS_CONFIG

class ScreenshotManager:
    def __init__(self, base_path=SCREENSHOTS_BASE_PATH):
        self.base_path = base_path
        # Créer les dossiers pour chaque boss et difficulté
        for boss_type in BOSS_CONFIG.keys():
            boss_path = os.path.join(base_path, boss_type)
            os.makedirs(boss_path, exist_ok=True)
            
            # Créer sous-dossiers pour les difficultés
            for difficulty in BOSS_CONFIG[boss_type]['difficulties']:
                difficulty_path = os.path.join(boss_path, difficulty)
                os.makedirs(difficulty_path, exist_ok=True)
    
    async def save_screenshot(self, attachment, username, damage, boss_type, difficulty=None):
        """Sauvegarde le screenshot localement"""
        try:
            timestamp = int(datetime.now().timestamp())
            file_extension = attachment.filename.split('.')[-1].lower()
            filename = f"{username.lower()}_{damage}_{timestamp}.{file_extension}"
            
            if difficulty:
                boss_path = os.path.join(self.base_path, boss_type, difficulty)
            else:
                boss_path = os.path.join(self.base_path, boss_type)
            
            filepath = os.path.join(boss_path, filename)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status == 200:
                        # Ouverture en binaire, pas de problème d'encodage
                        with open(filepath, 'wb') as f:
                            f.write(await resp.read())
                        return filename
            return None
            
        except Exception as e:
            print(f"Erreur sauvegarde screenshot: {str(e)}")
            return None
    
    def get_screenshot_path(self, filename, boss_type, difficulty=None):
        """Retourne le chemin complet du screenshot"""
        if filename:
            if difficulty:
                return os.path.join(self.base_path, boss_type, difficulty, filename)
            else:
                return os.path.join(self.base_path, boss_type, filename)
        return None
    
    def delete_old_screenshot(self, filename, boss_type, difficulty=None):
        """Supprime l'ancien screenshot"""
        if filename:
            old_path = self.get_screenshot_path(filename, boss_type, difficulty)
            if old_path and os.path.exists(old_path):
                try:
                    os.remove(old_path)
                    print(f"Ancien screenshot supprimé: {filename}")
                except Exception as e:
                    print(f"Erreur suppression screenshot: {str(e)}")
