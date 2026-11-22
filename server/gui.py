"""BearFarm 私服 GUI 运维控制台.

用法:
    python gui.py [port=8090] [--host 127.0.0.1]

浏览器访问 http://127.0.0.1:8090 ，Token 首次生成于 server/data/gui_token.txt。
零第三方依赖 (纯 Python 标准库)；与 game server 通过 SQLite(WAL) + 日志文件共享状态。
"""
import json
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
DB_PATH = os.path.join(BASE, "data", "bearfarm.db")
LOG_PATH = os.path.join(BASE, "server.log")
TOKEN_PATH = os.path.join(BASE, "data", "gui_token.txt")
PROTO_ITEMS = os.path.join(ROOT, "protostrings.txt")
GAME_PORTS = {"farmzone": 8080, "api": 80, "esb": 60000, "packs": 8100}

START_TIME = time.time()
TOKEN = None


# ---------------- token ----------------

def ensure_token():
    global TOKEN
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    if os.path.exists(TOKEN_PATH):
        TOKEN = open(TOKEN_PATH, encoding="utf-8").read().strip()
    if not TOKEN:
        TOKEN = secrets.token_urlsafe(12)
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(TOKEN)
    return TOKEN


# ---------------- db helpers ----------------

def db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        conn.execute("ALTER TABLE users ADD COLUMN last_seen INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    return conn


def get_shop(conn, uid):
    row = conn.execute("SELECT shop FROM archives WHERE uid=?", (uid,)).fetchone()
    if not row or not row["shop"]:
        return None
    d = json.loads(row["shop"])
    return d.get("shop", d)


def save_shop(conn, uid, shop):
    row = conn.execute("SELECT uid FROM archives WHERE uid=?", (uid,)).fetchone()
    payload = json.dumps({"shop": shop}, ensure_ascii=False)
    if row:
        conn.execute("UPDATE archives SET shop=? WHERE uid=?", (payload, uid))
    else:
        conn.execute("INSERT INTO archives(uid, shop, updated) VALUES (?,?,?)",
                     (uid, payload, int(time.time())))
    conn.commit()


def empty_cell(i, status=None):
    return {"id": None, "itemId": None, "amount": 0, "price": 0, "costItem": None,
            "status": status if status is not None else (0 if i < 4 else 2),
            "seller": None, "buyer": None, "voyage": 0, "createdAt": 0,
            "autoBuy": False, "autobuyTime": 0, "index": i, "buyed": False}


def norm_cells(shop):
    cells = shop.setdefault("cells", [])
    while len(cells) < 8:
        cells.append(empty_cell(len(cells)))
    return cells


def load_items():
    try:
        out = []
        for line in open(PROTO_ITEMS, encoding="utf-8"):
            s = line.strip()
            if not s or len(s) < 3:
                continue
            if re.search(r"FTUE|fv2m|fv2mobile|camilk|_[A-Z]{3,}|^[a-z]+$", s):
                continue
            out.append(s)
        return out
    except FileNotFoundError:
        return []


# ---------------- log helpers ----------------

def tail_log(n):
    try:
        with open(LOG_PATH, encoding="utf-8", errors="replace") as f:
            return f.readlines()[-n:]
    except FileNotFoundError:
        return []


def parse_log_time(s):
    """'10-21 13:33:24' -> epoch (current year; Windows mktime can't do 1900)."""
    import datetime
    try:
        dt = datetime.datetime.strptime(s.strip(), "%m-%d %H:%M:%S")
        dt = dt.replace(year=datetime.datetime.now().year)
        return dt.timestamp()
    except ValueError:
        return None


def server_start_info():
    """Last 'bearfarm-server' banner in the log => game server start time."""
    for line in reversed(tail_log(3000)):
        if "bearfarm-server]" in line:
            m = re.match(r"\[([\d\- :]+)\]", line.strip())
            if m:
                t = parse_log_time(m.group(1))
                if t is not None:
                    return {"started": m.group(1).strip(), "uptime": int(time.time() - t)}
            break
    return {"started": None, "uptime": None}


def log_rate(minutes=5):
    now = time.time()
    cnt = 0
    for line in tail_log(800):
        m = re.match(r"\[([\d\- :]+)\]", line)
        if not m:
            continue
        t = parse_log_time(m.group(1))
        if t is None or now - t > minutes * 60 or t > now:
            continue
        cnt += 1
    return round(cnt / minutes, 1)


def log_stats(sample=2000):
    from collections import Counter
    c = Counter()
    pat = re.compile(r"\[.*?\] (FZ|API) (\S+)")
    for line in tail_log(sample):
        m = pat.search(line)
        if not m:
            continue
        key = m.group(2).split("?")[0]
        lm = re.search(r"'logic': '([^']+)'", line)
        if lm:
            key += "?logic=" + lm.group(1)
        c[f"{m.group(1)} {key}"] += 1
    return [{"endpoint": k, "count": v} for k, v in c.most_common(20)]


# ---------------- api payload builders ----------------

def now_ts():
    return int(time.time())


def api_status(conn):
    import socket
    ports = {}
    for name, port in GAME_PORTS.items():
        s = socket.socket()
        s.settimeout(0.4)
        try:
            s.connect(("127.0.0.1", port))
            ports[name] = True
        except Exception:
            ports[name] = False
        finally:
            s.close()
    counts = {}
    try:
        counts["players"] = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
        counts["friends"] = conn.execute("SELECT COUNT(*) c FROM friends").fetchone()["c"]
        counts["trees_planted"] = conn.execute(
            "SELECT COUNT(*) c FROM trees WHERE status>0").fetchone()["c"]
        selling = 0
        for r in conn.execute("SELECT shop FROM archives WHERE shop IS NOT NULL AND shop!=''"):
            try:
                shop = json.loads(r["shop"]).get("shop", {})
                selling += sum(1 for c in shop.get("cells", []) if c.get("status") == 3)
            except Exception:
                pass
        counts["offers"] = selling
    except sqlite3.Error:
        counts["players"] = counts["friends"] = counts["trees_planted"] = counts["offers"] = 0
    online = []
    try:
        for r in conn.execute("SELECT uid,name,level,last_seen FROM users "
                              "WHERE last_seen>? ORDER BY last_seen DESC", (now_ts() - 60,)):
            online.append({"uid": r["uid"], "name": r["name"], "level": r["level"]})
    except sqlite3.Error:
        pass
    return {
        "ports": ports,
        "online": online,
        "counts": counts,
        "rate5m": log_rate(5),
        "server": server_start_info(),
        "gui_uptime": int(time.time() - START_TIME),
        "db_size": os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0,
        "recent": [l.rstrip() for l in tail_log(15)],
    }


def api_players(conn, q):
    sql = ("SELECT u.uid,u.name,u.level,u.vip,u.face,u.last_seen,u.guid,"
           "(SELECT COUNT(*) FROM friends f WHERE f.uid=u.uid) nfriends "
           "FROM users u")
    args = []
    if q:
        sql += " WHERE CAST(u.uid AS TEXT) LIKE ? OR u.name LIKE ?"
        args = [f"%{q}%", f"%{q}%"]
    sql += " ORDER BY u.last_seen DESC, u.uid LIMIT 200"
    rows = conn.execute(sql, args).fetchall()
    out = []
    for r in rows:
        coin = key = None
        a = conn.execute("SELECT role FROM archives WHERE uid=?", (r["uid"],)).fetchone()
        if a and a["role"]:
            try:
                role = json.loads(a["role"])
                coin, key = role.get("coin"), role.get("key")
            except Exception:
                pass
        online = r["last_seen"] and r["last_seen"] > now_ts() - 60
        out.append({"uid": r["uid"], "name": r["name"], "level": r["level"], "vip": r["vip"],
                    "face": r["face"], "friends": r["nfriends"], "coin": coin, "key": key,
                    "last_seen": r["last_seen"], "online": bool(online)})
    return {"players": out}


def api_player(conn, uid):
    u = conn.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()
    if not u:
        return None
    friends = [dict(r) for r in conn.execute(
        "SELECT f.fid, COALESCE(us.name,'') name FROM friends f "
        "LEFT JOIN users us ON us.uid=f.fid WHERE f.uid=?", (uid,))]
    tree = conn.execute("SELECT * FROM trees WHERE uid=?", (uid,)).fetchone()
    tree_out = None
    if tree:
        remain = tree["planted_at"] + tree["grow_seconds"] - now_ts()
        tree_out = {"level": tree["level"], "status": tree["status"],
                    "remain": max(0, remain) if tree["status"] == 1 else 0,
                    "output": tree["output"], "left": tree["left_count"],
                    "stolen": tree["steal_count"]}
    arch = conn.execute("SELECT role, length(memory) mlen, updated FROM archives WHERE uid=?",
                        (uid,)).fetchone()
    role = {}
    if arch and arch["role"]:
        try:
            role = json.loads(arch["role"])
        except Exception:
            pass
    shop = get_shop(conn, uid)
    selling = 0
    if shop:
        selling = sum(1 for c in shop.get("cells", []) if c.get("status") == 3)
    return {"uid": u["uid"], "name": u["name"], "level": u["level"], "vip": u["vip"],
            "face": u["face"], "online": bool(u["last_seen"] and u["last_seen"] > now_ts() - 60),
            "last_seen": u["last_seen"], "coin": role.get("coin"), "key": role.get("key"),
            "friends": friends, "tree": tree_out,
            "memory_len": arch["mlen"] if arch else 0, "shop_selling": selling}


def api_shops(conn):
    rows = conn.execute("SELECT a.uid, a.shop, COALESCE(u.name,'') uname "
                        "FROM archives a LEFT JOIN users u ON u.uid=a.uid "
                        "WHERE a.shop IS NOT NULL AND a.shop!=''").fetchall()
    out = []
    for r in rows:
        try:
            shop = json.loads(r["shop"]).get("shop", {})
        except Exception:
            continue
        cells = shop.get("cells", [])
        out.append({"uid": r["uid"], "name": shop.get("name") or r["uname"] or str(r["uid"]),
                    "level": shop.get("level"), "selling": sum(1 for c in cells if c.get("status") == 3),
                    "total": len(cells)})
    return {"shops": out}


def api_shop(conn, uid, valid_items):
    shop = get_shop(conn, uid)
    if not shop:
        return None
    cells = []
    for c in norm_cells(shop):
        cells.append({"index": c["index"], "itemId": c.get("itemId"), "amount": c.get("amount"),
                      "price": c.get("price"), "status": c.get("status"),
                      "valid": (c.get("itemId") in valid_items) if c.get("itemId") else None})
    return {"uid": uid, "name": shop.get("name"), "level": shop.get("level"), "cells": cells}


def api_trees(conn):
    rows = conn.execute("SELECT t.*, COALESCE(u.name,'') uname "
                        "FROM trees t LEFT JOIN users u ON u.uid=t.uid").fetchall()
    out = []
    for t in rows:
        remain = t["planted_at"] + t["grow_seconds"] - now_ts()
        if t["status"] == 1 and remain <= 0:
            state = "mature"
        else:
            state = {0: "unplanted", 1: "growing", 2: "mature"}.get(t["status"], "?")
        out.append({"uid": t["uid"], "name": t["uname"] or str(t["uid"]), "level": t["level"],
                    "state": state, "remain": max(0, remain), "output": t["output"],
                    "left": t["left_count"], "stolen": t["steal_count"]})
    return {"trees": out}


def do_offer(conn, uid, body):
    item = str(body.get("itemId", "")).strip()
    amount = int(body.get("amount", 1))
    price = int(body.get("price", 100))
    if not item or amount <= 0 or price < 0:
        return {"ok": False, "error": "参数不合法"}
    shop = get_shop(conn, uid) or {"cells": [], "face": 1, "faceData": "0", "faceType": 0,
                                   "level": 1, "name": f"player{uid}", "uId": str(uid),
                                   "shopStatus": 1}
    cells = norm_cells(shop)
    idx = body.get("index")
    if idx is None:
        idx = next((i for i, c in enumerate(cells) if not c.get("itemId")), None)
    if idx is None or not (0 <= idx < 8):
        return {"ok": False, "error": "没有空摊位 (0-7)"}
    cells[int(idx)] = {"id": None, "itemId": item, "amount": amount, "price": price,
                      "costItem": "coin", "status": 3, "seller": str(uid), "buyer": None,
                      "voyage": 0, "createdAt": now_ts(), "autoBuy": False,
                      "autobuyTime": 0, "index": int(idx), "buyed": False}
    save_shop(conn, uid, shop)
    return {"ok": True, "index": int(idx)}


def do_clear(conn, uid):
    shop = get_shop(conn, uid)
    if not shop:
        return {"ok": False, "error": "该玩家没有商店数据"}
    cells = norm_cells(shop)
    for i, c in enumerate(cells):
        if c.get("status") == 3:
            cells[i] = empty_cell(i)
    save_shop(conn, uid, shop)
    return {"ok": True}


def do_unlock(conn, uid, body):
    idx = int(body.get("index", -1))
    shop = get_shop(conn, uid)
    if not shop or not (0 <= idx < 8):
        return {"ok": False, "error": "参数不合法"}
    cells = norm_cells(shop)
    if not cells[idx].get("itemId"):
        cells[idx]["status"] = 0
    save_shop(conn, uid, shop)
    return {"ok": True}


def do_offshelf(conn, uid, body):
    """把指定摊位的在售商品下架(置空)。"""
    idx = int(body.get("index", -1))
    shop = get_shop(conn, uid)
    if not shop or not (0 <= idx < 8):
        return {"ok": False, "error": "参数不合法"}
    cells = norm_cells(shop)
    cells[idx] = empty_cell(idx, status=0)
    save_shop(conn, uid, shop)
    return {"ok": True}


# ---------------- http ----------------

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>熊大农场 · 私服控制台</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{
 --bg:#0f1216;--panel:#161b22;--panel2:#1d2430;--line:#262e3b;
 --tx:#d7dde6;--dim:#7b8494;--acc:#4f9cf9;--ok:#3fbb6e;--warn:#e8b03f;--bad:#e85b5b;
 --radius:10px; font-size:14px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--tx);font-family:"Segoe UI","Microsoft YaHei",sans-serif;height:100vh;display:flex}
