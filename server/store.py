"""SQLite storage for the BearFarm private server."""
import json
import os
import sqlite3
import threading
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "bearfarm.db")
_lock = threading.Lock()
_conn = None


def init():
    global _conn
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    _conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    _conn.row_factory = sqlite3.Row
    _conn.execute("PRAGMA journal_mode=WAL")
    # migrations
    cols = {r["name"] for r in _conn.execute("PRAGMA table_info(users)")}
    if "last_seen" not in cols:
        _conn.execute("ALTER TABLE users ADD COLUMN last_seen INTEGER DEFAULT 0")
    _conn.commit()
    _conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY,
            guid TEXT,
            name TEXT DEFAULT '',
            face INTEGER DEFAULT 1,
            face_type INTEGER DEFAULT 0,
            sex INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            vip INTEGER DEFAULT 0,
            age_group INTEGER DEFAULT 0,
            uuid TEXT DEFAULT '',
            channel_id TEXT DEFAULT '',
            reg_time INTEGER DEFAULT 0,
            login_time INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS archives (
            uid INTEGER PRIMARY KEY,
            role TEXT DEFAULT '',
            memory TEXT DEFAULT '',
            shop TEXT DEFAULT '',
            updated INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS friends (
            uid INTEGER NOT NULL,
            fid INTEGER NOT NULL,
            created INTEGER DEFAULT 0,
            PRIMARY KEY (uid, fid)
        );
        CREATE TABLE IF NOT EXISTS trees (
            uid INTEGER PRIMARY KEY,
            level INTEGER DEFAULT 1,
            guang_level INTEGER DEFAULT 1,
            status INTEGER DEFAULT 0,
            planted_at INTEGER DEFAULT 0,
            grow_seconds INTEGER DEFAULT 0,
            output INTEGER DEFAULT 0,
            left_count INTEGER DEFAULT 0,
            steal_count INTEGER DEFAULT 0,
            def_count INTEGER DEFAULT 0,
            plus_count INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS kv (
            k TEXT PRIMARY KEY,
            v TEXT
        );
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            picname TEXT DEFAULT '',
            type TEXT DEFAULT '0',
            desc TEXT DEFAULT '',
            gift_id INTEGER DEFAULT 0,
            posbtnx INTEGER DEFAULT 0,
            posbtny INTEGER DEFAULT 0,
            poslabx INTEGER DEFAULT 0,
            poslaby INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS mails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER NOT NULL,
            reward TEXT DEFAULT '',
            desc TEXT DEFAULT '',
            created INTEGER DEFAULT 0,
            read INTEGER DEFAULT 0
        );
        """
    )
    _conn.commit()


def q(sql, args=()):
    with _lock:
        cur = _conn.execute(sql, args)
        rows = cur.fetchall()
        _conn.commit()
        return rows


def q1(sql, args=()):
    rows = q(sql, args)
    return rows[0] if rows else None


def now():
    return int(time.time())


def upsert_user(uid, guid="", name="", **kw):
    row = q1("SELECT uid FROM users WHERE uid=?", (uid,))
    if row:
        sets, vals = [], []
        for k, v in (("name", name), ("guid", guid)):
            if v:
                sets.append(f"{k}=?")
                vals.append(v)
        for k, v in kw.items():
            sets.append(f"{k}=?")
            vals.append(v)
        if sets:
            vals.append(uid)
            q(f"UPDATE users SET {', '.join(sets)} WHERE uid=?", vals)
    else:
        cols = {"uid": uid, "guid": guid, "name": name, "reg_time": now(), "login_time": now()}
        cols.update(kw)
        keys = ",".join(cols)
        ph = ",".join("?" * len(cols))
        q(f"INSERT INTO users ({keys}) VALUES ({ph})", list(cols.values()))


def get_user(uid):
    return q1("SELECT * FROM users WHERE uid=?", (uid,))


def get_or_create_user_by_guid(guid):
    row = q1("SELECT * FROM users WHERE guid=?", (guid,))
    if row:
        return row
    uid = next_uid()
    upsert_user(uid, guid=guid)
    return get_user(uid)


def next_uid():
    row = q1("SELECT v FROM kv WHERE k='next_uid'")
    n = int(row["v"]) if row else 10001
    q("INSERT OR REPLACE INTO kv(k,v) VALUES('next_uid',?)", (str(n + 1),))
    return n


def save_archive(uid, role=None, memory=None, shop=None):
    row = q1("SELECT uid FROM archives WHERE uid=?", (uid,))
    if not row:
        q("INSERT INTO archives(uid) VALUES(?)", (uid,))
    if role is not None:
        q("UPDATE archives SET role=?, updated=? WHERE uid=?", (role, now(), uid))
    if memory is not None:
        q("UPDATE archives SET memory=?, updated=? WHERE uid=?", (memory, now(), uid))
    if shop is not None:
        q("UPDATE archives SET shop=?, updated=? WHERE uid=?", (shop, now(), uid))


def get_archive(uid):
    return q1("SELECT * FROM archives WHERE uid=?", (uid,))


# ---- kv config helpers ----

def get_config(key, default=None):
    row = q1("SELECT v FROM kv WHERE k=?", (key,))
    if row is not None:
        return row["v"]
    return default


def set_config(key, value):
    q("INSERT OR REPLACE INTO kv(k,v) VALUES (?,?)", (key, str(value)))


# ---- notices ----

def get_notices():
    return q("SELECT * FROM notices ORDER BY id")


def add_notice(picname='', type_='0', desc='', gift_id=0, posbtnx=0, posbtny=0, poslabx=0, poslaby=0):
    q("INSERT INTO notices(picname,type,desc,gift_id,posbtnx,posbtny,poslabx,poslaby) VALUES (?,?,?,?,?,?,?,?)",
      (picname, type_, desc, gift_id, posbtnx, posbtny, poslabx, poslaby))


def update_notice(id_, **kw):
    sets, vals = [], []
    for k, v in kw.items():
        sets.append(f"{k}=?")
        vals.append(v)
    vals.append(id_)
    q(f"UPDATE notices SET {', '.join(sets)} WHERE id=?", vals)


def delete_notice(id_):
    q("DELETE FROM notices WHERE id=?", (id_,))


# ---- mails ----

def send_mail(uid, reward, desc):
    q("INSERT INTO mails(uid, reward, desc, created, read) VALUES (?,?,?, ?,0)",
      (uid, reward, desc, now()))


def get_mails(uid):
    return q("SELECT * FROM mails WHERE uid=? ORDER BY id DESC", (uid,))


def mark_mail_read(id_):
    q("UPDATE mails SET read=1 WHERE id=?", (id_,))


def delete_mail(id_):
    q("DELETE FROM mails WHERE id=?", (id_,))


# ---- sign rewards (kv-backed) ----

DEFAULT_SIGN_REWARDS = json.dumps([
    {"awardtype1": "coin", "num1": 300, "awardtype2": "", "num2": 0, "awardtype3": "", "num3": 0},
    {"awardtype1": "coin", "num1": 500, "awardtype2": "", "num2": 0, "awardtype3": "", "num3": 0},
    {"awardtype1": "coin", "num1": 800, "awardtype2": "key", "num2": 1, "awardtype3": "", "num3": 0},
    {"awardtype1": "coin", "num1": 1000, "awardtype2": "", "num2": 0, "awardtype3": "", "num3": 0},
    {"awardtype1": "speedseed", "num1": 2, "awardtype2": "coin", "num2": 500, "awardtype3": "", "num3": 0},
    {"awardtype1": "coin", "num1": 1500, "awardtype2": "key", "num2": 2, "awardtype3": "", "num3": 0},
    {"awardtype1": "coin", "num1": 3000, "awardtype2": "key", "num2": 3, "awardtype3": "", "num3": 0},
], ensure_ascii=False)
