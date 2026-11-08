"""Collect public Google News RSS headlines into news.json (no API key)."""
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

SECTORS = {
    "Indian economy & government policy": "India economy government policy budget RBI",
    "Global economy & geopolitics": "global economy geopolitics trade",
    "Artificial intelligence & technology": "artificial intelligence technology research",
    "Business & startups": "business startups funding innovation",
    "Manufacturing & MSMEs": "India MSME manufacturing small business",
    "Consumer trends & personal finance": "consumer spending personal finance inflation",
    "Healthcare & biotechnology": "healthcare biotechnology medical research",
    "Energy & climate": "renewable energy climate energy transition",
    "Agriculture & food industry": "agriculture food industry farming",
}

results = []
for sector, query in SECTORS.items():
    params = urllib.parse.urlencode({"q": query + " when:2d", "hl": "en-IN", "gl": "IN", "ceid": "IN:en"})
    url = "https://news.google.com/rss/search?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "DailyIntelligenceBrief/0.1 (RSS reader)"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            root = ET.fromstring(response.read())
        items = []
        for item in root.findall("./channel/item")[:5]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            source = item.find("source")
            published = (item.findtext("pubDate") or "").strip()
            if not title or not link:
                continue
            items.append({"title": title, "url": link, "source": source.text if source is not None else "", "published": published})
        results.append({"sector": sector, "articles": items})
        print(f"{sector}: {len(items)} headlines")
    except Exception as exc:
        print(f"WARNING: {sector}: {exc}")
        results.append({"sector": sector, "articles": []})

if not any(section["articles"] for section in results):
    raise SystemExit("No headlines retrieved; existing news.json left unchanged")

output = {"updated_at": datetime.now(timezone.utc).isoformat(), "note": "Headlines only; not AI-verified or independently fact-checked.", "sectors": results}
Path("news.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Saved news.json")
