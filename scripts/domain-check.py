"""
Domain availability checker using RDAP (free, no API key needed).
Usage: python scripts/domain-check.py [--all]
"""
import json, urllib.request, ssl, sys, os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_DIR, "public", "data", "demand-radar.json")

# RDAP endpoints per TLD
RDAP_SERVERS = {
    "com": "https://rdap.verisign.com/com/v1/domain/",
    "net": "https://rdap.verisign.com/net/v1/domain/",
    "org": "https://rdap.publicinterestregistry.org/rdap/domain/",
    "io": "https://rdap.nic.io/domain/",
    "ai": "https://rdap.nic.ai/domain/",
    "app": "https://rdap.nic.google/domain/",
    "dev": "https://rdap.nic.google/domain/",
    "tools": "https://rdap.nic.tools/domain/",
    "xyz": "https://rdap.centralnic.com/xyz/domain/",
    "co": "https://rdap.nic.co/domain/",
    "pro": "https://rdap.afilias.net/rdap/pro/domain/",
    "fun": "https://rdap.centralnic.com/fun/domain/",
    "tech": "https://rdap.centralnic.com/tech/domain/",
    "me": "https://rdap.nic.me/domain/",
    "guide": "https://rdap.nic.guide/domain/",
    "info": "https://rdap.afilias.net/rdap/info/domain/",
}

def check_domain(domain):
    """Check single domain availability. Returns (domain, status, detail)."""
    parts = domain.split(".")
    tld = parts[-1].lower()

    server = RDAP_SERVERS.get(tld)
    if not server:
        return domain, "?", f"no RDAP server for .{tld}"

    url = server + domain
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/rdap+json"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        data = json.loads(resp.read().decode())
        status = data.get("status", [])
        if "active" in status or "registered" in status:
            return domain, "❌ taken", "registered"
        return domain, "✅ AVAILABLE", "free"
    except urllib.request.HTTPError as e:
        if e.code == 404:
            return domain, "✅ AVAILABLE", "free (not found)"
        return domain, "⚠️ error", f"HTTP {e.code}"
    except Exception as e:
        return domain, "⚠️ error", str(e)[:50]

def check_all():
    """Check all domains from the latest radar report."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        report = json.load(f)

    all_domains = []
    for signal in report.get("top10", []):
        for domain in signal.get("domainSuggestions", []):
            if domain not in all_domains:
                all_domains.append(domain)

    if not all_domains:
        print("No domains to check")
        return

    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    print(f"Checking {len(all_domains)} domains...\n")
    results = []
    for domain in all_domains:
        result = check_domain(domain)
        results.append(result)
        try:
            print(f"  {result[1]}  {domain}")
        except UnicodeEncodeError:
            print(f"  {result[1].encode('ascii','replace').decode()}  {domain}")
    return results

if __name__ == "__main__":
    check_all()
