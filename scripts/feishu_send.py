import json, urllib.request, sys, io

CREDS_PATH = "d:/Users/shenawei/Desktop/贝勒爷指南/code/git/demand-radar/scripts/feishu-credentials.json"
CHAT_ID = "oc_f5808f24b1b712050496728dc76ef2c7"

def get_token():
    creds = json.load(open(CREDS_PATH))
    data = json.dumps({"app_id": creds["app_id"], "app_secret": creds["app_secret"]}).encode("utf-8")
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data, headers={"Content-Type": "application/json"}
    )
    return json.loads(urllib.request.urlopen(req).read())["tenant_access_token"]

def send_text(text):
    token = get_token()
    msg = json.dumps({
        "receive_id": CHAT_ID,
        "msg_type": "text",
        "content": json.dumps({"text": text}, ensure_ascii=False)
    }, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=msg,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}"
        }
    )
    resp = json.loads(urllib.request.urlopen(req).read())
    return resp

def send_card(title, content_md):
    """Send an interactive card with markdown content"""
    token = get_token()
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "blue"
        },
        "elements": [
            {"tag": "markdown", "content": content_md}
        ]
    }
    msg = json.dumps({
        "receive_id": CHAT_ID,
        "msg_type": "interactive",
        "content": json.dumps(card, ensure_ascii=False)
    }, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=msg,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}"
        }
    )
    resp = json.loads(urllib.request.urlopen(req).read())
    return resp

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = sys.argv[1]
        resp = send_text(text)
    else:
        resp = send_text("🔍 热点雷达 测试消息 🚀")
    code = resp.get('code', -1)
    msg_id = resp.get('data', {}).get('message_id', '?')
    print(f"code={code} msg_id={msg_id}")
