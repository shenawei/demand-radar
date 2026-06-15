"""
Radar Pipeline — 雷达报告自动化推送
Usage: python scripts/radar-pipeline.py [--dry-run]
从 demand-radar.json 读取 → 域名检查 → 历史对比 → 飞书推送 → git push
"""
import json, os, sys
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_DIR, "public", "data", "demand-radar.json")

def load_report():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def check_available_domains(report):
    """Quick DNS-based domain check. Returns list of (domain, status)."""
    import subprocess
    available = []
    taken = []
    for signal in report.get("top10", [])[:5]:
        for domain in signal.get("domainSuggestions", []):
            try:
                result = subprocess.run(
                    ["nslookup", domain], capture_output=True, text=True, timeout=5
                )
                if "Non-existent domain" in result.stderr or "server can't find" in result.stdout.lower():
                    available.append(domain)
                elif "Address" in result.stdout or "Addresses" in result.stdout:
                    taken.append(domain)
            except:
                pass
    return available, taken

def build_feishu_message(report):
    date = report.get("date", "?")
    time = report.get("time", "?")
    top = report.get("top10", [])[:5]

    lines = [f"AI Hotspot Radar | {date} {time}", ""]
    lines.append("**Top 5**")
    for item in top:
        rank = item["rank"]
        kw = item["keyword"]
        desc = item["description"][:60]
        signal = item["signal"]
        gh = item.get("github", "")
        stars = f" {item['stars']}*" if item.get("stars") else ""
        lines.append(f"{rank}. **{kw}** {signal} | {desc}")
        if gh:
            lines.append(f"   GitHub: {gh}{stars}")

    # Domain availability
    available, taken = check_available_domains(report)
    if available:
        lines.append(f"\nDomain Available: {', '.join(available[:5])}")

    # Excluded
    excluded = report.get("scanParams", {}).get("githubExcluded", 0)
    if excluded:
        lines.append(f"\nExcluded {excluded} stale repos")

    lines.append(f"\nScanned {report.get('scanParams',{}).get('raw','?')} posts -> Top {len(top)}")
    return "\n".join(lines)

def push_to_git():
    import subprocess
    os.chdir(PROJECT_DIR)
    subprocess.run(["git", "add", "daily-reports/", "public/data/", "references/"], check=False)
    now = datetime.now().strftime("%Y-%m-%d %H:%M CST")
    top_keywords = ""
    try:
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
            top_keywords = " | ".join([x["keyword"] for x in d.get("top10", [])[:3]])
    except:
        pass
    subprocess.run(["git", "commit", "-m", f"radar: {now} - {top_keywords}"], check=False)
    subprocess.run(["git", "pull", "--rebase"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("git push done")

if __name__ == "__main__":
    report = load_report()
    msg = build_feishu_message(report)

    # Send to Feishu
    sys.path.insert(0, os.path.join(PROJECT_DIR, "scripts"))
    from feishu_send import send_text
    resp = send_text(msg)
    print(f"Feishu: code={resp.get('code')} msg_id={resp.get('data',{}).get('message_id','?')}")

    # Git push
    if "--dry-run" not in sys.argv:
        push_to_git()
