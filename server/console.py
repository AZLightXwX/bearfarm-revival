"""BearFarm 私服运维控制台.

与正在运行的服务器共享同一个 SQLite 数据库和日志文件，
可在不重启服务器的情况下实时管理玩家/集市/摇钱树。

用法:  python console.py
"""
import json
import os
import re
import shutil
import sqlite3
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "data", "bearfarm.db")
LOG_PATH = os.path.join(BASE, "server.log")


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


def now():
    return int(time.time())


def ts_str(ts):
    if not ts:
        return "-"
    return time.strftime("%m-%d %H:%M:%S", time.localtime(ts))


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
        conn.execute("INSERT INTO archives(uid, shop, updated) VALUES (?,?,?)", (uid, payload, now()))
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


# ---------------- commands ----------------

def cmd_help(a):
    print("""可用命令:
  status                       服务器状态(端口/在线/请求量)
  players [数量]                玩家列表
  player <uid>                 玩家详情(角色/好友/树/商店)
  online [秒]                  最近N秒心跳在线的玩家(默认60)
  tree <uid>                   查看摇钱树
  tree <uid> mature|reset      立即成熟 / 重置
  shop <uid>                   查看商店摊位
  shop <uid> add <物品ID> <数量> <价格> [摊位号]   上架商品
  shop <uid> clear             清空在售商品
  friends <uid>                好友列表
  friends <uid> add|remove <对方uid>              加/删好友
  rename <uid> <新名字>         改名(服务器侧)
  stats [数量]                 按端点统计请求数
  log [条数]                   查看最近日志(默认20)
  backup                       备份数据库
  quit                         退出控制台""")


def cmd_status(a):
    import socket
    ports = []
    for p in (8080, 80, 60000, 8100):
        s = socket.socket()
        s.settimeout(0.3)
        try:
            s.connect(("127.0.0.1", p))
            ports.append(f":{p}√")
        except Exception:
            ports.append(f":{p}×")
        finally:
            s.close()
    conn = db()
    n_users = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
    n_online = conn.execute("SELECT COUNT(*) c FROM users WHERE last_seen > ?",
                           (now() - 60,)).fetchone()["c"]
    conn.close()
    print(f"端口: {' '.join(ports)}")
    print(f"注册玩家: {n_users}    在线(60s心跳): {n_online}")
    print(f"数据库: {DB_PATH}")
    print(f"日志:   {LOG_PATH}")


def cmd_players(a):
    n = int(a[0]) if a else 20
    conn = db()
    rows = conn.execute(
        "SELECT u.uid, u.name, u.level, u.vip, u.last_seen, "
        "(SELECT COUNT(*) FROM friends f WHERE f.uid=u.uid) nfriends "
        "FROM users u ORDER BY u.last_seen DESC, u.uid LIMIT ?", (n,)).fetchall()
    conn.close()
    print(f"{'uid':<8}{'名字':<12}{'等级':<6}{'好友':<6}{'最近活跃':<14}")
    for r in rows:
        print(f"{r['uid']:<8}{(r['name'] or '-'):<12}{r['level']:<6}{r['nfriends']:<6}{ts_str(r['last_seen']):<14}")


def cmd_player(a):
    if not a:
        print("用法: player <uid>")
        return
    uid = int(a[0])
    conn = db()
    u = conn.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()
    if not u:
        print("玩家不存在")
        conn.close()
        return
    print(f"uid={u['uid']}  名字={u['name']}  等级={u['level']}  vip={u['vip']}  "
          f"face={u['face']}  最近活跃={ts_str(u['last_seen'])}")
    arch = conn.execute("SELECT role, length(memory) mlen, length(shop) slen, updated "
                         "FROM archives WHERE uid=?", (uid,)).fetchone()
    if arch:
        print(f"存档: memory={arch['mlen']}B shop={arch['slen']}B 更新于 {ts_str(arch['updated'])}")
        if arch["role"]:
            role = json.loads(arch["role"])
            print(f"角色: coin={role.get('coin')} key={role.get('key')} level={role.get('level')}")
    else:
        print("存档: 无")
    friends = conn.execute("SELECT fid FROM friends WHERE uid=?", (uid,)).fetchall()
    if friends:
        print("好友: " + ", ".join(str(f["fid"]) for f in friends))
    t = conn.execute("SELECT * FROM trees WHERE uid=?", (uid,)).fetchone()
    if t:
        remain = t["planted_at"] + t["grow_seconds"] - now()
        st = {0: "未种植", 1: f"生长中(剩{max(0, remain)}s)", 2: "已成熟", 3: "?"}.get(t["status"], "?")
        print(f"摇钱树: {st} 产出={t['output']} 剩余={t['left_count']} 被偷={t['steal_count']}")
    shop = get_shop(conn, uid)
    conn.close()
    if shop:
        cells = shop.get("cells", [])
        selling = [c for c in cells if c.get("status") == 3]
        print(f"商店: {len(selling)} 件在售, 名字={shop.get('name')}, uId={shop.get('uId')}")


