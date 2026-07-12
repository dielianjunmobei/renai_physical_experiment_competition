import os
import json
import hmac
import time
import tomllib
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import db


BASE_DIR = Path(__file__).resolve().parent
SECRETS_PATH = BASE_DIR / ".streamlit" / "secrets.toml"
_AUTH_FAILURES: dict[str, list[float]] = {}
_AUTH_WINDOW_SECONDS = 300
_AUTH_FAILURE_LIMIT = 10


def _load_admin_token() -> str:
    env_token = os.environ.get("ADMIN_ANALYTICS_TOKEN", "").strip()
    if env_token:
        return env_token
    if SECRETS_PATH.exists():
        with SECRETS_PATH.open("rb") as f:
            secrets = tomllib.load(f)
        return str(secrets.get("admin_token", "")).strip()
    return ""


def _require_admin_token(x_admin_token: str | None, authorization: str | None, client_ip: str = "unknown") -> None:
    now = time.monotonic()
    recent_failures = [t for t in _AUTH_FAILURES.get(client_ip, []) if now - t < _AUTH_WINDOW_SECONDS]
    if len(recent_failures) >= _AUTH_FAILURE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many authentication attempts.")

    expected = _load_admin_token()
    if not expected:
        raise HTTPException(status_code=503, detail="Admin token is not configured.")

    supplied = x_admin_token or ""
    if not supplied and authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer":
            supplied = token

    if not hmac.compare_digest(supplied, expected):
        recent_failures.append(now)
        _AUTH_FAILURES[client_ip] = recent_failures
        raise HTTPException(status_code=401, detail="Invalid admin token.")

    _AUTH_FAILURES.pop(client_ip, None)


def _analytics_payload(recent_error_limit: int = 15) -> dict:
    return {
        "total": db.get_total_stats(),
        "chapters": db.get_chapter_stats(),
        "daily": db.get_daily_stats(),
        "feedback": db.get_feedback_stats(),
        "users": db.get_user_stats(),
        "errors": {
            "by_type": db.get_error_stats(),
            "recent": db.get_recent_errors(recent_error_limit),
        },
        "unanswered": db.get_unanswered_questions(),
    }


