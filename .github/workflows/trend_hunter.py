
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


FEEDS = {
    "United States": "https://trends.google.com/trending/rss?geo=US",
    "United Kingdom": "https://trends.google.com/trending/rss?geo=GB",
    "Germany": "https://trends.google.com/trending/rss?geo=DE",
    "France": "https://trends.google.com/trending/rss?geo=FR",
    "Italy": "https://trends.google.com/trending/rss?geo=IT",
    "Spain": "https://trends.google.com/trending/rss?geo=ES",
}


def fetch_trends(country, url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            root = ET.fromstring(response.read())

        items = []

        for item in root.findall(".//item"):
            title = item.findtext("title", default="").strip()
            traffic = item.findtext(
                "{https://trends.google.com/trending/rss}approx_traffic",
                default=""
            ).strip()

            if title:
                items.append({
                    "country": country,
                    "topic": title,
                    "approx_traffic": traffic
                })

        return items

    except Exception as error:
        print(f"Could not fetch {country}: {error}")
        return []

def main():
    all_trends = []

    for country, url in FEEDS.items():
        print(f"Checking {country}...")
        all_trends.extend(fetch_trends(country, url))

    # Remove duplicate topics
    unique = {}
    for trend in all_trends:
        key = trend["topic"].casefold()
        if key not in unique:
            unique[key] = trend

    results = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "total_topics": len(unique),
        "trends": list(unique.values())
    }

    with open("trends.json", "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)

    print(f"Found {len(unique)} unique topics.")
    for trend in list(unique.values())[:15]:
        print(f"- [{trend['country']}] {trend['topic']} "
              f"({trend['approx_traffic'] or 'traffic unavailable'})")

if __name__ == "__main__":
    main()