def cmd_online(a):
    secs = int(a[0]) if a else 60
    conn = db()
    rows = conn.execute("SELECT uid, name, level, last_seen FROM users "
                        "WHERE last_seen > ? ORDER BY last_seen DESC", (now() - secs,)).fetchall()
    conn.close()
    if not rows:
        print(f"最近 {secs}s 无在线玩家")
        return
    print(f"最近 {secs}s 在线 {len(rows)} 人:")
    for r in rows:
        print(f"  {r['uid']:<8}{(r['name'] or '-'):<12}Lv{r['level']:<4}{ts_str(r['last_seen'])}")


def cmd_tree(a):
    if not a:
        print("用法: tree <uid> [mature|reset]")
        return
    uid = int(a[0])
    op = a[1] if len(a) > 1 else ""
    conn = db()
    if op == "mature":
        row = conn.execute("SELECT * FROM trees WHERE uid=?", (uid,)).fetchone()
        if not row:
            print("该玩家没有摇钱树记录")
        else:
            conn.execute("UPDATE trees SET status=2 WHERE uid=?", (uid,))
            conn.commit()
            print(f"uid {uid} 摇钱树已置为成熟(产出 {row['output']} 剩余 {row['left_count']})")
        conn.close()
        return
    if op == "reset":
        conn.execute("DELETE FROM trees WHERE uid=?", (uid,))
        conn.commit()
        conn.close()
        print(f"uid {uid} 摇钱树已重置(下次进游戏走本地)")
        return
    row = conn.execute("SELECT * FROM trees WHERE uid=?", (uid,)).fetchone()
    conn.close()
    if not row:
        print("没有摇钱树记录")
        return
    remain = row["planted_at"] + row["grow_seconds"] - now()
    st = {0: "未种植", 1: f"生长中(剩 {max(0, remain)}s)", 2: "已成熟"}.get(row["status"], str(row["status"]))
    print(f"uid={row['uid']} 等级={row['level']} 状态={st} 产出={row['output']} "
          f"剩余={row['left_count']} 被偷={row['steal_count']} 被抓={row['def_count']}")


def cmd_shop(a):
    if len(a) < 1:
        print("用法: shop <uid> [add <物品ID> <数量> <价格> [摊位号] | clear]")
        return
    uid = int(a[0])
    conn = db()
    if len(a) >= 2 and a[1] == "add":
        if len(a) < 5:
            print("用法: shop <uid> add <物品ID> <数量> <价格> [摊位号]")
            conn.close()
            return
        item, amount, price = a[2], int(a[3]), int(a[4])
        idx = int(a[5]) if len(a) > 5 else None
        shop = get_shop(conn, uid) or {"cells": [], "face": 1, "faceData": "0", "faceType": 0,
                                       "level": 1, "name": f"player{uid}", "uId": str(uid),
                                       "shopStatus": 1}
        cells = norm_cells(shop)
        if idx is None:
            idx = next((i for i, c in enumerate(cells)
                        if c.get("status") in (0, 2) and not c.get("itemId")), 0)
        if not (0 <= idx < 8):
            print("摊位号需为 0-7")
            conn.close()
            return
        cells[idx] = {"id": None, "itemId": item, "amount": amount, "price": price,
                      "costItem": "coin", "status": 3, "seller": str(uid), "buyer": None,
                      "voyage": 0, "createdAt": now(), "autoBuy": False, "autobuyTime": 0,
                      "index": idx, "buyed": False}
        save_shop(conn, uid, shop)
        print(f"已为 uid {uid} 摊位{idx} 上架: {item} x{amount} @ {price}金币")
        conn.close()
        return
    if len(a) >= 2 and a[1] == "clear":
        shop = get_shop(conn, uid)
        if shop:
            for i, c in enumerate(norm_cells(shop)):
                if c.get("status") == 3:
                    norm_cells(shop)[i] = empty_cell(i)
            save_shop(conn, uid, shop)
            print(f"已清空 uid {uid} 的在售商品")
        else:
            print("该玩家没有商店数据")
        conn.close()
        return
    shop = get_shop(conn, uid)
    conn.close()
    if not shop:
        print("该玩家没有商店数据")
        return
    print(f"商店: {shop.get('name')} (uId={shop.get('uId')}, 等级{shop.get('level')})")
    for c in shop.get("cells", []):
        if c.get("status") == 3:
            print(f"  摊位{c['index']}: {c['itemId']} x{c['amount']} @ {c['price']}金币 "
                  f"(seller={c.get('seller')})")
        elif c.get("itemId"):
            print(f"  摊位{c['index']}: {c['itemId']} x{c['amount']} @ {c['price']} "
                  f"[status={c['status']}]")
        else:
            print(f"  摊位{c['index']}: {'空位' if c.get('status') == 0 else '锁定'}")


