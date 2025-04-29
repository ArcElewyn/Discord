
# Discord Bot Setup Guide

This guide explains how to create, configure, and run a Discord bot that responds to commands in a specific channel and reads data from a Google Sheet.

---
## Step 1: Create Your Bot on Discord

1. **Go to the Discord Developer Portal**  
   Visit [Discord Developer Portal](https://discord.com/developers/applications).

2. **Create a New Application**  
   Click on **"New Application"** and give your bot a name (e.g., "MyBot").

3. **Add a Bot to the Application**  
   Once the application is created, click on **"Bot"** in the left menu and then click **"Add Bot"**.

4. **Copy the Authentication Token**  
   Under "TOKEN", click on **"Copy"** to copy your **token** (keep it safe and don't share it!).
   
---
## Step 2: Install Python Dependencies

If you don't have Python installed, download it here: [Python](https://www.python.org/downloads/).

Then, install the required libraries via pip:

```bash
pip install discord.py pandas gspread oauth2client
```

- `discord.py`: for interacting with the Discord API.
- `pandas`: for manipulating the Google Sheets data.
- `gspread` and `oauth2client`: for accessing Google Sheets (if your file is private).
---

## Step 5: Add Your Authorized Channel ID

- Replace `AUTHORIZED_CHANNEL_ID = 123456789012345678` with the ID of the channel where you want to allow the command.
- To get the channel ID, enable **Developer Mode** in Discord (User Settings > Advanced > Developer Mode), then **right-click** your channel and select **"Copy ID"**.

---
## Step 6: Obtain Your Google Sheet URL

1. If your Google Sheet is **public**: Go to your Google Sheets file, then click on **"File" > "Publish to the web"** and copy the URL.
2. If your Google Sheet is **private**, you will need to configure a **Google API key** and use it with `gspread` (this requires additional setup).

For a **public file**, the URL will look like this:  
`https://docs.google.com/spreadsheets/d/YOUR_FILE_ID/edit#gid=0`

Replace `"YOUR_GOOGLE_SHEET_URL"` with your actual URL in the code.

---
## Step 8: Run Your Bot

1. **Save your `bot.py` file** and make sure your Discord token is correct.
2. **Run the bot** using the following command in your terminal:

```bash
python bot.py
```

---
## Step 9: Invite the Bot to Your Server

1. Go to the Discord Developer Portal and in **"OAuth2"** -> **"URL Generator"**.
2. Check the required **permissions** like `bot` and `messages.read` to allow your bot to read and send messages.
3. Copy the generated URL and open it in your browser to invite your bot to your Discord server.

---
## Summary

- **The bot only responds** in a specific channel (using the channel ID).
- It **ignores** the command in other channels.
- It **reads data** from the **Google Sheet** only when the `!siege` command is called.
---
