"""Erzeugt aus _feed/eintraege.json (neueste zuerst):
  - /feed.xml      den RSS-Feed für Feedreader
  - /neu/index.html die Seite „Neues auf emergenz.art“ (zuletzt ergänzt)
Neue Texte oben in eintraege.json eintragen, dann: python3 _feed/feed.py
Der Ordner _feed wird von GitHub Pages (Jekyll) nicht ausgeliefert."""
import json, os
from datetime import datetime
from email.utils import format_datetime
from html import escape as html_escape
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://emergenz.art'
TZ = ZoneInfo('Europe/Berlin')
MONATE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli',
          'August', 'September', 'Oktober', 'November', 'Dezember']

eintraege = json.load(open(os.path.join(ROOT, '_feed', 'eintraege.json'), encoding='utf-8'))
eintraege.sort(key=lambda e: e['datum'], reverse=True)


def deutsch(datum):
    d = datetime.fromisoformat(datum)
    return f'{d.day}. {MONATE[d.month - 1]} {d.year}'


def rfc822(datum):
    return format_datetime(datetime.fromisoformat(datum).replace(hour=12, tzinfo=TZ))


# RSS
items = []
for e in eintraege:
    url = BASE + e['url']
    items.append(f'''    <item>
      <title>{escape(e['titel'])}</title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{rfc822(e['datum'])}</pubDate>
      <category>{escape(e['rubrik'])}</category>
      <description>{escape(e['text'])}</description>
    </item>''')

xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>emergenz.art</title>
    <link>{BASE}/</link>
    <atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Neue Texte, Würdigungen und Begriffe zu Emergenz, Kipppunkten und Kunst.</description>
    <language>de</language>
    <lastBuildDate>{rfc822(eintraege[0]['datum'])}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
'''
open(os.path.join(ROOT, 'feed.xml'), 'w', encoding='utf-8').write(xml)

# Seite /neu/
li = []
for e in eintraege:
    li.append(f'''      <li>
        <div class="eintrag-kopf"><span class="rubrik">{html_escape(e['rubrik'])}</span> · <time datetime="{e['datum']}">{deutsch(e['datum'])}</time></div>
        <a href="{e['url']}">{html_escape(e['titel'])}</a>
        <p>{html_escape(e['text'])}</p>
      </li>''')
vorlage = open(os.path.join(ROOT, '_feed', 'neu-vorlage.html'), encoding='utf-8').read()
os.makedirs(os.path.join(ROOT, 'neu'), exist_ok=True)
open(os.path.join(ROOT, 'neu', 'index.html'), 'w', encoding='utf-8').write(
    vorlage.replace('{{EINTRAEGE}}', '\n'.join(li)))

print(f'{len(items)} Einträge, neuester {eintraege[0]["datum"]}: feed.xml und neu/index.html geschrieben')
