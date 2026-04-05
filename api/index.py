import curl_cffi.requests as tls_requests
from flask import Flask, jsonify, request
import time
import random

FOTMOB_API = "https://www.fotmob.com/api"
LOGGER = print

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
        url = f"{FOTMOB_API}/data/matches?date={date_str}&timezone=Europe%2FParis&ccode3=FRA"
        return self._get(url)

    def get_team(self, team_id, tab="overview"):
        url = f"{FOTMOB_API}/data/teams?id={team_id}&tab={tab}&type=team&timeZone=Europe/Paris"
        return self._get(url)

    def get_league(self, league_id, tab="table"):
        url = f"{FOTMOB_API}/data/leagues?id={league_id}&tab={tab}&type=league&timeZone=Europe/Paris"
        return self._get(url)


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
