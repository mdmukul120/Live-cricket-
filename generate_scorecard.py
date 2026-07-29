
import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont

API_URL = "https://bdcrictime.com/api/get-live-score-slider?filtered=1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def fetch_image_from_url(url):
    try:
        if not url:
            return None
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content)).convert("RGBA")
    except Exception as e:
        print(f"Error fetching image: {e}")
    return None

def create_match_card(match):
    match_id = match.get("match_id", "live")
    tournament = match.get("competition", {}).get("abbr", "LIVE MATCH") if match.get("competition") else "LIVE MATCH"
    subtitle = match.get("subtitle", "")
    status_note = match.get("status_note") or match.get("live") or "Match Status N/A"
    
    team_a = match.get("teama", {})
    a_name = team_a.get("name", "Team A")
    a_score = team_a.get("scores_full") or team_a.get("scores") or "Yet to Bat"
    a_logo_url = team_a.get("logo_url")

    team_b = match.get("teamb", {})
    b_name = team_b.get("name", "Team B")
    b_score = team_b.get("scores_full") or team_b.get("scores") or "Yet to Bat"
    b_logo_url = team_b.get("logo_url")

    W, H = 800, 450
    card = Image.new("RGBA", (W, H), (15, 23, 42))
    draw = ImageDraw.Draw(card)

    draw.rectangle([0, 0, W, 60], fill=(30, 41, 59))
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_team = ImageFont.truetype("arial.ttf", 24)
        font_score = ImageFont.truetype("arial.ttf", 28)
        font_note = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        font_title = font_team = font_score = font_note = ImageFont.load_default()

    draw.text((W // 2, 30), f"{tournament} - {subtitle}", fill=(255, 255, 255), font=font_title, anchor="mm")

    logo_a = fetch_image_from_url(a_logo_url)
    logo_b = fetch_image_from_url(b_logo_url)

    if logo_a:
        logo_a = logo_a.resize((100, 100))
        card.paste(logo_a, (80, 110), logo_a)
    draw.text((130, 230), a_name, fill=(255, 255, 255), font=font_team, anchor="mm")
    draw.text((130, 270), a_score, fill=(132, 204, 22), font=font_score, anchor="mm")

    draw.text((W // 2, 200), "VS", fill=(148, 163, 184), font=font_team, anchor="mm")

    if logo_b:
        logo_b = logo_b.resize((100, 100))
        card.paste(logo_b, (620, 110), logo_b)
    draw.text((670, 230), b_name, fill=(255, 255, 255), font=font_team, anchor="mm")
    draw.text((670, 270), b_score, fill=(132, 204, 22), font=font_score, anchor="mm")

    draw.rectangle([0, 380, W, H], fill=(30, 41, 59))
    draw.text((W // 2, 415), status_note, fill=(226, 232, 240), font=font_note, anchor="mm")

    os.makedirs("output", exist_ok=True)
    filename = f"output/match_{match_id}.png"
    card.convert("RGB").save(filename)
    print(f"Successfully generated image: {filename}")

def main():
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=15)
        print(f"API Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("response", {}).get("items", [])
            
            if not items:
                print("No live matches currently available in API response.")
                # ম্যাচ না থাকলে টেস্ট ইমেজ বানাবে
                create_dummy_card()
                return

            for match in items:
                create_match_card(match)
        else:
            print("Failed to fetch API data.")
            create_dummy_card()
            
    except Exception as e:
        print(f"Error occurred: {e}")
        create_dummy_card()

def create_dummy_card():
    """ম্যাচ না থাকলে ডামি কার্ড তৈরি করে যেন টেস্ট বোঝা যায়"""
    dummy_data = {
        "match_id": "demo",
        "subtitle": "No Live Match Currently",
        "status_note": "Waiting for live match data...",
        "competition": {"abbr": "BDCRICTIME LIVE"},
        "teama": {"name": "Team A", "scores": "0/0", "logo_url": ""},
        "teamb": {"name": "Team B", "scores": "0/0", "logo_url": ""}
    }
    create_match_card(dummy_data)

if __name__ == "__main__":
    main()
