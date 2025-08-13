# RTF Discord Bot - Personal Best Tracker

Un bot Discord pour tracker les Personal Best (PB) de votre guilde sur différents boss avec système de clans et gestion des difficultés.

## 🎮 Fonctionnalités

- **Multi-Boss Support** : Hydra (4 difficultés), Chimera (6 difficultés), Clan vs Clan
- **Système de Clans** : RTF, RTFC, RTFR avec classements séparés
- **Screenshots automatiques** : Stockage et affichage des preuves
- **Base de données SQLite** : Stockage persistant et performant
- **Suppression automatique** : Anciens screenshots supprimés lors de nouveaux records
- **Interface intuitive** : Commandes simples et embeds Discord

## 📋 Prérequis

### Logiciels requis
- **Python 3.9+**
- **Container Station** (QNAP) ou **Docker**
- **Discord Bot Token** ([Discord Developer Portal](https://discord.com/developers/applications))

### Dépendances Python
```
discord.py>=2.3.0
aiohttp>=3.8.0
```

## 🏗️ Structure des dossiers sur le NAS

Créez cette structure sur votre QNAP :

```
/share/Container/discord-bot/
├── bot.py                          # Script principal du bot
├── requirements.txt                # Dépendances Python
├── .env                           # Variables d'environnement
├── docker-compose.yml             # Configuration Docker
├── bot_data.db                    # Base SQLite (créée automatiquement)
├── logs/                          # Logs du bot (optionnel)
└── screenshots/                   # Screenshots des PB
    ├── hydra/
    │   ├── normal/
    │   ├── hard/
    │   ├── brutal/
    │   └── nightmare/
    ├── chimera/
    │   ├── easy/
    │   ├── normal/
    │   ├── hard/
    │   ├── brutal/
    │   ├── nightmare/
    │   └── ultra/
    └── cvc/
```

## 🐳 Installation Docker (Recommandée)

### 1. Créer le fichier `requirements.txt`
```txt
discord.py>=2.3.0
aiohttp>=3.8.0
python-dotenv>=1.0.0
```

### 2. Créer le fichier `.env`
```env
DISCORD_TOKEN=your_bot_token_here
AUTHORIZED_CHANNEL_ID=your_channel_id_here
```

### 3. Créer le `Dockerfile`
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de configuration
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY bot.py .

# Créer les dossiers nécessaires
RUN mkdir -p screenshots/hydra/normal screenshots/hydra/hard screenshots/hydra/brutal screenshots/hydra/nightmare \
    screenshots/chimera/easy screenshots/chimera/normal screenshots/chimera/hard screenshots/chimera/brutal screenshots/chimera/nightmare screenshots/chimera/ultra \
    screenshots/cvc

# Variables d'environnement
ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
```

### 4. Créer le `docker-compose.yml`
```yaml
version: '3.8'

services:
  discord-bot:
    build: .
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./screenshots:/app/screenshots
      - ./bot_data.db:/app/bot_data.db
      - ./logs:/app/logs
    environment:
      - TZ=Europe/Paris
    container_name: rtf-discord-bot
    
    # Optionnel: Limits des ressources
    deploy:
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M
```

## ⚙️ Configuration

### 1. Obtenir le Token Discord
1. Aller sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Créer une nouvelle Application
3. Dans "Bot" → "Token" → Copier le token
4. Dans "Bot" → "Privileged Gateway Intents" → Activer "Message Content Intent"

### 2. Obtenir l'ID du Channel
1. Dans Discord, activer le Mode Développeur (Paramètres → Avancé)
2. Clic droit sur votre channel → "Copier l'identifiant"

### 3. Inviter le bot sur votre serveur
Générez une URL d'invitation avec ces permissions :
- Send Messages
- Read Message History
- Attach Files
- Use External Emojis
- Add Reactions

URL : `https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=378944&scope=bot`

## 🚀 Déploiement sur QNAP

### Via Container Station (Recommandé)

1. **Installer Container Station** via App Center
2. **Créer le dossier** `/share/Container/discord-bot/`
3. **Copier tous les fichiers** dans ce dossier
4. **Modifier le fichier `.env`** avec vos tokens
5. **Container Station** → "Create" → "Create Application via docker-compose"
6. **Sélectionner** votre `docker-compose.yml`
7. **Démarrer** le container

### Via SSH (Alternative)

```bash
# Se connecter au QNAP
ssh admin@IP_DE_VOTRE_QNAP

# Naviguer vers le dossier
cd /share/Container/discord-bot/

# Installer les dépendances (si Python est installé)
pip3 install -r requirements.txt

# Lancer le bot (test)
python3 bot.py

# Créer un service auto-start
# Via Interface QNAP : Panneau de contrôle → Applications → Autorun
# Ajouter : cd /share/Container/discord-bot && python3 bot.py &
```

## 📊 Base de données SQLite

### Structure automatique
Le bot crée automatiquement les tables nécessaires :

- **Table `users`** : PB de tous les boss et difficultés
- **Table `pb_history`** : Historique complet des records

### Colonnes principales
```sql
-- Hydra
pb_hydra_normal, pb_hydra_normal_screenshot, pb_hydra_normal_date
pb_hydra_hard, pb_hydra_hard_screenshot, pb_hydra_hard_date
pb_hydra_brutal, pb_hydra_brutal_screenshot, pb_hydra_brutal_date
pb_hydra_nightmare, pb_hydra_nightmare_screenshot, pb_hydra_nightmare_date

-- Chimera (6 difficultés similaires)
pb_chimera_easy, pb_chimera_normal, pb_chimera_hard, 
pb_chimera_brutal, pb_chimera_nightmare, pb_chimera_ultra

-- CvC
pb_cvc, pb_cvc_screenshot, pb_cvc_date
```

## 🎯 Utilisation des commandes

### Soumettre un PB
```
!pbhydra brutal 1500000    (+ screenshot attachée)
!pbchimera ultra 2000000   (+ screenshot attachée)
!pbcvc 1800000             (+ screenshot attachée)
```

### Voir des PB
```
!pbhydra nightmare         (votre PB)
!pbchimera easy Alice      (PB d'Alice)
!mystats                   (tous vos PB)
```

### Classements
```
!top10hydra brutal         (global)
!rtfhydra nightmare        (clan RTF)
!rtfcchimera ultra         (clan RTFC)
```

## 🔧 Maintenance

### Logs
```bash
# Via Docker
docker logs rtf-discord-bot

# Via Container Station
Container Station → Votre container → Logs
```

### Sauvegarde
```bash
# Sauvegarder la base de données
cp bot_data.db bot_data_backup_$(date +%Y%m%d).db

# Sauvegarder les screenshots
tar -czf screenshots_backup_$(date +%Y%m%d).tar.gz screenshots/
```

### Nettoyage
Les anciens screenshots sont **automatiquement supprimés** quand un nouveau PB est établi.

## 🛠️ Résolution de problèmes

### Le bot ne répond pas
- Vérifier que le `AUTHORIZED_CHANNEL_ID` est correct
- Vérifier que le bot a les bonnes permissions
- Consulter les logs pour les erreurs

### Screenshots non sauvegardées
- Vérifier les permissions du dossier `screenshots/`
- S'assurer que l'image est dans un format supporté (PNG, JPG, etc.)

### Erreurs de base de données
- Vérifier les permissions en écriture sur `bot_data.db`
- En cas de corruption : supprimer le fichier (il sera recréé)

## 📈 Performances

### Optimisation pour 50+ utilisateurs
- **SQLite** : Parfait jusqu'à 100+ utilisateurs simultanés
- **Screenshots** : ~2MB par image, nettoyage automatique
- **RAM** : ~128MB en utilisation normale
- **CPU** : Minimal (événements Discord uniquement)

## 🔒 Sécurité

- Token Discord dans `.env` (jamais dans le code)
- Bot limité à un seul channel
- Pas d'accès SSH ou système depuis le bot
- Screenshots stockées localement (contrôle total)

## 📝 Notes importantes

1. **Clans détectés automatiquement** : `[RTF] Username` ou `[RTF]Username`
2. **Anciens screenshots supprimés** automatiquement lors de nouveaux PB
3. **Classements vides** affichent un message informatif
4. **Format des dates** : MM/DD/YYYY at HH:MM AM/PM
5. **Émojis modifiables** dans `BOSS_CONFIG` et `CLAN_CONFIG`

## 🚀 Extensions possibles

- Ajout de nouveaux boss
- Statistiques avancées (moyennes, progressions)
- Export des données en Excel
- Interface web pour visualiser les stats
- Notifications automatiques de nouveaux records

---

**Développé pour la communauté RTF** 🎮