#side{width:190px;background:var(--panel);border-right:1px solid var(--line);padding:18px 12px;flex-shrink:0}
#logo{font-size:17px;font-weight:700;color:#fff;padding:6px 10px 18px}
#logo small{display:block;color:var(--dim);font-size:11px;font-weight:400;margin-top:3px}
.nav{display:block;width:100%;text-align:left;background:none;border:none;color:var(--dim);
 padding:10px 12px;border-radius:8px;cursor:pointer;font-size:14px;margin-bottom:2px}
.nav:hover{background:var(--panel2);color:var(--tx)}
.nav.on{background:var(--acc);color:#fff}
#main{flex:1;overflow-y:auto;padding:22px 26px}
h2{font-size:18px;margin-bottom:16px;color:#fff}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px}
.grid{display:grid;gap:14px}
.g4{grid-template-columns:repeat(4,1fr)} .g2{grid-template-columns:repeat(2,1fr)}
.kv{color:var(--dim);font-size:12px;margin-bottom:6px}
.val{font-size:22px;color:#fff;font-weight:600}
.val small{font-size:12px;color:var(--dim);font-weight:400}
table{width:100%;border-collapse:collapse;font-size:13px}
th{color:var(--dim);text-align:left;font-weight:500;padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
tr:hover td{background:var(--panel2)}
.badge{display:inline-block;padding:1px 8px;border-radius:10px;font-size:12px}
.b-ok{background:rgba(63,187,110,.15);color:var(--ok)} .b-bad{background:rgba(232,91,91,.15);color:var(--bad)}
.b-warn{background:rgba(232,176,63,.15);color:var(--warn)} .b-dim{background:var(--panel2);color:var(--dim)}
.port{padding:6px 12px;border-radius:8px;font-size:13px;background:var(--panel2);color:var(--dim)}
.port.up{background:rgba(63,187,110,.15);color:var(--ok)}
.port.down{background:rgba(232,91,91,.15);color:var(--bad)}
.mono{font-family:Consolas,monospace;font-size:12px}
#recent{max-height:210px;overflow-y:auto;font-family:Consolas,monospace;font-size:12px;line-height:1.6;color:var(--dim)}
button.act{background:var(--acc);border:none;color:#fff;padding:6px 14px;border-radius:7px;cursor:pointer;font-size:13px}
button.act:hover{filter:brightness(1.15)}
button.act.red{background:var(--bad)} button.act.gray{background:var(--panel2);color:var(--tx)}
button.act.mini{padding:3px 9px;font-size:12px}
input,select{background:var(--panel2);border:1px solid var(--line);color:var(--tx);
 padding:7px 10px;border-radius:7px;font-size:13px;outline:none}
input:focus{border-color:var(--acc)}
.drawer{position:fixed;top:0;right:-460px;width:440px;height:100vh;background:var(--panel);
 border-left:1px solid var(--line);transition:right .25s;padding:22px;overflow-y:auto;z-index:50}
.drawer.open{right:0}
.overlay{position:fixed;inset:0;background:rgba(5,8,12,.7);z-index:100;display:none;
 align-items:center;justify-content:center}
.overlay.show{display:flex}
.modal{background:var(--panel);border:1px solid var(--line);border-radius:12px;
 padding:22px;width:640px;max-height:88vh;overflow-y:auto}
.dl{row-gap:8px;margin:10px 0}
.dl div{padding:4px 0;border-bottom:1px dashed var(--line);display:flex;justify-content:space-between}
.dl span:first-child{color:var(--dim)}
#toast{position:fixed;bottom:26px;left:50%;transform:translateX(-50%);z-index:200;
 background:var(--panel2);border:1px solid var(--line);color:var(--tx);
 padding:10px 20px;border-radius:9px;display:none;font-size:13px}
#toast.err{border-color:var(--bad);color:var(--bad)}
#logbox{background:#0a0d11;border:1px solid var(--line);border-radius:8px;padding:12px;
 max-height:52vh;overflow-y:auto;font-family:Consolas,monospace;font-size:12px;line-height:1.55;white-space:pre-wrap;word-break:break-all}
.bar{height:14px;background:var(--acc);border-radius:3px;min-width:2px}
.cellcard{background:var(--panel2);border:1px solid var(--line);border-radius:8px;padding:10px;font-size:12px}
.cellcard b{display:block;color:#fff;font-size:13px;margin-bottom:3px}
.dimtx{color:var(--dim)} .rowflex{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:10px 0}
.search{width:220px}
.fld{display:flex;flex-direction:column;gap:4px;font-size:12px;color:var(--dim)}
#login{max-width:380px}
#login h2{margin-bottom:8px}
#login input{width:100%}
h3{font-size:14px;color:#fff;margin:14px 0 8px}
</style>
</head>
<body>
<div id="side">
 <div id="logo">🐻 熊大农场<small>私服运维控制台</small></div>
 <button class="nav on" data-page="dash">📊 总览</button>
 <button class="nav" data-page="players">👥 玩家</button>
 <button class="nav" data-page="market">🛒 集市</button>
 <button class="nav" data-page="trees">🌳 摇钱树</button>
 <button class="nav" data-page="log">📜 日志</button>
 <button class="nav" data-page="notice">📢 公告</button>
 <button class="nav" data-page="mail">✉️ 邮件</button>
 <button class="nav" data-page="settings">⚙️ 设置</button>
 <div style="margin-top:26px;color:var(--dim);font-size:11px;padding:0 10px;line-height:1.8">
   GUI 运行 <span id="guiup">-</span><br>数据 3s 刷新
 </div>
</div>
<div id="main">
 <section id="page-dash">
  <h2>总览</h2>
  <div class="rowflex" id="ports"></div>
  <div class="grid g4" style="margin-top:14px">
   <div class="card"><div class="kv">注册玩家</div><div class="val" id="c-players">-</div></div>
   <div class="card"><div class="kv">好友关系</div><div class="val" id="c-friends">-</div></div>
   <div class="card"><div class="kv">生长中摇钱树</div><div class="val" id="c-trees">-</div></div>
   <div class="card"><div class="kv">在售商品</div><div class="val" id="c-offers">-</div></div>
  </div>
  <div class="grid g2" style="margin-top:14px">
   <div class="card"><div class="kv">当前在线 (60s 心跳)</div><div id="online" style="margin-top:6px;line-height:1.9">-</div></div>
   <div class="card"><div class="kv">请求速率 (近5分钟)</div>
     <div class="val" id="c-rate">-<small> 条/分</small></div>
     <div class="kv" style="margin-top:12px">game server 启动于</div><div id="c-srvstart" class="mono">-</div>
     <div class="rowflex" style="margin-top:14px"><button class="act gray mini" onclick="backup()">💾 备份数据库</button>
     <span class="dimtx mono" id="c-dbsize">-</span></div>
   </div>
  </div>
  <div class="card" style="margin-top:14px"><div class="kv">最近事件</div><div id="recent">-</div></div>
 </section>

 <section id="page-players" style="display:none">
  <h2>玩家管理</h2>
  <div class="rowflex">
    <input class="search" id="pq" placeholder="搜索 uid / 名字" oninput="loadPlayers()">
  </div>
  <div class="card" style="padding:0;overflow-x:auto">
   <table id="ptable"><thead><tr>
    <th>uid</th><th>名字</th><th>等级</th><th>VIP</th><th>好友</th>
    <th>金币</th><th>钻石</th><th>最近活跃</th><th>状态</th></tr></thead><tbody></tbody></table>
  </div>
  <div class="dimtx" style="margin-top:8px">金币/钻石为客户端权威数据，仅供查看。</div>
 </section>

 <section id="page-market" style="display:none">
  <h2>集市管理</h2>
  <div class="card" style="padding:0"><table id="mtable">
   <thead><tr><th>uid</th><th>摊位主人</th><th>等级</th><th>在售/摊位</th><th>操作</th></tr></thead>
   <tbody></tbody></table></div>
 </section>

 <section id="page-trees" style="display:none">
  <h2>摇钱树</h2>
  <div class="card" style="padding:0"><table id="ttable">
   <thead><tr><th>uid</th><th>主人</th><th>树等级</th><th>状态</th><th>产出</th><th>剩余</th><th>被偷</th><th>操作</th></tr></thead>
   <tbody></tbody></table></div>
 </section>

 <section id="page-log" style="display:none">
  <h2>实时日志</h2>
  <div class="rowflex">
   <select id="ltype"><option value="">全部</option><option value="FZ">FZ (farmzone)</option><option value="API">API (DES)</option></select>
   <input class="search" id="luid" placeholder="uid 过滤">
   <input class="search" id="lq" placeholder="关键字">
   <button class="act gray mini" id="lauto" onclick="toggleAuto()">⏸ 暂停自动刷新</button>
   <button class="act gray mini" onclick="loadLog(true)">立即刷新</button>
  </div>
  <div class="grid g2" style="margin:12px 0">
   <div class="card"><div class="kv">请求统计 (最近日志采样)</div><div id="stats" style="margin-top:8px"></div></div>
   <div class="card"><div class="kv">日志流 (最新 200 条)</div><div id="logbox" style="margin-top:8px">-</div></div>
  </div>
 </section>

 <section id="page-notice" style="display:none">
  <h2>公告管理</h2>
  <div class="card" style="margin-bottom:14px;padding:16px">
   <h3>添加公告</h3>
   <div class="rowflex">
    <div class="fld">描述<textarea id="n_desc" rows="2" style="width:300px"></textarea></div>
    <div class="fld">图片名<input id="n_pic" placeholder="公告图片名(可选)" style="width:180px"></div>
    <div class="fld">类型<input id="n_type" value="0" style="width:60px"></div>
    <div class="fld">礼包ID<input id="n_gift" value="0" style="width:80px"></div>
   </div>
   <div class="rowflex" style="margin-top:8px"><button class="act" onclick="addNotice()">添加</button>
   <span class="dimtx">公告版本已自动递增,玩家下次启动会拉取新公告</span></div>
  </div>
  <div class="card" style="padding:0"><table id="ntable">
   <thead><tr><th>ID</th><th>描述</th><th>图片</th><th>类型</th><th>操作</th></tr></thead>
   <tbody></tbody></table></div>
 </section>

 <section id="page-mail" style="display:none">
  <h2>邮件系统</h2>
  <div class="card" style="margin-bottom:14px;padding:16px">
   <h3>发送邮件</h3>
   <div class="rowflex">
    <div class="fld">收件人 uid<input id="m_uid" placeholder="玩家 uid" style="width:100px"></div>
    <div class="fld">奖励格式: itemId|数量,itemId|数量<br>
    <input id="m_reward" placeholder="coin|1000,key|5" style="width:220px"></div>
    <div class="fld">描述<textarea id="m_desc" rows="2" style="width:280px"></textarea></div>
   </div>
   <div class="rowflex" style="margin-top:8px"><button class="act" onclick="sendMail()">发送</button>
   <span class="dimtx">玩家在游戏内邮箱中可领取 (需客户端 farm/mail 路径,当前主要为 dreammarket/getMails)</span></div>
  </div>
  <div class="card" style="padding:16px;margin-bottom:14px">
   <div class="rowflex"><input class="search" id="m_filter_uid" placeholder="按 uid 查看已发送邮件"
    oninput="loadMails()"></div>
  </div>
  <div class="card" style="padding:0"><table id="mtable2">
   <thead><tr><th>ID</th><th>uid</th><th>奖励</th><th>描述</th><th>时间</th><th>操作</th></tr></thead>
   <tbody></tbody></table></div>
 </section>

 <section id="page-settings" style="display:none">
  <h2>系统设置</h2>
  <div class="grid g2">
   <div class="card">
    <h3>摇钱树参数</h3>
    <div class="dl">
     <div><span>成熟时间 (秒)</span><input id="cfg_grow" style="width:100px" value="7200"></div>
     <div><span>产出基数</span><input id="cfg_base" style="width:100px" value="100"></div>
     <div><span>每级加成</span><input id="cfg_per" style="width:100px" value="20"></div>
    </div>
    <button class="act" onclick="saveConfig()">保存摇钱树配置</button>
   </div>
   <div class="card">
    <h3>签到奖励 (7天)</h3>
    <div id="signrewards" style="margin:8px 0"></div>
    <button class="act" onclick="saveSignRewards()">保存签到奖励</button>
   </div>
  </div>
  <div class="card" style="margin-top:14px">
   <h3>数据备份</h3>
   <div class="rowflex">
    <button class="act" onclick="backup()">💾 立即备份</button>
    <span class="dimtx">备份文件在 server/data/ 目录</span>
   </div>
   <div id="backuplist" style="margin-top:10px"></div>
  </div>
  <div class="card" style="margin-top:14px">
   <h3>日志维护</h3>
   <div class="rowflex">
    <button class="act red" onclick="confirmDo('确定清空所有日志?此操作不可撤销。',()=>clearLog())">清空日志</button>
    <span class="dimtx">server.log 当前约 <span id="logsize">-</span></span>
   </div>
  </div>
 </section>
</div>

<div class="drawer" id="drawer"></div>

<div class="overlay" id="ovl">
 <div class="modal" id="login" style="display:none">
  <h2>🔐 控制台登录</h2>
  <p class="dimtx" style="margin-bottom:12px">Token 已生成于服务器 server/data/gui_token.txt</p>
  <input id="tok" placeholder="粘贴 Token" onkeydown="if(event.key==='Enter')login()">
  <div class="rowflex"><button class="act" onclick="login()">登录</button><span class="dimtx" id="logintip"></span></div>
 </div>
 <div class="modal" id="shopModal" style="display:none"></div>
 <div class="modal" id="confirmModal" style="display:none;max-width:400px">
  <h3 id="cfTitle">确认</h3><p id="cfText" style="margin:10px 0 18px"></p>
  <div class="rowflex"><button class="act red" id="cfYes">确认</button>
  <button class="act gray" onclick="hideConfirm()">取消</button></div>
 </div>
</div>
<div id="toast"></div>

<script>
let TOKEN=localStorage.getItem('bf_token')||'';
let itemsCache=null;
let page='dash', poller=null, autoLog=true;

function api(path,opts){
  opts=opts||{};
  opts.headers=Object.assign({'X-Token':TOKEN},opts.headers||{});
  if(opts.body) opts.headers['Content-Type']='application/json';
  return fetch(path,opts).then(r=>{
    if(r.status===401){ showLogin(); throw new Error('401'); }
    return r.json();
  });
}
function toast(msg,err){const t=document.getElementById('toast');
  t.textContent=msg;t.className=err?'err':'';t.style.display='block';
  clearTimeout(t._h);t._h=setTimeout(()=>t.style.display='none',2600);}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){
 if(c==='&')return '&'+'amp;'; if(c==='<')return '&'+'lt;';
 if(c==='>')return '&'+'gt;'; return '&'+'quot;';});}
function fmtTime(ts){if(!ts)return'-';const d=new Date(ts*1000);
  return (d.getMonth()+1)+'-'+d.getDate()+' '+String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');}

/* ---------- pages ---------- */
document.querySelectorAll('.nav').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('.nav').forEach(x=>x.classList.remove('on'));
  b.classList.add('on');page=b.dataset.page;
  ['dash','players','market','trees','log','notice','mail','settings'].forEach(p=>{
    document.getElementById('page-'+p).style.display=(p===page)?'':'none';});
  refresh();
});
function refresh(){
  if(page==='dash') loadDash();
  else if(page==='players') loadPlayers();
  else if(page==='market') loadShops();
  else if(page==='trees') loadTrees();
  else if(page==='log') loadLog();
  else if(page==='notice') loadNotices();
  else if(page==='mail') loadMails();
  else if(page==='settings') loadSettings();
}
poller=setInterval(()=>{ if(!document.hidden) refresh();
  document.getElementById('guiup').textContent=Math.floor((Date.now()-GUI_T0)/1000)+'s';},3000);
const GUI_T0=Date.now();

/* ---------- login ---------- */
function showLogin(){document.getElementById('ovl').style.display='flex';
  document.getElementById('login').style.display='block';
  document.getElementById('shopModal').style.display='none';}
function hideOvl(){document.getElementById('ovl').style.display='none';}
function login(){const v=document.getElementById('tok').value.trim();
  TOKEN=v;
  api('/api/status').then(()=>{
    localStorage.setItem('bf_token',v);
    hideOvl();toast('登录成功');refresh();
  }).catch(()=>{
    document.getElementById('logintip').textContent='Token 无效';
  });}

/* ---------- dashboard ---------- */
function loadDash(){api('/api/status').then(s=>{
  const p=document.getElementById('ports');p.innerHTML='';
  for(const[k,v]of Object.entries(s.ports)){
    const el=document.createElement('span');
    el.className='port '+(v?'up':'down');
    el.textContent=(v?'● ':'✕ ')+k+':'+({farmzone:8080,api:80,esb:60000,packs:8100}[k]);
    p.appendChild(el);}
  document.getElementById('c-players').textContent=s.counts.players;
  document.getElementById('c-friends').textContent=s.counts.friends;
  document.getElementById('c-trees').textContent=s.counts.trees_planted;
  document.getElementById('c-offers').textContent=s.counts.offers;
  document.getElementById('c-rate').innerHTML=s.rate5m+'<small> 条/分</small>';
  document.getElementById('c-srvstart').textContent=s.server.started?('['+s.server.started+'] 运行 '+Math.floor(s.server.uptime/60)+' 分钟'):'未检测到启动横幅';
  document.getElementById('c-dbsize').textContent=(s.db_size/1024).toFixed(0)+' KB';
  const ol=document.getElementById('online');
  ol.innerHTML=s.online.length?s.online.map(o=>'<span class="badge b-ok">● </span> '+
    esc(o.name||o.uid)+' <span class="dimtx">Lv'+o.level+'</span>').join('<br>'):'<span class="dimtx">暂无在线玩家</span>';
  document.getElementById('recent').textContent=s.recent.join('\n')||'暂无日志';
}).catch(()=>{});}

function backup(){api('/api/backup',{method:'POST'}).then(r=>{
  toast(r.ok?'已备份: '+r.file:r.error,!r.ok);});}

/* ---------- players ---------- */
function loadPlayers(){api('/api/players?q='+encodeURIComponent(document.getElementById('pq').value.trim()))
 .then(d=>{const tb=document.querySelector('#ptable tbody');tb.innerHTML='';
  d.players.forEach(p=>{
    const tr=document.createElement('tr');tr.style.cursor='pointer';
    tr.onclick=()=>openDrawer(p.uid);
    tr.innerHTML='<td>'+p.uid+'</td><td>'+esc(p.name||'-')+'</td><td>'+p.level+'</td><td>'+p.vip+
      '</td><td>'+p.friends+'</td><td>'+(p.coin==null?'-':p.coin)+'</td><td>'+(p.key==null?'-':p.key)+
      '</td><td>'+fmtTime(p.last_seen)+'</td><td>'+(p.online?'<span class="badge b-ok">在线</span>':'<span class="badge b-dim">离线</span>')+'</td>';
    tb.appendChild(tr);});
 }).catch(()=>{});}

function openDrawer(uid){
  api('/api/player/'+uid).then(p=>{
    const d=document.getElementById('drawer');
    const tree=p.tree?({unplanted:'未种植',growing:'生长中 ('+Math.floor(p.tree.remain/60)+'分)',mature:'已成熟'}[p.tree.state]||p.tree.state):'无记录';
    let h='<h2>玩家 '+esc(p.name||p.uid)+' <span class="dimtx">#'+p.uid+'</span> '+
      (p.online?'<span class="badge b-ok">在线</span>':'')+'</h2>';
    h+='<div class="dl">'+
      '<div><span>等级 / VIP</span><b>'+p.level+' / '+p.vip+'</b></div>'+
      '<div><span>金币 / 钻石 (客户端权威)</span><b>'+(p.coin==null?'-':p.coin)+' / '+(p.key==null?'-':p.key)+'</b></div>'+
      '<div><span>农场存档</span><b>'+(p.memory_len/1024).toFixed(1)+' KB</b></div>'+
      '<div><span>商店在售</span><b>'+p.shop_selling+' 件</b></div>'+
      '<div><span>摇钱树</span><b>'+tree+'</b></div></div>';
    h+='<h3>改名</h3><div class="rowflex"><input id="rn" value="'+esc(p.name||'')+'">'+
      '<button class="act mini" onclick="rename('+p.uid+')">保存</button></div>';
    h+='<h3>好友 ('+p.friends.length+')</h3>';
    p.friends.forEach(f=>{h+='<div class="rowflex"><span>'+f.fid+' '+esc(f.name||'')+'</span>'+
      '<button class="act red mini" onclick="friendOp('+p.uid+',\'remove\','+f.fid+')">删除</button></div>';});
    h+='<div class="rowflex"><input id="nfid" placeholder="对方 uid" style="width:110px">'+
      '<button class="act mini" onclick="friendOp('+p.uid+',\'add\',null)">加好友</button></div>';
    h+='<h3>摇钱树操作</h3><div class="rowflex">'+
      '<button class="act mini" onclick="treeOp('+p.uid+',\'mature\')">⚡ 立即成熟</button>'+
      '<button class="act gray mini" onclick="treeOp('+p.uid+',\'reset\')">🔄 重置</button></div>';
    h+='<div style="margin-top:20px"><button class="act gray" onclick="closeDrawer()">关闭</button></div>';
    d.innerHTML=h;d.classList.add('open');
  }).catch(()=>{});}
function closeDrawer(){document.getElementById('drawer').classList.remove('open');}
function rename(uid){const name=document.getElementById('rn').value.trim();if(!name)return;
  api('/api/player/'+uid+'/rename',{method:'POST',body:JSON.stringify({name})})
   .then(r=>{toast(r.ok?'已改名':'失败',!r.ok);openDrawer(uid);loadPlayers();}).catch(()=>{});}
function friendOp(uid,action,fid){
  if(action==='add'){fid=parseInt(document.getElementById('nfid').value);if(!fid)return toast('输入uid',true);}
  confirmDo((action==='remove'?'删除好友 ':'添加好友 ')+fid+' ?',()=>
   api('/api/player/'+uid+'/friends',{method:'POST',body:JSON.stringify({action,fid})})
    .then(r=>{toast(r.ok?'完成':r.error,!r.ok);openDrawer(uid);}).catch(()=>{}));}
function treeOp(uid,op){api('/api/tree/'+uid+'/'+op,{method:'POST'})
  .then(r=>{toast(r.ok?'完成':r.error,!r.ok);openDrawer(uid);}).catch(()=>{});}

/* ---------- market ---------- */
function loadShops(){api('/api/shops').then(d=>{const tb=document.querySelector('#mtable tbody');
  tb.innerHTML='';d.shops.forEach(s=>{const tr=document.createElement('tr');
   tr.innerHTML='<td>'+s.uid+'</td><td>'+esc(s.name)+'</td><td>'+(s.level||'-')+
     '</td><td>'+s.selling+' / '+s.total+'</td>'+
     '<td><button class="act mini" onclick="openShop('+s.uid+')">管理摊位</button></td>';
   tb.appendChild(tr);});}).catch(()=>{});}

function openShop(uid){
  Promise.all([api('/api/shop/'+uid),api('/api/items')]).then(([s,cat])=>{
    itemsCache=cat.items;
    const m=document.getElementById('shopModal');
    let h='<h2>摊位管理 · '+esc(s.name)+' <span class="dimtx">#'+uid+'</span></h2>';
    h+='<div class="grid" style="grid-template-columns:repeat(4,1fr);gap:8px;margin:12px 0">';
    s.cells.forEach(c=>{
      const st=c.status===3?'<span class="badge b-ok">在售</span>':c.status===1?'<span class="badge b-warn">已售</span>':
        c.status===2?'<span class="badge b-dim">锁定</span>':'<span class="badge b-dim">空位</span>';
      const valid=c.itemId==null?null:c.valid;
      h+='<div class="cellcard"><b>摊位 '+c.index+' '+st+'</b>'+
        (c.itemId?('物品: '+esc(c.itemId)+(valid===false?' <span class="badge b-bad">无效ID</span>':'<br>')+'数量: '+c.amount+' · 价格: '+c.price):
          '<span class="dimtx">—</span>')+
        '<div style="margin-top:6px">'+(c.itemId?'<button class="act red mini" onclick="offshelf('+uid+','+c.index+')">下架</button>':
          (c.status===2?'<button class="act gray mini" onclick="unlock('+uid+','+c.index+')">解锁</button>':''))+'</div></div>';});
    h+='</div><h3>上架新商品</h3><div class="rowflex">';
    h+='<div class="fld">物品ID<input id="oitem" list="itemlist" style="width:170px"></div>';
    h+='<datalist id="itemlist">'+itemsCache.slice(0,400).map(i=>'<option value="'+i+'">').join('')+'</datalist>';
    h+='<div class="fld">数量<input id="oamt" type="number" value="1" style="width:80px"></div>';
    h+='<div class="fld">价格(金币)<input id="oprice" type="number" value="100" style="width:100px"></div>';
    h+='<div class="fld">摊位(可选)<input id="oidx" type="number" placeholder="自动" style="width:80px"></div>';
    h+='<button class="act" onclick="addOffer('+uid+')">上架</button>';
    h+='<button class="act red" onclick="confirmDo(\'清空该玩家全部在售商品?\',()=>clearShop('+uid+'))">清空在售</button>';
    h+='<button class="act gray" onclick="hideOvl()">关闭</button></div>';
    h+='<p class="dimtx" style="margin-top:8px">物品ID 需为 ProtoDB 合法ID(带 _01 后缀, 如 Wheat_01)。无效ID不会被客户端渲染。</p>';
    m.innerHTML=h;
    document.getElementById('ovl').style.display='flex';m.style.display='block';
    document.getElementById('login').style.display='none';
  }).catch(()=>{});}
function addOffer(uid){const itemId=document.getElementById('oitem').value.trim();
  const amount=+document.getElementById('oamt').value,price=+document.getElementById('oprice').value;
  const idxS=document.getElementById('oidx').value,idx=idxS===''?null:+idxS;
  if(itemsCache.indexOf(itemId)<0&&!idxS&&false){}
  api('/api/shop/'+uid+'/offer',{method:'POST',body:JSON.stringify({itemId,amount,price,index:idx})})
   .then(r=>{toast(r.ok?'已上架到摊位 '+r.index:r.error,!r.ok);if(r.ok)openShop(uid);}).catch(()=>{});}
function offshelf(uid,idx){api('/api/shop/'+uid+'/offshelf',{method:'POST',body:JSON.stringify({index:idx})})
  .then(r=>{toast(r.ok?'已下架':'失败',!r.ok);openShop(uid);}).catch(()=>{});}
function unlock(uid,idx){api('/api/shop/'+uid+'/unlock',{method:'POST',body:JSON.stringify({index:idx})})
  .then(r=>{toast(r.ok?'已解锁':'失败',!r.ok);openShop(uid);}).catch(()=>{});}
function clearShop(uid){api('/api/shop/'+uid+'/clear',{method:'POST'})
  .then(r=>{toast(r.ok?'已清空':'失败',!r.ok);openShop(uid);loadShops();}).catch(()=>{});}

/* ---------- trees ---------- */
function loadTrees(){api('/api/trees').then(d=>{const tb=document.querySelector('#ttable tbody');
  tb.innerHTML='';d.trees.forEach(t=>{const tr=document.createElement('tr');
   const state=t.state==='growing'?'<span class="badge b-warn">生长中 '+Math.floor(t.remain/60)+'分</span>':
     t.state==='mature'?'<span class="badge b-ok">已成熟</span>':'<span class="badge b-dim">未种植</span>';
   tr.innerHTML='<td>'+t.uid+'</td><td>'+esc(t.name)+'</td><td>'+t.level+'</td><td>'+state+'</td>'+
    '<td>'+t.output+'</td><td>'+t.left+'</td><td>'+t.stolen+'</td>'+
    '<td><button class="act mini" onclick="treeOp2('+t.uid+',\'mature\')">⚡成熟</button> '+
    '<button class="act gray mini" onclick="treeOp2('+t.uid+',\'reset\')">重置</button></td>';
   tb.appendChild(tr);});}).catch(()=>{});}
function treeOp2(uid,op){api('/api/tree/'+uid+'/'+op,{method:'POST'})
  .then(r=>{toast(r.ok?'完成':r.error,!r.ok);loadTrees();}).catch(()=>{});}

/* ---------- log ---------- */
function toggleAuto(){autoLog=!autoLog;
  document.getElementById('lauto').textContent=autoLog?'⏸ 暂停自动刷新':'▶ 恢复自动刷新';}
function loadLog(force){if(!force&&!autoLog)return;
  const t=document.getElementById('ltype').value,u=document.getElementById('luid').value.trim(),
        q=document.getElementById('lq').value.trim();
  api('/api/log?n=200&type='+t+'&uid='+encodeURIComponent(u)+'&q='+encodeURIComponent(q))
   .then(d=>{
     const box=document.getElementById('logbox');
     const stick=box.scrollTop+box.clientHeight>=box.scrollHeight-30;
     box.textContent=d.lines.join('\n')||'(无匹配日志)';
     if(stick)box.scrollTop=box.scrollHeight;
   }).catch(()=>{});
  api('/api/stats').then(d=>{const el=document.getElementById('stats');
    const max=d.stats[0]?d.stats[0].count:1;
    el.innerHTML=d.stats.map(s=>'<div class="rowflex" style="margin:4px 0">'+
     '<span class="mono" style="width:52%;overflow:hidden;text-overflow:ellipsis">'+esc(s.endpoint)+'</span>'+
     '<div class="bar" style="width:'+Math.max(2,s.count/max*42)+'%"></div>'+
     '<span class="dimtx">'+s.count+'</span></div>').join('')||'<span class="dimtx">暂无</span>';
  }).catch(()=>{});}

/* ---------- confirm ---------- */
let cfCb=null;
function confirmDo(text,cb){document.getElementById('cfText').textContent=text;cfCb=cb;
  document.getElementById('ovl').style.display='flex';
  document.getElementById('confirmModal').style.display='block';
  document.getElementById('login').style.display='none';
  document.getElementById('shopModal').style.display='none';}
function hideConfirm(){document.getElementById('confirmModal').style.display='none';hideOvl();}
document.getElementById('cfYes').onclick=()=>{hideConfirm();cfCb&&cfCb();};

/* ---------- boot ---------- */
/* ---------- notice ---------- */
function loadNotices(){api('/api/notices').then(d=>{
  const tb=document.querySelector('#ntable tbody');tb.innerHTML='';
  d.notices.forEach(n=>{const tr=document.createElement('tr');
   tr.innerHTML='<td>'+n.id+'</td><td style="max-width:350px;overflow:hidden;text-overflow:ellipsis">'+
    esc(n.desc)+'</td><td>'+esc(n.picname||'-')+'</td><td>'+n.type+
    '</td><td><button class="act red mini" onclick="delNotice('+n.id+')">删除</button></td>';
   tb.appendChild(tr);});
}).catch(()=>{});}
function addNotice(){const desc=document.getElementById('n_desc').value.trim();
  if(!desc)return toast('描述不能为空',true);
  api('/api/notice/add',{method:'POST',body:JSON.stringify({
    desc:desc,picname:document.getElementById('n_pic').value.trim(),
    type:document.getElementById('n_type').value||'0',
    giftId:+document.getElementById('n_gift').value||0})})
   .then(r=>{toast(r.ok?'公告已添加':'失败',!r.ok);
    document.getElementById('n_desc').value='';loadNotices();}).catch(()=>{});}
function delNotice(id){confirmDo('删除公告 #'+id+' ?',()=>
 api('/api/notice/delete',{method:'POST',body:JSON.stringify({id})})
  .then(r=>{toast(r.ok?'已删除':'失败',!r.ok);loadNotices();}).catch(()=>{}));}

/* ---------- mail ---------- */
function sendMail(){const uid=+document.getElementById('m_uid').value;
  const reward=document.getElementById('m_reward').value.trim();
  const desc=document.getElementById('m_desc').value.trim();
  if(!uid||!reward)return toast('uid和奖励不能为空',true);
  api('/api/mail/send',{method:'POST',body:JSON.stringify({uid,reward,desc})})
   .then(r=>{toast(r.ok?'邮件已发送':'失败',!r.ok);
    document.getElementById('m_desc').value='';loadMails();}).catch(()=>{});}
function loadMails(){const uid=+document.getElementById('m_filter_uid').value||0;
  if(!uid){document.querySelector('#mtable2 tbody').innerHTML='';return;}
  api('/api/mail/list?uid='+uid).then(d=>{
   const tb=document.querySelector('#mtable2 tbody');tb.innerHTML='';
   d.mails.forEach(m=>{const tr=document.createElement('tr');
    tr.innerHTML='<td>'+m.id+'</td><td>'+m.uid+'</td><td>'+esc(m.reward)+'</td>'+
     '<td style="max-width:260px;overflow:hidden;text-overflow:ellipsis">'+esc(m.desc)+'</td>'+
     '<td class="mono">'+fmtTime(m.created)+'</td>'+
     '<td><button class="act red mini" onclick="delMail('+m.id+')">删除</button></td>';
    tb.appendChild(tr);});
  }).catch(()=>{});}
function delMail(id){api('/api/mail/delete',{method:'POST',body:JSON.stringify({id})})
  .then(r=>{toast(r.ok?'已删除':'失败',!r.ok);loadMails();}).catch(()=>{});}

/* ---------- settings ---------- */
function loadSettings(){
  api('/api/config').then(d=>{
   document.getElementById('cfg_grow').value=d.config.tree_grow_seconds||7200;
   document.getElementById('cfg_base').value=d.config.tree_output_base||100;
   document.getElementById('cfg_per').value=d.config.tree_output_per_level||20;
  }).catch(()=>{});
  api('/api/signrewards').then(d=>{
   const el=document.getElementById('signrewards');
   el.innerHTML='';
   (d.rewards||[]).forEach((r,i)=>{
    el.innerHTML+='<div class="rowflex" style="margin:4px 0">'+
     '<span class="dimtx" style="width:50px">第'+(i+1)+'天</span>'+
     '<input value="'+esc(r.awardtype1||'')+'" data-r="'+i+'" data-f="awardtype1" style="width:120px" placeholder="物品1">'+
     '<input type="number" value="'+(r.num1||0)+'" data-r="'+i+'" data-f="num1" style="width:70px">'+
     '<input value="'+esc(r.awardtype2||'')+'" data-r="'+i+'" data-f="awardtype2" style="width:120px" placeholder="物品2">'+
     '<input type="number" value="'+(r.num2||0)+'" data-r="'+i+'" data-f="num2" style="width:70px">'+
     '<input value="'+esc(r.awardtype3||'')+'" data-r="'+i+'" data-f="awardtype3" style="width:120px" placeholder="物品3">'+
     '<input type="number" value="'+(r.num3||0)+'" data-r="'+i+'" data-f="num3" style="width:70px">'+
     '</div>';});
  }).catch(()=>{});
  loadBackups();
}
function saveConfig(){const cfg={};
  cfg.tree_grow_seconds=document.getElementById('cfg_grow').value;
  cfg.tree_output_base=document.getElementById('cfg_base').value;
  cfg.tree_output_per_level=document.getElementById('cfg_per').value;
  api('/api/config',{method:'POST',body:JSON.stringify(cfg)})
   .then(r=>toast(r.ok?'配置已保存':'失败',!r.ok)).catch(()=>{});}
function saveSignRewards(){
  const rewards=[];
  document.querySelectorAll('#signrewards input[data-r]').forEach(inp=>{
   const ri=+inp.dataset.r,f=inp.dataset.f;
   if(!rewards[ri])rewards[ri]={};
   rewards[ri][f]=isNaN(+inp.value)?inp.value:+inp.value;});
  api('/api/signrewards',{method:'POST',body:JSON.stringify({rewards})})
   .then(r=>toast(r.ok?'签到奖励已保存':'失败',!r.ok)).catch(()=>{});}
function loadBackups(){api('/api/backups').then(d=>{
  const el=document.getElementById('backuplist');
  el.innerHTML=(d.backups||[]).map(b=>
   '<div class="rowflex" style="margin:3px 0"><span class="mono">'+b+'</span>'+
   '<button class="act red mini" onclick="confirmDo(\'恢复备份 '+b+' ? 当前数据将被覆盖!\',()=>restoreBak(\''+b+'\'))">恢复</button></div>'
  ).join('')||'<span class="dimtx">暂无备份</span>';
 }).catch(()=>{});}
function restoreBak(f){api('/api/backup/restore',{method:'POST',body:JSON.stringify({file:f})})
  .then(r=>toast(r.ok?'已恢复,建议重启game server':'失败',!r.ok)).catch(()=>{});}
function clearLog(){api('/api/log/clear',{method:'POST',body:'{}'})
  .then(r=>toast(r.ok?'日志已清空':'失败',!r.ok)).catch(()=>{});}
if(!TOKEN){showLogin();}
else api('/api/status').then(()=>{refresh();}).catch(()=>{});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeDrawer();hideOvl();}});
refresh();
</script>
</body>
</html>"""


def _bump_notice_ver(conn):
    row = conn.execute("SELECT v FROM kv WHERE k='notice_version'").fetchone()
    nv = str(int(row["v"]) + 1) if row else "1"
    conn.execute("INSERT OR REPLACE INTO kv(k,v) VALUES ('notice_version',?)", (nv,))


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "BearFarmGUI/1.0"

    def log_message(self, fmt, *args):
        pass

    # ---- helpers ----
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (ConnectionResetError, BrokenPipeError):
            pass

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _authed(self):
        tok = self.headers.get("X-Token") or ""
        return tok == TOKEN

    def _body(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n) if n else b""
            return json.loads(raw.decode("utf-8", "replace")) if raw else {}
        except Exception:
            return {}

    # ---- routes ----
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        path = u.path
        q = urllib.parse.parse_qs(u.query)

        if path == "/" or path == "/index.html":
            self._send(200, HTML, "text/html; charset=utf-8")
            return

        if path.startswith("/api/"):
            if not self._authed():
                self._json({"error": "unauthorized"}, 401)
                return
            try:
                self._api_get(path, q)
            except Exception as e:
                self._json({"error": str(e)}, 500)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        path = u.path
        if path.startswith("/api/"):
            if not self._authed():
                self._json({"error": "unauthorized"}, 401)
                return
            try:
                self._api_post(path, self._body())
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, 500)

    def _api_get(self, path, q):
        conn = db()
        try:
            if path == "/api/status":
                self._json(api_status(conn))
            elif path == "/api/players":
                self._json(api_players(conn, (q.get("q") or [""])[0].strip()))
            elif path.startswith("/api/player/"):
                uid = int(path.split("/")[3])
                data = api_player(conn, uid)
                if data is None:
                    self._json({"error": "玩家不存在"}, 404)
                else:
                    self._json(data)
            elif path == "/api/shops":
                self._json(api_shops(conn))
            elif path.startswith("/api/shop/"):
                uid = int(path.split("/")[3])
                data = api_shop(conn, uid, set(load_items()))
                if data is None:
                    self._json({"error": "没有商店数据"}, 404)
                else:
                    self._json(data)
            elif path == "/api/items":
                items = load_items()
                kw = (q.get("q") or [""])[0].strip().lower()
                if kw:
                    items = [i for i in items if kw in i.lower()]
                self._json({"items": items[:400], "total": len(items)})
            elif path == "/api/trees":
                self._json(api_trees(conn))
            elif path == "/api/log":
                n = min(int((q.get("n") or [200])[0]), 1000)
                ltype = (q.get("type") or [""])[0]
                uid = (q.get("uid") or [""])[0]
                kw = (q.get("q") or [""])[0]
                lines = []
                for l in tail_log(n):
                    if ltype and ltype not in l:
                        continue
                    if uid and ("'%s'" % uid) not in l:
                        continue
                    if kw and kw not in l:
                        continue
                    lines.append(l.rstrip())
                self._json({"lines": lines})
            elif path == "/api/stats":
                self._json({"stats": log_stats()})
            elif path == "/api/notices":
                rows = conn.execute("SELECT * FROM notices ORDER BY id").fetchall()
                self._json({"notices": [dict(r) for r in rows]})
            elif path == "/api/signrewards":
                row = conn.execute("SELECT v FROM kv WHERE k='sign_rewards'").fetchone()
                raw = row["v"] if row else None
                try:
                    self._json({"rewards": json.loads(raw) if raw else []})
                except Exception:
                    self._json({"rewards": []})
            elif path == "/api/mail/list":
                uid = int((q.get("uid") or [0])[0])
                rows = conn.execute("SELECT * FROM mails WHERE uid=? ORDER BY id DESC",
                                    (uid,)).fetchall()
                self._json({"mails": [dict(r) for r in rows]})
            elif path == "/api/config":
                rows = conn.execute("SELECT k,v FROM kv WHERE k IN "
                                    "('tree_grow_seconds','tree_output_base','tree_output_per_level')").fetchall()
                self._json({"config": {r["k"]: r["v"] for r in rows}})
            elif path == "/api/backups":
                d = os.path.dirname(DB_PATH)
                baks = sorted([f for f in os.listdir(d) if f.endswith(".bak")], reverse=True)
                self._json({"backups": baks})
            else:
                self._json({"error": "not found"}, 404)
        finally:
            conn.close()

    def _api_post(self, path, body):
        conn = db()
        try:
            if path == "/api/backup":
                ts = time.strftime("%Y%m%d_%H%M%S")
                dst = DB_PATH + f".{ts}.bak"
                shutil.copy2(DB_PATH, dst)
                self._json({"ok": True, "file": os.path.basename(dst)})
            elif path == "/api/backup/restore":
                fname = body.get("file", "")
                src = os.path.join(os.path.dirname(DB_PATH), fname)
                if not os.path.exists(src) or not fname.endswith(".bak"):
                    self._json({"ok": False, "error": "备份文件不存在"})
                    return
                shutil.copy2(src, DB_PATH)
                self._json({"ok": True})
            elif path == "/api/log/clear":
                open(LOG_PATH, "w").close()
                self._json({"ok": True})
            elif path == "/api/player/create":
                name = str(body.get("name", "")).strip() or f"player{now_ts()}"
                face = int(body.get("face", 1))
                level = int(body.get("level", 1))
                uid = now_ts()
                conn.execute("INSERT INTO users(uid, guid, name, face, level, reg_time, login_time) "
                             "VALUES (?,?,?,?,?,?,?)",
                             (uid, f"gui-{uid}", name, face, level, now_ts(), now_ts()))
                cells = [empty_cell(i) for i in range(8)]
                shop = {"shop": {"cells": cells, "face": face, "faceData": "0",
                                 "faceType": 0, "level": level, "name": name,
                                 "uId": str(uid), "shopStatus": 1}}
                conn.execute("INSERT INTO archives(uid, shop, updated) VALUES (?,?,?)",
                             (uid, json.dumps(shop, ensure_ascii=False), now_ts()))
                conn.commit()
                self._json({"ok": True, "uid": uid})
            elif path.startswith("/api/player/") and "/delete" in path:
                uid = int(path.split("/")[3])
                for tbl in ("users", "archives", "trees"):
                    conn.execute(f"DELETE FROM {tbl} WHERE uid=?", (uid,))
                conn.execute("DELETE FROM friends WHERE uid=? OR fid=?", (uid, uid))
                conn.execute("DELETE FROM mails WHERE uid=?", (uid,))
                conn.commit()
                self._json({"ok": True})
            elif "/rename" in path:
                uid = int(path.split("/")[3])
                name = str(body.get("name", "")).strip()
                if not name:
                    self._json({"ok": False, "error": "名字不能为空"})
                    return
                conn.execute("UPDATE users SET name=? WHERE uid=?", (name, uid))
                conn.commit()
                self._json({"ok": True})
            elif "/friends" in path:
                uid = int(path.split("/")[3])
                action, fid = body.get("action"), int(body.get("fid", 0))
                if action == "add":
                    conn.execute("INSERT OR IGNORE INTO friends(uid,fid,created) VALUES (?,?,?)",
                                 (uid, fid, now_ts()))
                elif action == "remove":
                    conn.execute("DELETE FROM friends WHERE uid=? AND fid=?", (uid, fid))
                else:
                    self._json({"ok": False, "error": "未知操作"})
                    return
                conn.commit()
                self._json({"ok": True})
            elif path.endswith("/offer"):
                uid = int(path.split("/")[3])
                self._json(do_offer(conn, uid, body))
            elif path.endswith("/clear"):
                uid = int(path.split("/")[3])
                self._json(do_clear(conn, uid))
            elif path.endswith("/unlock"):
                uid = int(path.split("/")[3])
                self._json(do_unlock(conn, uid, body))
            elif path.endswith("/offshelf"):
                uid = int(path.split("/")[3])
                self._json(do_offshelf(conn, uid, body))
            elif path.endswith("/mature"):
                uid = int(path.split("/")[3])
                conn.execute("UPDATE trees SET status=2 WHERE uid=?", (uid,))
                conn.commit()
                self._json({"ok": True})
            elif path.endswith("/reset"):
                uid = int(path.split("/")[3])
                conn.execute("DELETE FROM trees WHERE uid=?", (uid,))
                conn.commit()
                self._json({"ok": True})
            elif path.endswith("/plant"):
                uid = int(path.split("/")[3])
                level = int(body.get("level", 1))
                guang = int(body.get("guang", 1))
                grow = int(conn.execute("SELECT v FROM kv WHERE k='tree_grow_seconds'").fetchone()["v"]) \
                    if conn.execute("SELECT v FROM kv WHERE k='tree_grow_seconds'").fetchone() else 7200
                base = int(conn.execute("SELECT v FROM kv WHERE k='tree_output_base'").fetchone()["v"]) \
                    if conn.execute("SELECT v FROM kv WHERE k='tree_output_base'").fetchone() else 100
                per = int(conn.execute("SELECT v FROM kv WHERE k='tree_output_per_level'").fetchone()["v"]) \
                    if conn.execute("SELECT v FROM kv WHERE k='tree_output_per_level'").fetchone() else 20
                output = base + level * per + guang * (per // 2)
                conn.execute("INSERT OR REPLACE INTO trees(uid, level, guang_level, status, "
                             "planted_at, grow_seconds, output, left_count, steal_count, def_count, plus_count) "
                             "VALUES (?,?,?,1,?,?,?,?,0,0,0)",
                             (uid, level, guang, now_ts(), grow, output, output))
                conn.commit()
                self._json({"ok": True, "output": output})
            elif path.endswith("/setoutput"):
                uid = int(path.split("/")[3])
                output = int(body.get("output", 100))
                conn.execute("UPDATE trees SET output=?, left_count=? WHERE uid=?",
                             (output, output, uid))
                conn.commit()
                self._json({"ok": True})
            elif path == "/api/mail/send":
                uid = int(body.get("uid", 0))
                reward = str(body.get("reward", "")).strip()
                desc = str(body.get("desc", "")).strip()
                if not uid or not reward:
                    self._json({"ok": False, "error": "uid和奖励不能为空"})
                    return
                conn.execute("INSERT INTO mails(uid, reward, desc, created, read) "
                             "VALUES (?,?,?, ?,0)", (uid, reward, desc, now_ts()))
                conn.commit()
                self._json({"ok": True})
            elif path == "/api/mail/delete":
                conn.execute("DELETE FROM mails WHERE id=?", (int(body.get("id", 0)),))
                conn.commit()
                self._json({"ok": True})
            elif path == "/api/notice/add":
                conn.execute("INSERT INTO notices(picname,type,desc,gift_id,posbtnx,posbtny,poslabx,poslaby) "
                             "VALUES (?,?,?,?,?,?,?,?)",
                             (body.get("picname", ""), body.get("type", "0"),
                              body.get("desc", ""), int(body.get("giftId", 0)),
                              int(body.get("posbtnx", 0)), int(body.get("posbtny", 0)),
                              int(body.get("poslabx", 0)), int(body.get("poslaby", 0))))
                _bump_notice_ver(conn)
                conn.commit()
                self._json({"ok": True})
            elif path == "/api/notice/delete":
                conn.execute("DELETE FROM notices WHERE id=?", (int(body.get("id", 0)),))
                _bump_notice_ver(conn)
                conn.commit()
                self._json({"ok": True})
            elif path == "/api/notice/version":
                _bump_notice_ver(conn)
                conn.commit()
                self._json({"ok": True})
            elif path == "/api/signrewards":
                rewards = json.dumps(body.get("rewards", []), ensure_ascii=False)
                conn.execute("INSERT OR REPLACE INTO kv(k,v) VALUES ('sign_rewards',?)", (rewards,))
                conn.commit()
                self._json({"ok": True})
            elif path == "/api/config":
                for k, v in body.items():
                    conn.execute("INSERT OR REPLACE INTO kv(k,v) VALUES (?,?)", (k, str(v)))
                conn.commit()
                self._json({"ok": True})
            else:
                self._json({"ok": False, "error": "not found"}, 404)
        finally:
            conn.close()


def main():
    port = 8090
    host = "127.0.0.1"
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--host" and i + 1 < len(args):
            host = args[i + 1]
            i += 2
        else:
            port = int(args[i])
            i += 1

    if not os.path.exists(DB_PATH):
        print(f"[gui] 数据库不存在: {DB_PATH} — 请先启动 game server")
        sys.exit(1)

    ensure_token()
    srv = ThreadingHTTPServer((host, port), Handler)
    print("=" * 52)
    print("  熊大农场 私服控制台")
    print(f"  地址:   http://{host}:{port}")
    print(f"  Token:  {TOKEN}")
    print(f"  绑定:   {host}  (局域网访问请加 --host 0.0.0.0)")
    print("=" * 52)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
