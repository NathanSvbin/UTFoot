import curl_cffi.requests as tls_requests
from flask import Flask, jsonify, request
from playwright.async_api import async_playwright
import asyncio
import time
import random
import os

FOTMOB_API = "https://www.fotmob.com/api"
BROWSERLESS_API_KEY = os.environ.get("BROWSERLESS_API_KEY", "2UHKzQuYjr0lWAuf349e3f7b275e99504e0ce026b44123f0d")
LOGGER = print

# --- Scraper curl_cffi (matches, team, league) ---
class FotMobScraper:
    def __init__(self):
        self.session = self._init_session()

    def _init_session(self):
        session = tls_requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*'
        })
        return session

    def _get(self, url):
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            LOGGER(f"❌ Erreur: {e}")
            return {}

    def get_daily_schedule(self, date_str):
        return self._get(f"{FOTMOB_API}/data/matches?date={date_str}&timezone=Europe%2FParis&ccode3=FRA")

    def get_team(self, team_id, tab="overview"):
        return self._get(f"{FOTMOB_API}/data/teams?id={team_id}&tab={tab}&type=team&timeZone=Europe/Paris")

    def get_league(self, league_id, tab="table"):
        return self._get(f"{FOTMOB_API}/data/leagues?id={league_id}&tab={tab}&type=league&timeZone=Europe/Paris")


# --- Scraper Playwright via Browserless (matchDetails, playerData) ---
async def get_match_browserless(match_id):
    ws_url = f"wss://chrome.browserless.io?token={BROWSERLESS_API_KEY}"
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(ws_url)
        context = await browser.new_context()
        page = await context.new_page()

        result = {}

        async def handle_response(response):
            if "matchDetails" in response.url and str(match_id) in response.url:
                try:
                    result['data'] = await response.json()
                except:
                    pass

        page.on("response", handle_response)
        await page.goto(
            f"https://www.fotmob.com/fr/matches/x/x#{match_id}",
            wait_until="domcontentloaded",
            timeout=60000
        )
        await page.wait_for_timeout(5000)
        await browser.close()
        return result.get('data')


async def get_player_browserless(player_id):
    ws_url = f"wss://chrome.browserless.io?token={BROWSERLESS_API_KEY}"
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(ws_url)
        context = await browser.new_context()
        page = await context.new_page()

        result = {}

        async def handle_response(response):
            if "data/playerData" in response.url and str(player_id) in response.url:
                if response.status == 200:
                    try:
                        result['data'] = await response.json()
                    except:
                        pass

        page.on("response", handle_response)
        await page.goto(
            f"https://www.fotmob.com/fr/players/{player_id}/x",
            wait_until="domcontentloaded",
            timeout=60000
        )
        await page.wait_for_timeout(5000)
        await browser.close()
        return result.get('data')


# --- Flask ---
app = Flask(__name__)
bot = FotMobScraper()

@app.route('/')
def home():
    return jsonify({"status": "online"})

@app.route('/api/matches', methods=['GET'])
def get_matches():
    date = request.args.get('date')
    if not date or not date.isdigit() or len(date) != 8:
        return jsonify({"error": "Format requis : ?date=YYYYMMDD"}), 400
    time.sleep(random.uniform(1.0, 3.0))
    data = bot.get_daily_schedule(date)
    if not data:
        return jsonify({"error": "Échec récupération"}), 404
    return jsonify(data), 200

@app.route('/api/team', methods=['GET'])
def get_team():
    team_id = request.args.get('id')
    tab = request.args.get('tab', 'overview')
    if not team_id:
        return jsonify({"error": "Paramètre manquant : ?id=9825"}), 400
    time.sleep(random.uniform(1.0, 3.0))
    data = bot.get_team(team_id, tab)
    if not data:
        return jsonify({"error": "Échec récupération"}), 404
    return jsonify(data), 200

@app.route('/api/league', methods=['GET'])
def get_league():
    league_id = request.args.get('id')
    tab = request.args.get('tab', 'table')
    if not league_id:
        return jsonify({"error": "Paramètre manquant : ?id=54"}), 400
    time.sleep(random.uniform(1.0, 3.0))
    data = bot.get_league(league_id, tab)
    if not data:
        return jsonify({"error": "Échec récupération"}), 404
    return jsonify(data), 200

@app.route('/api/match', methods=['GET'])
def get_match():
    match_id = request.args.get('id')
    if not match_id:
        return jsonify({"error": "Paramètre manquant : ?id=5205795"}), 400
    data = asyncio.run(get_match_browserless(match_id))
    if not data:
        return jsonify({"error": "Échec récupération"}), 404
    return jsonify(data), 200

@app.route('/api/player', methods=['GET'])
def get_player():
    player_id = request.args.get('id')
    if not player_id:
        return jsonify({"error": "Paramètre manquant : ?id=693171"}), 400
    data = asyncio.run(get_player_browserless(player_id))
    if not data:
        return jsonify({"error": "Échec récupération"}), 404
    return jsonify(data), 200
