"""DES-ECB JSON API layer (api.joyapi.com protocol).

Request  : POST, body = "data=" + base64(DES-ECB-PKCS5(json))
Response : base64(DES-ECB-PKCS5(json))
Key      : b"abc12345"
Envelope : {"status": int, "msg": str, "data": ...}
"""
import base64
import json
import time

from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

KEY = b"abc12345"


def encrypt(obj) -> str:
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    c = DES.new(KEY, DES.MODE_ECB)
    return base64.b64encode(c.encrypt(pad(raw, 8))).decode()


def decrypt_body(body: bytes):
    """Returns dict of params or raises."""
    text = body.decode("utf-8", "replace").strip()
    if text.startswith("data="):
        text = text[5:]
    raw = base64.b64decode(text)
    c = DES.new(KEY, DES.MODE_ECB)
    plain = unpad(c.decrypt(raw), 8)
    return json.loads(plain.decode("utf-8", "replace"))


def ok(data=None, **extra):
    resp = {"status": 1, "msg": "", "data": data if data is not None else {}}
    resp.update(extra)
    return encrypt(resp)


def fail(msg="", status=0, data=None):
    return encrypt({"status": status, "msg": msg, "data": data if data is not None else {}})


def ts():
    return int(time.time())
