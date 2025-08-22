# RTF Discord Bot - Personal Best Tracker

A Discord Bot to track Personal Best (PB) for each clan boss  

## 🎮 Features

- **Multi-Boss Support** : Hydra (4 difficulties), Chimera (6 difficulties), Clan vs Clan
- **Cluster support** : RTF, RTFC, RTFR with split leaderboards
- **Saves Screenshots** : Storage and display of proof 
- **SQLite Databse** : Persistent and efficient storage
- **Automatic Cleanupe** : Old screenshots deleted when new records are set
- **User-Friendly Interface** : Simple commands and Discord embeds

## 📋 Requirements

### Softwares required
- **Python 3.9+**
- **Container Station** (QNAP) or **Docker**
- **Discord Bot Token** ([Discord Developer Portal](https://discord.com/developers/applications))

### Python dependencies
```
discord.py>=2.3.0
aiohttp>=3.8.0
```

## 🏗️Nas Folder Structure

Create the following structure on your QNAP:

```
/share/Container/discord-bot/
├── bot.py                  # Script principal minimal
├── config.py               # Variables centrales (token, channel ID)
├── requirements.txt        # Dépendances Python
├── .env                    # Tokens, IDs de channel
├── docker-compose.yml
├── bot_data.db             # SQLite DB
├── cogs/                   # Toutes les commandes du bot
│   ├── guide.py            # Commande !guide
│   ├── pbhydra.py          # Commandes PB Hydra
│   ├── pbchimera.py        # Commandes PB Chimera
│   ├── pbcvc.py            # Commandes PB CvC
│   ├── top10.py            # Classements globaux
│   └── mystats.py          # Commande !mystats
├── utils/                  # Fonctions utilitaires partagées
│   ├── DatabaseManager_class.py         # Gestion DB SQLite
│   ├── ScreenshotManager_class.py       # Gestion des screenshots
│   ├── leaderboard_handler.py       # Gestion tableau de score
│   ├── pbhandler.py       # Gestion des pbs
│   └── helpers.py          # Fonctions génériques (ex: channel autorisé)
├── logs/                   # Logs du bot (optionnel)
└── screenshots/            # Screenshots organisés par boss/difficulté
    ├── hydra/
    ├── chimera/
    └── cvc/
```

## 🐳 Docker Installation (Recommended)

### 1. Create `requirements.txt`
```txt
discord.py>=2.3.0
aiohttp>=3.8.0
python-dotenv>=1.0.0
```

### 2. Create  `.env`
```env
DISCORD_TOKEN=your_bot_token_here
AUTHORIZED_CHANNEL_ID=your_channel_id_here
```

### 3. Create `Dockerfile`
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY bot.py .

# Create required folders
RUN mkdir -p screenshots/hydra/normal screenshots/hydra/hard screenshots/hydra/brutal screenshots/hydra/nightmare \
    screenshots/chimera/easy screenshots/chimera/normal screenshots/chimera/hard screenshots/chimera/brutal screenshots/chimera/nightmare screenshots/chimera/ultra \
    screenshots/cvc

# Environment variables
ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
```

### 4. Create `docker-compose.yml`
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
    
    # Optional: Resource limits
    deploy:
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M
```

## ⚙️ Configuration

1. Get Discord Token
Go to Discord Developer Portal (https://discord.com/developers/applications)

Create a new Application

In "Bot" → "Token" → Copy token

In "Bot" → "Privileged Gateway Intents" → Enable "Message Content Intent"

2. Get Channel ID
Enable Developer Mode in Discord (Settings → Advanced)

Right-click your channel → "Copy ID"

3. Invite the Bot to Your Server
Generate an invitation URL with these permissions:

Send Messages

Read Message History

Attach Files

Use External Emojis

Add Reactions

URL : `https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=378944&scope=bot`

## 🚀 Déploiement sur QNAP

### Via Container Station (Recommandé)

1. Install Container Station via App Center
2. Create /share/Container/discord-bot/
3. Copy all files into this folder
4. Edit .env with your tokens
5. Container Station → "Create" → "Create Application via docker-compose"
6. Select your docker-compose.yml
7. Start the container

### Via SSH (Alternative)

```bash
# Connect to QNAP
ssh admin@YOUR_QNAP_IP

# Navigate to folder
cd /share/Container/discord-bot/

# Install dependencies (if Python is installed)
pip3 install -r requirements.txt

# Test run
python3 bot.py

# Create auto-start service via QNAP interface
# Control Panel → Applications → Autorun
# Add: cd /share/Container/discord-bot && python3 bot.py &
```

## 📊 SQLite Database

**Automatic Structure**
The bot automatically creates the necessary tables:
 
- Table users: PBs for all bosses and difficulties
- Table pb_history: Complete record history

### Main columns
```sql
-- Hydra
pb_hydra_normal, pb_hydra_normal_screenshot, pb_hydra_normal_date
pb_hydra_hard, pb_hydra_hard_screenshot, pb_hydra_hard_date
pb_hydra_brutal, pb_hydra_brutal_screenshot, pb_hydra_brutal_date
pb_hydra_nightmare, pb_hydra_nightmare_screenshot, pb_hydra_nightmare_date

-- Chimera (6 similar difficulties)
pb_chimera_easy, pb_chimera_normal, pb_chimera_hard, 
pb_chimera_brutal, pb_chimera_nightmare, pb_chimera_ultra

-- CvC
pb_cvc, pb_cvc_screenshot, pb_cvc_date
```

## 🎯 Commands Usage

### Submit a PB
```
!pbhydra brutal 1500000    (+ attached screenshot)
!pbchimera ultra 2000000   (+ attached screenshot)
!pbcvc 1800000             (+ attached screenshot)
```

### View PBs
```
!pbhydra nightmare         (your PB)
!pbchimera easy Alice      (Alice's PB)
!mystats                   (all your PBs)
```

### Leaderboards
```
!top10hydra brutal         (global)
!rtfhydra nightmare        (for RTF)
!rtfcchimera ultra         (for RTFC)
```

## 🔧 Maintenance

### Logs
```bash
# Via Docker
docker logs rtf-discord-bot

# Via Container Station
Container Station → Your container → Logs
```

### Backup
```bash
# Backup database
cp bot_data.db bot_data_backup_$(date +%Y%m%d).db

# Backup screenshots
tar -czf screenshots_backup_$(date +%Y%m%d).tar.gz screenshots/

```

### Cleanup
Old screenshots are automatically deleted when a new PB is set.

## 🛠️ Troubleshooting

### Bot not responding
- Check AUTHORIZED_CHANNEL_ID
- Check bot permissions
- Consult logs for errors

### Screenshots Not Saved
- Check screenshots/ folder permissions
- Ensure image format is supported (PNG, JPG, etc.)

### Database errors
- Check write permissions on bot_data.db
- If corrupted: delete the file (it will be recreated)

## 📈 Performance

### Optimized for 50+ Users
- SQLite: Works well up to 100+ concurrent users
- Screenshots: ~2MB per image, auto cleanup
- RAM: ~128MB normal usage
- CPU: Minimal (Discord events only)

## 🔒 Security

- Discord token in .env (never in code)
- Bot limited to a single channel
- No SSH or system access from bot
- Screenshots stored locally (full control)

## 📝 Important Notes

- Clans detected automatically: [RTF] Username or [RTF]Username
- Old screenshots deleted automatically on new PB
- Empty leaderboards show an informative message
- Date format: MM/DD/YYYY at HH:MM AM/PM
- Emojis editable in BOSS_CONFIG and CLAN_CONFIG

## 🚀 Possible Extensions
- Add new bosses
- Advanced statistics (averages, progression)
- Export data to Excel
- Web interface to view stats
- Automatic notifications for new records
---

**Developed for the RTF community By Elewyn** 🎮
