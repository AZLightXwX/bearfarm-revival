"""DES JSON API routes (served on port 80 as api.joyapi.com / netuser / hijoyres)."""
import json

import desapi
import store


def character_info(user):
    if user is None:
        return None
    return {
        "ageGroup": user["age_group"], "channelId": user["channel_id"] or "",
        "coin": 0, "constellation": "", "face": user["face"],
        "faceName": "0", "faceType": user["face_type"], "id": str(user["uid"]),
        "key": 0, "level": user["level"], "name": user["name"] or ("玩家" + str(user["uid"])),
        "npc": False, "registerTime": str(user["reg_time"]), "sex": user["sex"], "vip": user["vip"],
    }


def friend_list_payload(uid):
    friends = store.q(
        "SELECT u.* FROM friends f JOIN users u ON u.uid=f.fid WHERE f.uid=?", (uid,))
    return {
        "curNum": len(friends), "maxNum": 50,
        "userList": [character_info(f) for f in friends],
    }


def world_shops_payload(uid, limit=30):
    """List of other players' shop cells (from their uploaded shop archives)."""
    rows = store.q(
        "SELECT a.uid, a.shop FROM archives a WHERE a.shop IS NOT NULL AND a.shop != '' AND a.uid != ? LIMIT ?",
        (uid, limit))
    out = []
    for r in rows:
        try:
            d = json.loads(r["shop"])
        except (ValueError, TypeError):
            continue
        shop = d.get("shop", d) if isinstance(d, dict) else None
        if not isinstance(shop, dict):
            continue
        shop["uId"] = str(r["uid"])
        out.append(shop)
    return out


def default_shop(uid):
    cells = []
    for i in range(8):
        cells.append({
            "id": None, "itemId": None, "amount": 0, "price": 0, "costItem": None,
            "status": 0 if i < 4 else 2, "seller": None, "buyer": None, "voyage": 0,
            "createdAt": 0, "autoBuy": False, "autobuyTime": 0, "index": i, "buyed": False,
        })
    u = store.get_user(uid)
    return {
        "cells": cells, "face": u["face"] if u else 1, "faceData": "0", "faceType": 0,
        "level": u["level"] if u else 1, "name": (u["name"] if u else "") or str(uid),
        "uId": str(uid), "shopStatus": 1,
    }


def get_shop_dict(uid):
    arch = store.get_archive(uid)
    if arch and arch["shop"]:
        try:
            d = json.loads(arch["shop"])
            if "shop" in d:
                return d
        except (ValueError, TypeError):
            pass
    return {"shop": default_shop(uid)}


def save_shop_dict(uid, d):
    store.save_archive(uid, shop=json.dumps(d, ensure_ascii=False))


def norm_cells(shop):
    cells = shop.setdefault("cells", [])
    while len(cells) < 8:
        i = len(cells)
        cells.append({
            "id": None, "itemId": None, "amount": 0, "price": 0, "costItem": None,
            "status": 0 if i < 4 else 2, "seller": None, "buyer": None, "voyage": 0,
            "createdAt": 0, "autoBuy": False, "autobuyTime": 0, "index": i, "buyed": False,
        })
    return cells


def handle_shop(uid, params):
    """Market/trading operations (all POST farm/shop with a `type`)."""
    ftype = str(params.get("type", "0"))
    fid = str(params.get("fId", params.get("fid", "")))
    index = params.get("index")
    jstr = params.get("json", "")

    if ftype == "1":  # addGoods: sell an item in one of my slots
        try:
            offer = json.loads(jstr) if jstr else {}
        except (ValueError, TypeError):
            offer = {}
        d = get_shop_dict(uid)
        cells = norm_cells(d["shop"])
        idx = offer.get("index")
        if idx is None and index is not None and str(index).isdigit():
            idx = int(index)
        if not isinstance(idx, int) or not (0 <= idx < 8):
            idx = 0
        cells[idx] = offer
        save_shop_dict(uid, d)
        return desapi.ok({"index": idx})

    if ftype == "5":  # buyGoods from a seller's slot
        seller = str(params.get("seller", fid or "0"))
        s_uid = int(seller) if seller.isdigit() else uid
        idx = int(index) if str(index).isdigit() else 0
        d = get_shop_dict(s_uid)
        cells = norm_cells(d["shop"])
        if 0 <= idx < len(cells):
            cells[idx]["buyed"] = True
            cells[idx]["status"] = 1
            cells[idx]["buyer"] = str(uid)
            save_shop_dict(s_uid, d)
        return desapi.ok({"index": idx})

    if ftype == "6":  # reset/clear a slot
        d = get_shop_dict(uid)
        cells = norm_cells(d["shop"])
        idx = int(index) if str(index).isdigit() else 0
        if 0 <= idx < len(cells):
            cells[idx] = {
                "id": None, "itemId": None, "amount": 0, "price": 0, "costItem": None,
                "status": 0, "seller": None, "buyer": None, "voyage": 0,
                "createdAt": 0, "autoBuy": False, "autobuyTime": 0, "index": idx, "buyed": False,
            }
            save_shop_dict(uid, d)
        return desapi.ok({"index": idx})

    if ftype == "4":  # rent a locked slot
        d = get_shop_dict(uid)
        cells = norm_cells(d["shop"])
        idx = int(index) if str(index).isdigit() else 0
        if 0 <= idx < len(cells):
            cells[idx]["status"] = 0
            save_shop_dict(uid, d)
        return desapi.ok({"index": idx})

    if ftype == "0":  # my shop: data = ShopCells object (with cells)
        d = get_shop_dict(uid)
        return desapi.ok(d["shop"])

    if ftype == "2":  # world market: other players' shops
        return desapi.ok(world_shops_payload(uid))

    if ftype == "3":  # friends market: my friends' shops
        fids = store.q("SELECT fid FROM friends WHERE uid=?", (uid,))
        shops = []
        for f in fids:
            d = get_shop_dict(f["fid"])
            d["shop"]["uId"] = str(f["fid"])
            shops.append(d["shop"])
        return desapi.ok(shops)

    if ftype == "8":  # friend shop: data = array of SeafarerOffer (cells)
        target = int(fid) if fid.isdigit() else uid
        d = get_shop_dict(target)
        return desapi.ok(norm_cells(d["shop"]))

    if ftype == "9":  # friend selling check
        target = int(fid) if fid.isdigit() else uid
        d = get_shop_dict(target)
        has = any(c.get("itemId") for c in norm_cells(d["shop"]))
        return desapi.ok({"selling": 1 if has else 0})

    return desapi.ok([])


