"""farmzone.joymeng.com:8080/BearFarm/Bear — the plain-HTTP game logic server."""
import json
import os
import time
import zlib

import store

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

FRIEND_INFO_KEYS = ("face", "faceType", "id", "isNpc", "level", "name", "sex", "shopStatus", "status", "vip")


def friend_info(user, is_npc=0):
    if user is None:
        return {"face": 0, "faceType": 0, "id": "0", "isNpc": 1, "level": 99,
                "name": "强哥", "sex": 0, "shopStatus": 1, "status": 0, "vip": 3}
    return {
        "face": user["face"], "faceType": user["face_type"], "id": str(user["uid"]),
        "isNpc": is_npc, "level": user["level"], "name": user["name"] or ("玩家" + str(user["uid"])),
        "sex": user["sex"], "shopStatus": 0, "status": 0, "vip": user["vip"],
    }


def load_data(name, default):
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        return open(path, "rb").read()
    return default.encode("utf-8")


def sign_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def get_sign_rewards():
    raw = store.get_config("sign_rewards", store.DEFAULT_SIGN_REWARDS)
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return json.loads(store.DEFAULT_SIGN_REWARDS)


def build_notice_xml():
    rows = store.get_notices()
    parts = ['<?xml version="1.0" encoding="utf-8"?>', "<Notices>"]
    for r in rows:
        parts.append(
            f'<Notice id="{r["id"]}" picname="{r["picname"]}" type="{r["type"]}" '
            f'desc="{r["desc"]}" giftId="{r["gift_id"]}" '
            f'posbtnx="{r["posbtnx"]}" posbtny="{r["posbtny"]}" '
            f'poslabx="{r["poslabx"]}" poslaby="{r["poslaby"]}"/>'
        )
    parts.append("</Notices>")
    return "\n".join(parts).encode("utf-8")


def get_notice_version():
    raw = store.get_config("notice_version", "0")
    return int(raw) if raw else 0


TREE_GROW_SECONDS_KEY = "tree_grow_seconds"
TREE_OUTPUT_BASE_KEY = "tree_output_base"
TREE_OUTPUT_PER_LEVEL_KEY = "tree_output_per_level"


def tree_config():
    grow = int(store.get_config(TREE_GROW_SECONDS_KEY, str(TREE_GROW_SECONDS)) or 7200)
    base = int(store.get_config(TREE_OUTPUT_BASE_KEY, "100") or 100)
    per = int(store.get_config(TREE_OUTPUT_PER_LEVEL_KEY, "20") or 20)
    return grow, base, per


def tree_row(uid):
    return store.q1("SELECT * FROM trees WHERE uid=?", (uid,))


