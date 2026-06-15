# Known Stale Repos — 已知旧项目回锅清单

> 以下 GitHub 项目经常在 X 上被重新提起，但创建日期远超 90 天，套利窗口已关闭。
> 每次新鲜度校验时优先检查此清单，匹配则直接排除，节省 GitHub 导航请求。

## 确认排除（>90 天）

| Repo | Stars | 创建年龄 | X 常见触发词 | 备注 |
|------|-------|----------|-------------|------|
| `bytedance/UI-TARS-desktop` | ~36K | >12 个月 | "China open-source desktop agent", "29k stars", "screen control" | ByteDance 桌面自动化 agent |
| `Shubhamsaboo/awesome-llm-apps` | ~106K | >12 个月 | "learn AI agents", "10 GitHub repos", "100+ agent apps" | 老牌 LLM 应用合集 |
| `nickscamara/openclaw` | ~300K | >6 个月 | "OpenClaw", "personal AI assistant", "WhatsApp Telegram" | 个人 AI 助手，已多次回锅 |
| `bytedance/deer-flow` | ~65K | >6 个月 | "ByteDance SuperAgent", "Deer Flow" | ByteDance 另一个 agent 项目 |
| `harry0703/MoneyPrinterTurbo` | 88.1K | >27 个月 | "AI short video factory", "MoneyPrinter" | AI 短视频工厂 |
| `NousResearch/Hermes-Agent` | 194K | ~11 个月 | "Hermes Agent", "automation blueprints" | 持续更新活跃但 repo 年龄 >90 天 |

## 疑似旧项目（需验证）

| Repo | 疑点 | 验证方法 |
|------|------|----------|
| 任何 "GPT-Image-X prompts" repo | 工具本身是新品，repo 通常 <7 天 | 仍建议验证创建日期 |

## 快速排除 JS

在 GitHub 仓库页面运行：
```javascript
const KNOWN_STALE = ['UI-TARS-desktop', 'awesome-llm-apps', 'openclaw', 'deer-flow', 'MoneyPrinterTurbo', 'Hermes-Agent'];
const repoName = window.location.pathname.split('/').slice(1,3).join('/').toLowerCase();
if (KNOWN_STALE.some(r => repoName.includes(r.toLowerCase()))) {
  return JSON.stringify({ action: 'SKIP', reason: 'known stale repo', repo: repoName });
}
```