def route(path, params):
    """path like 'farm/getArchive'; params already decrypted (dict).
    Returns DES-encrypted response body."""
    ctrl, _, action = path.partition("/")
    ctrl = ctrl.lower()
    action = action.lower()

    def guid_of():
        g = params.get("guid") or params.get("uid") or "0"
        return str(g)

    def uid_of():
        g = guid_of()
        if g.isdigit():
            return int(g)
        row = store.q1("SELECT uid FROM users WHERE guid=?", (g,))
        return row["uid"] if row else 0

    # ---------------- user / account ----------------
    if ctrl == "user":
        guid = guid_of()
        if action in ("logincombine", "quickreg", "login"):
            user = store.get_or_create_user_by_guid(guid)
            store.q("UPDATE users SET login_time=? WHERE uid=?", (store.now(), user["uid"]))
            return desapi.ok({
                "uid": user["uid"], "nickname": user["name"] or "",
                "regTime": user["reg_time"], "time": store.now(),
                "_real_reg_": 1, "ip": "127.0.0.1",
            })
        if action == "updateuser":
            nick = params.get("nickname")
            if nick:
                store.upsert_user(uid_of(), name=nick)
            return desapi.ok({"uid": guid})
        return desapi.ok({})

    # ---------------- game config ----------------
    if ctrl == "game" and action == "getallparam":
        return desapi.ok({"getLogInit": "", "getAdList": [], "getMailList": [], "getActData": []})

    if ctrl == "bigbear" and action == "getpackslist":
        return desapi.ok({
            "IsMonthcardbuyed": 0, "MonthcardCollect": False,
            "IsMonthcardbuyedCu": 0, "MonthcardCollectCu": False,
            "comeBackFromFriend": False, "ShowBtUI": 1, "showRoleBuy": "true",
            "isShowUnicomGift": "false", "RandomControl": 0, "iscode": 0,
            "isOpenADS": 0, "ShowGiftsbox": "", "GeneralControl": "0",
            "Youlechang": "0", "CatchCowRatio": 100, "SpecialControl": False,
            "IsShowCMMonthlyGift": 0, "monthGiftPriceRange": "0,0",
            "commentCount": "0",
        })

    if ctrl == "ranks":
        return desapi.ok([])

    # ---------------- farm subsystem ----------------
    if ctrl == "farm":
        uid = uid_of()
        if uid == 0:
            uid = store.get_or_create_user_by_guid(guid_of())["uid"]

        if action in ("setarchive", "setarchivenew"):
            data = params.get("data", "")
            try:
                obj = json.loads(data) if isinstance(data, str) else data
            except (ValueError, TypeError):
                obj = {}
            if isinstance(obj, dict) and "shop" in obj:
                store.save_archive(uid, shop=json.dumps(obj["shop"], ensure_ascii=False))
            elif isinstance(obj, dict):
                role = obj.get("role")
                memory = obj.get("memory")
                role_json = json.dumps(role, ensure_ascii=False) if role is not None else None
                store.save_archive(uid, role=role_json,
                                   memory=json.dumps(memory, ensure_ascii=False) if memory is not None else None)
                if isinstance(role, dict):
                    kw = {}
                    if role.get("name"):
                        kw["name"] = role["name"]
                    if isinstance(role.get("level"), int):
                        kw["level"] = role["level"]
                    if isinstance(role.get("face"), int):
                        kw["face"] = role["face"]
                    if isinstance(role.get("sex"), int):
                        kw["sex"] = role["sex"]
                    if isinstance(role.get("vip"), int):
                        kw["vip"] = role["vip"]
                    if isinstance(role.get("ageGroup"), int):
                        kw["age_group"] = role["ageGroup"]
                    if kw:
                        store.upsert_user(uid, **kw)
            return desapi.ok({"uid": uid})

        if action == "getarchive":
            arch = store.get_archive(uid)
            atype = params.get("archive_type", "memory")
            blob = (arch["memory"] if atype == "memory" else (arch["role"] or "")) if arch else ""
            if blob:
                try:
                    return desapi.ok(json.loads(blob))
                except (ValueError, TypeError):
                    return desapi.ok({"data": blob})
            return desapi.fail("data empty!", status=0)

        if action == "gettargetarchive":
            tid = params.get("targetId", params.get("targetid", "0"))
            uid_t = int(tid) if str(tid).isdigit() else 0
            arch = store.get_archive(uid_t)
            blob = arch["memory"] if arch else None
            if not blob:
                # fall back to any existing farm blob (original server served a
                # default farm for blob-less friends instead of erroring)
                tpl = store.q1("SELECT memory FROM archives WHERE memory IS NOT NULL "
                               "AND memory != '' LIMIT 1")
                blob = tpl["memory"] if tpl else None
            if blob:
                try:
                    return desapi.ok({"memory": json.loads(blob)})
                except (ValueError, TypeError):
                    return desapi.ok({"memory": blob})
            return desapi.fail("data empty!", status=0)

        if action == "rmarchive":
            store.q("DELETE FROM archives WHERE uid=?", (uid,))
            return desapi.ok({})

        if action == "friendlist":
            return desapi.ok(friend_list_payload(uid))

        if action == "friendrecommend":
            friends = store.q("SELECT fid FROM friends WHERE uid=?", (uid,))
            fids = [f["fid"] for f in friends] + [uid]
            ph = ",".join("?" * len(fids))
            recs = store.q(f"SELECT * FROM users WHERE uid NOT IN ({ph}) ORDER BY reg_time DESC LIMIT 10", fids)
            return desapi.ok({
                "curNum": len(recs), "maxNum": 50,
                "userList": [character_info(r) for r in recs],
            })

        if action == "addfriend":
            fid = params.get("friend_id", params.get("fid", "0"))
            if str(fid).isdigit() and int(fid) > 0:
                store.q("INSERT OR IGNORE INTO friends(uid,fid,created) VALUES(?,?,?)",
                        (uid, int(fid), store.now()))
                store.upsert_user(int(fid))
            return desapi.ok({})

        if action == "delfriend":
            fid = params.get("friend_id", params.get("fid", "0"))
            if str(fid).isdigit():
                store.q("DELETE FROM friends WHERE uid=? AND fid=?", (uid, int(fid)))
            return desapi.ok({})

        if action == "getfriendinfo":
            fid = params.get("friend_id", params.get("fid", "0"))
            u = store.get_user(int(fid) if str(fid).isdigit() else 0)
            return desapi.ok(character_info(u) or {})

        if action in ("shop", "getgoodslist"):
            return handle_shop(uid, params)

        if action == "setshopproperty":
            data = params.get("data", "")
            try:
                obj = json.loads(data) if isinstance(data, str) else data
                if isinstance(obj, dict) and "shop" in obj:
                    store.save_archive(uid, shop=json.dumps(obj["shop"], ensure_ascii=False))
            except (ValueError, TypeError):
                pass
            return desapi.ok({})

        if action in ("sendmsg", "sendmsgmarket"):
            return desapi.ok({})
        if action == "receivemsg":
            return desapi.ok([])
        if action == "heart":
            return desapi.ok({})
        if action == "planorder":
            return desapi.ok({})
        return desapi.ok({})

    # ---------------- dreammarket subsystem ----------------
    if ctrl == "dreammarket":
        uid = uid_of()
        if action == "friendlist":
            return desapi.ok(friend_list_payload(uid))
        if action == "friendrecommend":
            return desapi.ok({"curNum": 0, "maxNum": 50, "userList": []})
        if action == "friendvisit":
            tid = params.get("fId", params.get("fid", "0"))
            u = store.get_user(int(tid) if str(tid).isdigit() else 0)
            return desapi.ok(character_info(u) or {})
        if action == "getmails":
            mails = store.get_mails(uid)
            out = []
            for m in mails:
                out.append({
                    "MailID": str(m["id"]),
                    "reward": m["reward"],
                    "desc": m["desc"],
                })
            return desapi.ok(out)

        if action == "rmmail":
            mail_id = params.get("mailIds", params.get("mailId", ""))
            for mid in str(mail_id).split(","):
                if mid.strip().isdigit():
                    store.delete_mail(int(mid))
            return desapi.ok({})

        if action == "rankview":
            return desapi.ok({"list": [], "self": None})
        return desapi.ok({})

    # ---------------- generic fallback ----------------
    if ctrl in ("shop", "mail", "msg", "friend", "car", "work", "rank", "market", "apporder", "log"):
        return desapi.ok({})

    return desapi.ok({})