def tree_output(level, guang_level):
    _, base, per = tree_config()
    return base + level * per + guang_level * (per // 2)


def tree_payload(row):
    status = row["status"]
    remain = 0
    if status == 1:
        remain = row["planted_at"] + row["grow_seconds"] - store.now()
        if remain <= 0:
            store.q("UPDATE trees SET status=2 WHERE uid=?", (row["uid"],))
            status = 2
            remain = 0
    return {
        "joyId": row["uid"],
        "level": row["level"],
        "time": remain * 1000,
        "output": row["output"],
        "stealCount": row["steal_count"],
        "defCount": row["def_count"],
        "plus": row["plus_count"],
        "left": row["left_count"],
        "status": status,
        "guangLevel": row["guang_level"],
    }


def tree_handler(logic, uid, params):
    if logic == "TreeStatus":
        row = tree_row(uid)
        if row is None:
            # auto-create an unplanted tree for this player (the original server
            # created one at registration); keeps the client out of local mode
            u = store.get_user(uid)
            lvl = u["level"] if u else 1
            store.q("INSERT OR IGNORE INTO trees(uid, level, guang_level, status, planted_at, "
                    "grow_seconds, output, left_count, steal_count, def_count, plus_count) "
                    "VALUES (?,?,?,0,0,0,0,0,0,0,0)", (uid, lvl, 1))
            row = tree_row(uid)
        return 200, json.dumps({"status": 1, "tree": tree_payload(row)}).encode(), []

    if logic == "TreePlant":
        level = int(params.get("bearLevel", 1) or 1)
        guang = int(params.get("guangLevel", 1) or 1)
        output = tree_output(level, guang)
        grow, _, _ = tree_config()
        store.q("INSERT OR REPLACE INTO trees(uid, level, guang_level, status, planted_at, "
                "grow_seconds, output, left_count, steal_count, def_count, plus_count) "
                "VALUES (?,?,?,1,?,?,?,?,0,0,0)",
                (uid, level, guang, store.now(), grow, output, output))
        row = tree_row(uid)
        rate = int(params.get("motion", 80) or 80) // 10
        return 200, json.dumps({"status": 1, "tree": tree_payload(row), "rate": rate}).encode(), []

    if logic == "TreeHarvest":
        row = tree_row(uid)
        if row is None or row["status"] != 2:
            return 200, json.dumps({"status": 0, "message": "not mature"}).encode(), []
        gained = row["left_count"] + row["plus_count"]
        store.q("UPDATE trees SET status=0, output=0, left_count=0, plus_count=0, "
                "steal_count=0, def_count=0 WHERE uid=?", (uid,))
        row = tree_row(uid)
        return 200, json.dumps({"status": 1, "tree": tree_payload(row)}).encode(), []

    if logic == "TreeSteal":
        fid = params.get("fid", "0")
        f_uid = int(fid) if str(fid).isdigit() else 0
        row = tree_row(f_uid) if f_uid else None
        if row is None:
            return 200, json.dumps({"status": 0, "message": "no tree"}).encode(), []
        if row["status"] != 2:
            return 200, json.dumps({"status": 0, "message": "not mature"}).encode(), []
        if row["left_count"] <= 0:
            return 200, json.dumps({"status": 0, "message": "nothing left"}).encode(), []
        money = max(10, row["output"] // 10)
        new_left = max(0, row["left_count"] - money)
        store.q("UPDATE trees SET left_count=?, steal_count=steal_count+1 WHERE uid=?",
                (new_left, f_uid))
        row = tree_row(f_uid)
        rate = int(params.get("motionBear", 80) or 80) // 10
        return 200, json.dumps({"status": 1, "tree": tree_payload(row),
                                "money": money, "rate": rate}).encode(), []

    return 200, json.dumps({"status": 0, "message": "bad op"}).encode(), []


def handle(uid, params, method="GET", body=b""):
    """Main dispatcher. params = dict of query/form fields."""
    logic = params.get("logic") or params.get("Logic") or ""
    if isinstance(uid, list):
        uid = uid[0] if uid else None
    # the numeric id query param is the caller's identity on this endpoint
    pid = params.get("id")
    if pid is not None and str(pid).lstrip("-").isdigit():
        uid = int(pid)
    try:
        uid = int(str(uid))
    except (TypeError, ValueError):
        uid = 0
    user = store.get_user(uid)

    if logic == "Heart":
        if uid:
            store.q("UPDATE users SET last_seen=? WHERE uid=?", (store.now(), uid))
        return 200, b"ok", []

    if logic == "LoginAfter":
        return 200, b"1,1", []

    if logic == "Log":
        return 200, b"1", []

    if logic == "Notice":
        ntype = params.get("type", "0")
        if ntype == "0":
            return 200, f"{get_notice_version()},0".encode(), []
        return 200, build_notice_xml(), []

    if logic == "Friend":
        ftype = params.get("type", "0")
        fid = params.get("fid", params.get("fId", "0"))
        if ftype == "2":
            friends = store.q(
                "SELECT u.* FROM friends f JOIN users u ON u.uid=f.fid WHERE f.uid=?", (uid,))
            resp = {
                "curNum": len(friends), "maxNum": 50,
                "canSteal": [], "userList": [friend_info(f) for f in friends],
                "online": [],
            }
            return 200, json.dumps(resp).encode(), []
        if ftype == "3":
            frow = store.get_user(int(fid) if str(fid).isdigit() else 0)
            return 200, json.dumps(friend_info(frow)).encode(), []
        if ftype == "1":
            if str(fid).isdigit() and int(fid) > 0:
                store.q("INSERT OR IGNORE INTO friends(uid,fid,created) VALUES(?,?,?)",
                        (uid, int(fid), store.now()))
                store.upsert_user(int(fid))
            return 200, b"{}", []
        if ftype == "4":
            if str(fid).isdigit():
                store.q("DELETE FROM friends WHERE uid=? AND fid=?", (uid, int(fid)))
            return 200, b"{}", []
        return 200, b"{}", []

    if logic == "Access":
        # Friend visit: raw zlib blob + memoryLen header.
        arch = store.get_archive(uid)
        if arch and arch["memory"]:
            blob = zlib.compress(arch["memory"].encode("utf-8"))
            return 200, blob, [("memoryLen", str(len(blob)))]
        return 200, b"", [("memoryLen", "0")]

    if logic == "SearchAround":
        keys = params.get("keys", "")
        out = []
        for k in keys.split(","):
            if k.strip().isdigit():
                u = store.get_user(int(k))
                if u:
                    out.append(friend_info(u))
        return 200, json.dumps(out).encode(), []

    if logic == "Sign":
        return 200, json.dumps({"time": sign_time(), "reward": get_sign_rewards()}).encode(), []

    if logic == "Steal":
        # "ok:amount" or "err:msg"
        return 200, b"ok:5", []

    if logic == "Vip":
        return 200, b"0", []

    if logic == "Shop":
        return 200, b"0", []

    if logic == "Rename":
        name = params.get("name")
        face = params.get("face")
        if name:
            store.upsert_user(uid, name=name)
        if face and str(face).isdigit():
            store.upsert_user(uid, face=int(face))
        return 200, b"1", []

    if logic == "RewardGet":
        return 200, json.dumps({"desc": "奖励已发放", "reward": "coin|100"}).encode(), []

    if logic == "InvitationFriend":
        ids = params.get("ids", "")
        out = []
        for k in ids.split(","):
            if k.strip().isdigit():
                u = store.get_user(int(k))
                if u:
                    out.append(friend_info(u))
        return 200, json.dumps(out).encode(), []

    if logic == "LoadHotsellsFile":
        xml = load_data("hotsell.xml", '<?xml version="1.0" encoding="utf-8"?><Hotsells></Hotsells>')
        return 200, xml, []

    if logic in ("TreeStatus", "TreePlant", "TreeHarvest", "TreeSteal"):
        return tree_handler(logic, uid, params)

    if logic == "Change":
        set_id = params.get("setId", "")
        if str(set_id).isdigit() and int(set_id) > 0:
            uid = int(set_id)
        name = params.get("setName")
        face = params.get("setFace")
        sex = params.get("setSex")
        face_type = params.get("setFaceType")
        kw = {}
        if name:
            kw["name"] = name
        if face and str(face).isdigit():
            kw["face"] = int(face)
        if sex and str(sex).isdigit():
            kw["sex"] = int(sex)
        if face_type and str(face_type).isdigit():
            kw["face_type"] = int(face_type)
        store.upsert_user(uid, **kw)
        return 200, str(uid).encode(), []

    if logic == "Regist":
        set_id = params.get("setUid", "")
        if str(set_id).isdigit() and int(set_id) > 0:
            uid = int(set_id)
        store.upsert_user(uid, name=params.get("setName", ""),
                          guid=params.get("setUuid", ""), channel_id=params.get("setChannelId", ""))
        return 200, str(uid).encode(), []

    return 200, b"1", []
