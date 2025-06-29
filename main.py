import asyncio
import datetime
import aiohttp

from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetFullChannelRequest
from utils import translate_with_libretranslate

# === TELEGRAM CONFIGURATION ===
api_id = '--'
api_hash = '--'
phone_number = '--'
target_channel = "--"


# === INIT TELEGRAM CLIENT ===
client = TelegramClient('session_name', api_id, api_hash)


# ────────────────────────────────────────────
#  RADAR API HELPERS
# ────────────────────────────────────────────
SEARCH_URL    = "https://radar.squat.net/api/1.2/search/events.json"
EVENT_URL     = "https://radar.squat.net/api/1.2/event/{id}.json"
LOCATION_URL  = "https://radar.squat.net/api/1.2/location/{id}.json"

sent_event_ids   : set[str] = set()
location_cache   : dict[str, dict] = {}   # id → detail json

# ---------- primary search ----------
async def fetch_event_objects(session):
    today = datetime.date.today()
    params = {
        "search[date_after]": (today - datetime.timedelta(days=3)).isoformat(),
        "search[date_before]": (today + datetime.timedelta(days=30)).isoformat(),
        "search[limit]": 100,
    }

    async with session.get(SEARCH_URL, params=params) as resp:
        if resp.status != 200:
            print(f"[Radar] error: {resp.status}")
            return []

        data = await resp.json()
        result = data.get("result", {})
        return list(result.values())  # full event objects


# ---------- fetch event detail ----------
async def fetch_event_detail(session, eid: str) -> dict | None:
    url  = EVENT_URL.format(id=eid)
    resp = await session.get(url)
    if resp.status != 200:
        return None
    return await resp.json()

# ---------- fetch (and cache) location detail ----------
async def fetch_location_detail(session, lid: str) -> dict | None:
    if lid in location_cache:
        return location_cache[lid]
    resp = await session.get(LOCATION_URL.format(id=lid))
    if resp.status != 200:
        return None
    data = await resp.json()
    location_cache[lid] = data
    return data

# ---------- compose and send ----------
async def post_event_links(max_send=50):
    async with aiohttp.ClientSession() as session:
        events = await fetch_event_objects(session)
        print(f"[Radar] Fetch returned {len(events)} events.")

        sent = 0
        for ev in events:
            if sent >= max_send:
                break

            title = ev.get("title", "Untitled")
            date = ev.get("date_time", [{}])[0].get("time_start", "Unknown")
            city = ev.get("offline", [{}])[0].get("title", "Unknown").split()[-1]  # crude extract
            radar_url = ev.get("url")

            # location URI
            loc_uri = ev.get("offline", [{}])[0].get("uri")
            latlon = "Unknown"
            tz = "Unknown"

            if loc_uri:
                async with session.get(loc_uri + ".json") as loc_resp:
                    if loc_resp.status == 200:
                        loc = await loc_resp.json()
                        lat = loc.get("lat")
                        lon = loc.get("lon")
                        if lat and lon:
                            latlon = f"{lat},{lon}"
                        tz = loc.get("timezone", "Unknown")


            title = ev.get("title", "Untitled")
            categories = ev.get("category", [])

            print(f"[DEBUG] '{title}' → categories: {[cat.get('name') for cat in categories]}")
# category and country filter

            #filter for events that contain tag protest  \/
            protest_keywords = ["protest", "action", "demonstration", "march", "rally", "strike"] 
            is_protest = any(
                any(kw in cat.get("name", "").lower() for kw in protest_keywords)
                for cat in categories
            )
            if not is_protest:
                print(f"[skip] Not protest: {ev.get('title')}")
                continue

                

                                        #European countries filter \/
            EURO_COUNTRIES = {"AL","AD","AT","BE","BG","BY","CH","CY","CZ","DE","DK","EE",
                                "ES","FI","FR","GB","GR","HR","HU","IE","IS","IT","LI","LT",
                                "LU","LV","MC","MD","ME","MK","MT","NL","NO","PL","PT","RO",
                                "RS","SE","SI","SK","SM","UA","VA"}
    
    #filter for Europe
            country = (
                loc.get("country")                      # top-level (rare)
                or loc.get("address", {}).get("country")  # nested (common)
                or None
            )
            lat  = loc.get("lat")
            lon  = loc.get("lon")

            if country not in EURO_COUNTRIES:
                print(f"[skip] Not in Europe: {ev.get('title')} ({country})")
                continue


            msg = (
                f"📅 **Upcoming Event**\n\n"
                f"**Title:** {title}\n"
                f"**When:** {date}\n"
                f"**Where:** {city}\n"
                f"**Lat/Lon:** {latlon}\n"
                f"**Timezone:** {tz}\n\n"
                f"🔗 [View on Radar]({radar_url})"
            )

            print(f"[Radar] Sending: {title}")
            await client.send_message(target_channel, msg, parse_mode="markdown")
            sent += 1


# background loop
async def radar_poll_loop(interval=3600):
    while True:
        try:
            await post_event_links()
        except Exception as e:
            print("[Radar] error:", e)
        await asyncio.sleep(interval)

# ────────────────────────────────────────────
#  MAIN
# ────────────────────────────────────────────
async def main():
    await client.start(phone_number)
    print("✅ Telegram client ready.")

    # Kick-off Radar polling (hourly)
    asyncio.create_task(radar_poll_loop(3600))

    print("🎧 Listening & polling …")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())