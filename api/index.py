import curl_cffi.requests as tls_requests
import hashlib
import json
import base64
import time
import asyncio
import os
from flask import Flask, jsonify, request
from playwright.async_api import async_playwright

app = Flask(__name__)

FOO = "production:74ac2edaa7d42530fa49330efe1eedcfb21b555d"
BROWSERLESS_API_KEY = os.environ.get("BROWSERLESS_API_KEY", "")
LYRICS = """[Spoken Intro: Alan Hansen & Trevor Brooking]
I think it's bad news for the English game
We're not creative enough, and we're not positive enough

[Refrain: Ian Broudie & Jimmy Hill]
It's coming home, it's coming home, it's coming
Football's coming home (We'll go on getting bad results)
It's coming home, it's coming home, it's coming
Football's coming home
It's coming home, it's coming home, it's coming
Football's coming home
It's coming home, it's coming home, it's coming
Football's coming home

[Verse 1: Frank Skinner]
Everyone seems to know the score, they've seen it all before
They just know, they're so sure
That England's gonna throw it away, gonna blow it away
But I know they can play, 'cause I remember

[Chorus: All]
Three lions on a shirt
Jules Rimet still gleaming
Thirty years of hurt
Never stopped me dreaming

[Verse 2: David Baddiel]
So many jokes, so many sneers
But all those "Oh, so near"s wear you down through the years
But I still see that tackle by Moore and when Lineker scored
Bobby belting the ball, and Nobby dancing

[Chorus: All]
Three lions on a shirt
Jules Rimet still gleaming
Thirty years of hurt
Never stopped me dreaming

[Bridge]
England have done it, in the last minute of extra time!
What a save, Gordon Banks!
Good old England, England that couldn't play football!
England have got it in the bag!
I know that was then, but it could be again

[Refrain: Ian Broudie]
It's coming home, it's coming
Football's coming home
It's coming home, it's coming home, it's coming
Football's coming home
(England have done it!)
It's coming home, it's coming home, it's coming
Football's coming home
It's coming home, it's coming home, it's coming
Football's coming home
[Chorus: All]
(It's coming home) Three lions on a shirt
(It's coming home, it's coming) Jules Rimet still gleaming
(Football's coming home
It's coming home) Thirty years of hurt
(It's coming home, it's coming) Never stopped me dreaming
(Football's coming home
It's coming home) Three lions on a shirt
(It's coming home, it's coming) Jules Rimet still gleaming
(Football's coming home
It's coming home) Thirty years of hurt
(It's coming home, it's coming) Never stopped me dreaming
(Football's coming home
It's coming home) Three lions on a shirt
(It's coming home, it's coming) Jules Rimet still gleaming
(Football's coming home
It's coming home) Thirty years of hurt
(It's coming home, it's coming) Never stopped me dreaming
(Football's coming home)"""

class FotMobScraper:
    def __init__(self):
        self.base_url = "https://www.fotmob.com"
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8",
            "Referer": "https://www.fotmob.com/",
            "Origin": "https://www.fotmob.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

    def _get_xmas_header(self, path):
        timestamp = int(time.time() * 1000)
        body = {"url": path, "code": timestamp, "foo": FOO}
        json_str = json.dumps(body, separators=(',', ':'))
        sig = hashlib.md5(f"{json_str}{LYRICS}".encode('utf-8')).hexdigest().upper()
        full_payload = {"body": body, "signature": sig}
        return base64.b64encode(json.dumps(full_payload).encode('utf-8')).decode('utf-8')

    def _request(self, path):
        token = self._get_xmas_header(path)
        h = self.headers.copy()
        h["x-mas"] = token
        try:
            resp = tls_requests.get(f"{self.base_url}{path}", headers=h, impersonate="chrome120", timeout=15)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 403:
                return {"error": "Access Forbidden (403)", "details": "Possible Turnstile/WAF block"}
            else:
                return {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_daily_schedule(self, date_str):
        path = f"/api/data/matches?date={date_str}&timezone=Europe%2FParis&ccode3=FRA"
        return self._request(path)

    def get_team_details(self, team_id):
        path = f"/api/data/teams?id={team_id}&tab=overview&type=team&timeZone=Europe/Paris"
        return self._request(path)

    def get_league_details(self, league_id, tab="table"):
        path = f"/api/data/leagues?id={league_id}&tab={tab}&type=league&timeZone=Europe/Paris"
        return self._request(path)

    def get_match_details(self, match_id):
        async def _fetch():
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
                await page.goto(f"https://www.fotmob.com/fr/matches/x/x#{match_id}", wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(5000)
                await browser.close()
                return result.get('data')
        return asyncio.run(_fetch())

    def get_player_details(self, player_id):
        async def _fetch():
            ws_url = f"wss://chrome.browserless.io?token={BROWSERLESS_API_KEY}"
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(ws_url)
                context = await browser.new_context()
                page = await context.new_page()

                await page.goto(
                    f"https://www.fotmob.com/fr/players/{player_id}/x",
                    wait_until="domcontentloaded",
                    timeout=60000
                )
                await page.wait_for_timeout(3000)

                data = await page.evaluate("""
                    () => {
                        const el = document.getElementById('__NEXT_DATA__');
                        return el ? JSON.parse(el.innerText) : null;
                    }
                """)

                await browser.close()
                return data
        return asyncio.run(_fetch())


bot = FotMobScraper()

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "FotMob API Scraper Wrapper"})

@app.route('/api/match/<match_id>')
def match(match_id):
    return jsonify(bot.get_match_details(match_id))

@app.route('/api/player/<player_id>')
def player(player_id):
    return jsonify(bot.get_player_details(player_id))

@app.route('/api/team/<team_id>')
def team(team_id):
    return jsonify(bot.get_team_details(team_id))

@app.route('/api/league/<league_id>')
def league(league_id):
    tab = request.args.get('tab', 'table')
    return jsonify(bot.get_league_details(league_id, tab))

@app.route('/api/daily/<date_str>')
def daily(date_str):
    return jsonify(bot.get_daily_schedule(date_str))

app = app
