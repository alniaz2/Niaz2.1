import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

INPUT_FILE = "trends.json"
OUTPUT_FILE = "research.json"
MAX_TOPICS = 10
RESULTS_PER_TOPIC = 5

def text_of(element, name):
    child = element.find(name)
    return (child.text or "").strip() if child is not None else ""

def search_news(topic, country):
    
    settings = {
        "United States": ("US", "en", "US:en"),
        "United Kingdom": ("GB", "en", "GB:en"),
        "Germany": ("DE", "en", "DE:en"),
        "France": ("FR", "en", "FR:en"),
        "Italy": ("IT", "en", "IT:en"),
        "Spain": ("ES", "en", "ES:en"),
    }

    gl, hl, ceid = settings.get(
        country, ("US", "en", "US:en")
    )

    params = urllib.parse.urlencode({
        "q": topic,
        "hl": f"{hl}-{gl}",
        "gl": gl,
        "ceid": ceid,
    })
    url = "https://news.google.com/rss/search?" + params

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            root = ET.fromstring(response.read())

        articles = []
        for item in root.findall(".//item")[:RESULTS_PER_TOPIC]:
            title = text_of(item, "title")
            link = text_of(item, "link")
            source = text_of(item, "source")
            pub_date = text_of(item, "pubDate")
            description = text_of(item, "description")

            if not title or not link:
                continue

            try:
                published = parsedate_to_datetime(pub_date).isoformat()
            except (ValueError, TypeError, OverflowError):
                published = pub_date

            articles.append({
                "title": title,
                "source": source or "Source not identified",
                "url": link,
                "published_at": published,
                "description": description,
            })

        return articles

    except Exception as error:
        print(f"Search failed for '{topic}': {error}")
        return []

def main():
    with open(INPUT_FILE, encoding="utf-8") as file:
        trends = json.load(file).get("trends", [])

    reports = []
    seen_urls = set()

    for trend in trends[:MAX_TOPICS]:
        topic = trend.get("topic", "").strip()
        country = trend.get("country", "United States")

        if not topic:
            continue

        print(f"Searching news for: {topic}")
        articles = search_news(topic, country)

        for article in articles:
            if article["url"] in seen_urls:
                continue

            seen_urls.add(article["url"])
            reports.append({
                "trend": topic,
                "trend_country": country,
                **article
            })

    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "topics_checked": min(len(trends), MAX_TOPICS),
        "reports_found": len(reports),
        "reports": reports,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print(f"Research complete: {len(reports)} reports found.")

if __name__ == "__main__":
    main()
