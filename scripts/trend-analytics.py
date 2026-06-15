"""
Trend analytics — compare today vs yesterday radar reports.
Detects: accelerating signals, re-emerging topics, fading signals.
Usage: python scripts/trend-analytics.py
"""
import json, os, glob
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(PROJECT_DIR, "daily-reports")

def find_recent_reports(n=7):
    """Find the n most recent report directories."""
    dirs = sorted(glob.glob(os.path.join(REPORTS_DIR, "*-*-*")), reverse=True)
    return dirs[:n]

def load_report(dir_path):
    """Load a report from a directory. Returns dict or None."""
    data_file = os.path.join(PROJECT_DIR, "public", "data", "demand-radar.json")
    # Check if the data file matches this report date
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except:
        return None

def compare_reports(today, yesterday):
    """Compare two reports and return insights."""
    insights = []

    today_signals = {s["keyword"]: s for s in today.get("top10", [])}
    yesterday_signals = {s["keyword"]: s for s in yesterday.get("top10", [])}

    # 1. New signals (not in yesterday's report)
    new = [k for k in today_signals if k not in yesterday_signals]
    if new:
        insights.append(f"🆕 新信号: {', '.join(new)}")

    # 2. Accelerating signals (higher rank today)
    for k in set(today_signals) & set(yesterday_signals):
        t_rank = today_signals[k]["rank"]
        y_rank = yesterday_signals[k]["rank"]
        if t_rank < y_rank:
            insights.append(f"📈 加速: {k} (#{y_rank} -> #{t_rank})")

    # 3. Fading signals (lower rank)
    for k in set(today_signals) & set(yesterday_signals):
        t_rank = today_signals[k]["rank"]
        y_rank = yesterday_signals[k]["rank"]
        if t_rank > y_rank + 2:
            insights.append(f"📉 消退: {k} (#{y_rank} -> #{t_rank})")

    # 4. Dropped signals (was in yesterday, not today)
    dropped = [k for k in yesterday_signals if k not in today_signals]
    if dropped:
        insights.append(f"💨 退出榜单: {', '.join(dropped[:5])}")

    # 5. Signal strength changes
    for k in set(today_signals) & set(yesterday_signals):
        t_s = today_signals[k]["signal"]
        y_s = yesterday_signals[k]["signal"]
        if t_s != y_s:
            insights.append(f"🔄 信号变化: {k} ({y_s} -> {t_s})")

    return insights

def main():
    reports = find_recent_reports()
    if len(reports) < 1:
        print("No reports found")
        return

    today = load_report(reports[0])
    if not today:
        print("Cannot load today's report")
        return

    print(f"📊 Trend Analytics | {today.get('date','?')}")
    print()

    if len(reports) >= 2:
        yesterday = load_report(reports[1])
        if yesterday:
            insights = compare_reports(today, yesterday)
            if insights:
                for i in insights:
                    print(i)
            else:
                print("No significant changes from yesterday")
        else:
            print("Cannot load yesterday's report")
    else:
        print("Only one report available — need more data for comparison")

    print(f"\n🔮 Today's Insights:")
    for i in today.get("insights", [])[:3]:
        print(f"  • {i}")

if __name__ == "__main__":
    main()
