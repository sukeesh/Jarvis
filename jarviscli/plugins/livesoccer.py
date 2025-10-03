from plugin import plugin #lets jarvis recognize this file as a plugin
import requests #used for calling the external soccer API.

KEY = "4ec85a0cf6msh28cda3dfb58f16ep18b152jsnd7f7ade0cd8b" #API key (hardcoded here). will explain issue later
HOST = "free-api-live-football-data.p.rapidapi.com" #API endpoint for matches
URL = f"https://{HOST}/football-current-live"   ##API endpoint for matches


def headers(): 
    "Return headers for API"
    return {"x-rapidapi-host": HOST, "x-rapidapi-key": KEY}


def fetch():
    "Get live matches score from API"
    r = requests.get(URL, headers=headers(), timeout=12)
    return r.json() if r.content else {}


def get_matches(data):
    "Return list of matches"
    if not isinstance(data, dict):
        return []
    resp = data.get("response")
    if isinstance(resp, dict) and isinstance(resp.get("live"), list):
        return resp["live"]
    if isinstance(data.get("data"), list):
        return data["data"]
    if isinstance(data.get("response"), list):
        return data["response"]
    return []


def status(m):
    "Return short match status"
    st = m.get("status") or {}
    lt = st.get("liveTime") or {}
    t = lt.get("short")
    if t:
        return f" ({t})"
    if st.get("finished"):
        return " (Full-time)"
    if st.get("cancelled"):
        return " (Cancelled)"
    if st.get("started") and st.get("ongoing"):
        return " (In progress)"
    return ""


def one_line(m):
    "Return match info in one line"
    league = m.get("leagueName") or f"League {m.get('leagueId','')}".strip() or "League"
    home = (m.get("home") or {}).get("name", "Home")
    away = (m.get("away") or {}).get("name", "Away")

    score = (m.get("status") or {}).get("scoreStr")
    if not score:
        gh = (m.get("home") or {}).get("score")
        ga = (m.get("away") or {}).get("score")
        gh = "-" if gh is None else gh
        ga = "-" if ga is None else ga
        score = f"{gh} - {ga}"

    score = score.replace("-", "–")
    suf = status(m)

    red = (m.get("status") or {}).get("numberOfAwayRedCards")
    note = ""
    if isinstance(red, int) and red > 0:
        note = f" {away} have {red} red card{'s' if red != 1 else ''}."

    return f"In {league}, {home} {score} {away}{suf}.{note}"


@plugin("livesoccer")
def livesoccer(jarvis, s):
    "Show all live matches"
    data = fetch()
    matches = get_matches(data)

    if not matches:
        jarvis.say("No live matches right now.")
        return

    for m in matches:
        if isinstance(m, dict):
            jarvis.say(one_line(m))