def cmd_friends(a):
    if not a:
        print("用法: friends <uid> [add|remove <对方uid>]")
        return
    uid = int(a[0])
    conn = db()
    if len(a) >= 3 and a[1] in ("add", "remove"):
        fid = int(a[2])
        if a[1] == "add":
            conn.execute("INSERT OR IGNORE INTO friends(uid,fid,created) VALUES (?,?,?)",
                         (uid, fid, now()))
            conn.commit()
            print(f"已添加: {uid} → {fid}")
        else:
            conn.execute("DELETE FROM friends WHERE uid=? AND fid=?", (uid, fid))
            conn.commit()
            print(f"已删除: {uid} → {fid}")
    rows = conn.execute("SELECT f.fid, u.name, u.level FROM friends f "
                        "LEFT JOIN users u ON u.uid=f.fid WHERE f.uid=?", (uid,)).fetchall()
    conn.close()
    print(f"uid {uid} 的好友 ({len(rows)}):")
    for r in rows:
        print(f"  {r['fid']:<8}{(r['name'] or '-'):<12}Lv{r['level'] or 1}")


def cmd_rename(a):
    if len(a) < 2:
        print("用法: rename <uid> <新名字>")
        return
    uid, name = int(a[0]), a[1]
    conn = db()
    conn.execute("UPDATE users SET name=? WHERE uid=?", (name, uid))
    conn.commit()
    conn.close()
    print(f"uid {uid} 已改名为 {name} (好友列表可见)")


def cmd_stats(a):
    if not os.path.exists(LOG_PATH):
        print("暂无日志")
        return
    n = int(a[0]) if a else 5000
    lines = open(LOG_PATH, encoding="utf-8", errors="replace").readlines()[-n:]
    pat = re.compile(r"\[.*?\] (FZ|API) (\S+)")
    from collections import Counter
    c = Counter()
    for line in lines:
        m = pat.search(line)
        if m:
            key = m.group(2).split("?")[0]
            if "logic" in line:
                lm = re.search(r"'logic': '([^']+)'", line)
                if lm:
                    key += f"?{lm.group(1)}"
            c[f"{m.group(1)} {key}"] += 1
    if not c:
        print("日志中无请求记录")
        return
    print(f"最近日志中的请求统计 (采样{len(lines)}行):")
    for k, v in c.most_common(20):
        print(f"  {v:>6}  {k}")


def cmd_log(a):
    n = int(a[0]) if a else 20
    if not os.path.exists(LOG_PATH):
        print("暂无日志")
        return
    lines = open(LOG_PATH, encoding="utf-8", errors="replace").readlines()[-n:]
    for line in lines:
        print(line.rstrip())


def cmd_backup(a):
    ts = time.strftime("%Y%m%d_%H%M%S")
    dst = DB_PATH + f".{ts}.bak"
    shutil.copy2(DB_PATH, dst)
    print(f"已备份到: {dst}")


COMMANDS = {
    "help": cmd_help, "h": cmd_help, "?": cmd_help,
    "status": cmd_status,
    "players": cmd_players, "ls": cmd_players,
    "player": cmd_player, "p": cmd_player,
    "online": cmd_online,
    "tree": cmd_tree,
    "shop": cmd_shop,
    "friends": cmd_friends,
    "rename": cmd_rename,
    "stats": cmd_stats,
    "log": cmd_log,
    "backup": cmd_backup,
    "quit": lambda a: sys.exit(0),
    "exit": lambda a: sys.exit(0),
}


def main():
    if not os.path.exists(DB_PATH):
        print(f"数据库不存在: {DB_PATH} — 请先启动服务器 (python main.py)")
        sys.exit(1)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print("熊出没之熊大农场 私服控制台  (输入 help 查看命令)")
    while True:
        try:
            raw = input("bearfarm> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        parts = raw.split()
        cmd, args = parts[0].lower(), parts[1:]
        fn = COMMANDS.get(cmd)
        if fn:
            try:
                fn(args)
            except Exception as e:
                print(f"错误: {e}")
        else:
            print(f"未知命令: {cmd}  (help 查看帮助)")


if __name__ == "__main__":
    main()
