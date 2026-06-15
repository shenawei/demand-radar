"""
Radar Pipeline — 雷达报告自动化推送
用法: python scripts/radar-pipeline.py
从 demand-radar.json 读取最新报告 → 生成飞书消息 → 发送 → git push
"""
import json, os, sys
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_DIR, "public", "data", "demand-radar.json")

def load_report():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def build_feishu_message(report):
    date = report.get("date", "?")
    time = report.get("time", "?")
    top = report.get("top10", [])[:5]

    lines = [f"🔍 AI 热点雷达 | {date} {time}", ""]

    # Top 5 table
    lines.append("**🔥 Top 5**")
    for item in top:
        rank = item["rank"]
        kw = item["keyword"]
        desc = item["description"][:60]
        signal = item["signal"]
        gh = item.get("github", "")
        stars = f" ⭐{item['stars']}" if item.get("stars") else ""
        lines.append(f"{rank}. **{kw}** {signal} — {desc}")
        if gh:
            lines.append(f"   GitHub: {gh}{stars}")

    # Excluded
    excluded = report.get("scanParams", {}).get("githubExcluded", 0)
    if excluded:
        lines.append(f"\n💀 已排除 {excluded} 个旧项目回锅")

    # Insights
    insights = report.get("insights", [])[:2]
    if insights:
        lines.append("\n**🔮 关键洞察**")
        for i in insights:
            lines.append(f"• {i}")

    lines.append(f"\n📊 原始 {report.get('scanParams',{}).get('raw','?')} 条 → 精选 {len(top)} 条")
    return "\n".join(lines)

def push_to_git():
    import subprocess
    os.chdir(PROJECT_DIR)
    subprocess.run(["git", "add", "daily-reports/", "public/data/"], check=False)
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
    push_to_git()
