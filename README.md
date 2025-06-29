# Radar Protest Bot 📡
This is a Python application that connects to the Radar.squat.net API, filters protest-related events happening in Europe, and sends structured updates about upcoming events to a Telegram channel using the Telethon library. Although it can be filtered for other locations, most events on the website are happening in Europe.

## 🚀 Quick start
### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/TelegramRadarSquat.git
cd RadarProtestBot
```
### 2️⃣ Install Python dependencies
✅ Create a virtual environment (recommended):

```bash
python -m venv .venv
Activate it:
```
```bash
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```
✅ Install required packages:

```bash
pip install -r requirements.txt
```

### 3️⃣ Set up Telegram configuration
Edit main.py and configure:

Your Telegram API credentials

Phone number

Target channel username or ID

Example snippet:

```python
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
phone_number = '+1234567890'
target_channel = 'your_target_channel_username_or_id'
```

### 4️⃣ Run the bot! 🏁
```bash
python radar_protest_bot.py
```

✅ The bot will:

* Connect to Telegram using your credentials

* Query the Radar API every hour

* Filter upcoming protest-related events in Europe

* Format and send those events to your target Telegram channel

⚡ Full Features
✅ Fetches protest events from radar.squat.net
✅ Filters by protest-related keywords (e.g. protest, action, strike)
✅ Filters for events in European countries only
✅ Grabs and formats city, coordinates, time, and timezone
✅ Sends structured messages to your Telegram channel
✅ Built with async and runs continuously in the background

### 🧠 Notes
* Radar API is public, but rate-limited—this script is optimized for hourly polling.

* This bot is read-only: it only pulls and sends public event information.

* You can easily modify the keyword list or geographic filter to suit other use cases.
