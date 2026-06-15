"""
Radar Pipeline — 雷达报告飞书推送
Usage: python scripts/radar-pipeline.py [--dry-run]
"""
import json, os, sys
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_DIR, "public", "data", "demand-radar.json")

def load_report():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def push_to_git():
    import subprocess
    os.chdir(PROJECT_DIR)
    subprocess.run(["git", "add", "daily-reports/", "public/data/", "references/"], check=False)
    now = datetime.now().strftime("%Y-%m-%d %H:%M CST")
    try:
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
            top_keywords = " | ".join([x["keyword"] for x in d.get("signals", [])[:3]])
    except:
        top_keywords = ""
    subprocess.run(["git", "commit", "-m", f"radar: {now} - {top_keywords}"], check=False)
    subprocess.run(["git", "pull", "--rebase"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("git push done")

if __name__ == "__main__":
    report = load_report()
    signals = report.get("signals", report.get("top10", []))
    date = report.get("date", "?")
    time = report.get("time", "?")

    sys.path.insert(0, os.path.join(PROJECT_DIR, "scripts"))
    from feishu_send import send_text

    # Part 1: Top 5 with full details
    lines1 = [f"AI Hotspot Radar | {date} {time}", ""]
    for s in signals[:5]:
        gh = ""
        if s.get("github"):
            gh = f" [{s['github'].split('/')[-1]} {s.get('stars','')}]"
        lines1.append(f"{s['rank']}. {s['keyword']} {s['signal']} ({s['finalScore']}){gh}")
        lines1.append(f"   {s['description']}")
        # Arbitrage
        arb = s.get("arbitrageDirection", "")
        if arb:
            lines1.append(f"   Dir: {arb[:80]}")
        # Pain point
        pp = s.get("painPoint", "")
        if pp:
            lines1.append(f"   Pain: {pp[:80]}")
        # Domains
        ds = s.get("domainSuggestions", [])
        if ds:
            lines1.append(f"   Domains: {', '.join(ds[:3])}")
        lines1.append("")
    send_text("\n".join(lines1))

    # Part 2: 6-10 + insights
    lines2 = [f"Top 6-10 + Insights | {date}", ""]
    for s in signals[5:10]:
        gh = ""
        if s.get("github"):
            gh = f" [{s['github'].split('/')[-1]} {s.get('stars','')}]"
        lines2.append(f"{s['rank']}. {s['keyword']} {s['signal']} | {s['description'][:80]}{gh}")
        arb = s.get("arbitrageDirection", "")
        if arb:
            lines2.append(f"   Dir: {arb[:80]}")
        lines2.append("")

    lines2.append("---")
    for i in report.get("insights", [])[:3]:
        lines2.append(f"> {i[:120]}")
    sp = report.get("scanParams", {})
    lines2.append(f"\n{sp.get('top','?')} posts | excluded {sp.get('githubExcluded',0)} stale")
    send_text("\n".join(lines2))

    print("Feishu sent OK")

    if "--dry-run" not in sys.argv:
        push_to_git()