def _analytics_login_page() -> str:
    return """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>数据分析 - 管理员访问</title>
  <style>
    body { margin: 0; font-family: "Microsoft YaHei", system-ui, sans-serif; background: #0f141b; color: #e7edf5; }
    main { max-width: 1120px; margin: 0 auto; padding: 36px 20px; }
    .hero { background: #142235; border: 1px solid #26384f; border-radius: 10px; padding: 24px; margin-bottom: 22px; }
    h1 { margin: 0 0 8px; font-size: 28px; }
    .muted { color: #9fb0c4; }
    .login { display: flex; gap: 10px; align-items: center; margin-top: 18px; }
    input { flex: 1; min-width: 240px; padding: 11px 12px; border-radius: 6px; border: 1px solid #40546d; background: #0b1118; color: #fff; font-size: 15px; }
    button { padding: 11px 16px; border-radius: 6px; border: 0; background: #2f80ed; color: #fff; font-weight: 700; cursor: pointer; }
    button:hover { background: #4a90f0; }
    .error { color: #ff8a8a; margin-top: 12px; min-height: 22px; }
    .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 18px 0; }
    .card { background: #121b27; border: 1px solid #26384f; border-radius: 8px; padding: 16px; }
    .metric { font-size: 26px; font-weight: 800; margin-top: 8px; }
    .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    pre { white-space: pre-wrap; word-break: break-word; background: #091019; border: 1px solid #26384f; border-radius: 8px; padding: 12px; max-height: 360px; overflow: auto; }
    li { margin: 6px 0; }
    @media (max-width: 800px) { .grid, .cols { grid-template-columns: 1fr; } .login { flex-direction: column; align-items: stretch; } }
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>📈 数学物理方法 Agent 数据分析</h1>
      <div class="muted">管理员专用。请输入口令后查看问答日志、错误追踪和章节统计。</div>
      <div class="login">
        <input id="token" type="password" placeholder="输入管理员口令" autocomplete="current-password" />
        <button onclick="loadAnalytics()">进入</button>
      </div>
      <div id="error" class="error"></div>
    </section>
    <section id="dashboard"></section>
  </main>
  <script>
    const tokenInput = document.getElementById("token");
    tokenInput.addEventListener("keydown", event => {
      if (event.key === "Enter") loadAnalytics();
    });

    function itemList(rows, mapper) {
      if (!rows || rows.length === 0) return "<p class='muted'>暂无数据</p>";
      return "<ul>" + rows.map(row => mapper(new Proxy(row, {
        get(target, key) { return escapeHtml(target[key]); }
      }))).join("") + "</ul>";
    }

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function loadAnalytics() {
      const token = tokenInput.value.trim();
      const errorEl = document.getElementById("error");
      const dashboard = document.getElementById("dashboard");
      errorEl.textContent = "";
      dashboard.innerHTML = "";
      if (!token) {
        errorEl.textContent = "请输入管理员口令。";
        return;
      }
      const resp = await fetch("/analytics?format=json", {
        headers: { "X-Admin-Token": token }
      });
      if (!resp.ok) {
        const text = await resp.text();
        errorEl.textContent = resp.status === 401 ? "口令错误。" : text;
        return;
      }
      const data = await resp.json();
      const total = data.total || {};
      const users = data.users || {};
      dashboard.innerHTML = `
        <div class="grid">
          <div class="card"><div class="muted">总提问数</div><div class="metric">${total.total_questions ?? 0}</div></div>
          <div class="card"><div class="muted">错误数</div><div class="metric">${total.total_errors ?? 0}</div></div>
          <div class="card"><div class="muted">用户数</div><div class="metric">${users.total_users ?? 0}</div></div>
          <div class="card"><div class="muted">Sessions</div><div class="metric">${total.total_sessions ?? 0}</div></div>
        </div>
        <div class="cols">
          <div class="card">
            <h2>📚 章节统计</h2>
            ${itemList(data.chapters, r => `<li><b>${r.chapter || "未分类"}</b>: ${r.cnt} 题 | in=${r.ti || 0} out=${r.to_tokens || 0}</li>`)}
          </div>
          <div class="card">
            <h2>📅 每日用量</h2>
            ${itemList(data.daily, r => `<li><b>${r.day}</b>: ${r.questions} 题 | in=${r.ti || 0} out=${r.to_tokens || 0}</li>`)}
          </div>
        </div>
        <div class="cols" style="margin-top:14px;">
          <div class="card">
            <h2>👤 最近用户</h2>
            ${itemList(users.recent, r => `<li><b>${r.display_name || r.username}</b> <span class="muted">@${r.username}</span><br><span class="muted">最近登录: ${r.last_login ? String(r.last_login).slice(0,19) : "尚未登录"}</span></li>`)}
          </div>
          <div class="card">
            <h2>💬 反馈统计</h2>
            ${itemList(data.feedback, r => `<li><b>${r.rating}</b>: ${r.cnt} 次</li>`)}
          </div>
        </div>
        <div class="cols" style="margin-top:14px;">
          <div class="card">
            <h2>🚨 最近错误</h2>
            ${itemList((data.errors || {}).recent, r => `<li><b>${String(r.timestamp).slice(0,19)}</b> ${r.error_type}: ${r.error_message}</li>`)}
          </div>
          <div class="card">
            <h2>❓ 未成功回答</h2>
            ${itemList(data.unanswered, r => `<li><b>${r.chapter || ""}</b> ${String(r.question || "").slice(0,120)}<br><span class="muted">${String(r.error || "").slice(0,160)}</span></li>`)}
          </div>
        </div>
        <div class="card" style="margin-top:14px;">
          <h2>原始 JSON</h2>
          <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>
        </div>
      `;
    }
  </script>
</body>
</html>
"""


app = FastAPI(
    title="数学物理方法 Agent Admin API",
    description="管理员数据分析接口。需要 X-Admin-Token 或 Bearer token。",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Authorization", "X-Admin-Token"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/analytics")
def analytics(
    request: Request,
    x_admin_token: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
    recent_error_limit: int = Query(default=15, ge=1, le=100),
    format: str = Query(default="html"),
):
    has_token = bool(x_admin_token or authorization)
    if not has_token and format != "json":
        return HTMLResponse(_analytics_login_page())

    client_ip = request.client.host if request.client else "unknown"
    _require_admin_token(x_admin_token, authorization, client_ip)
    return _analytics_payload(recent_error_limit)
