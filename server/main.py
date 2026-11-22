"""BearFarm private server — main entry.

Serves:
  :8080  farmzone.joymeng.com  -> /BearFarm/Bear (plain HTTP game logic)
  :80    api.joyapi.com        -> DES(JSON) endpoints
         netuser.joymeng.com   -> account (plain)
         hijoyres.joymeng.com  -> static resources
  :60000 farmesb1.joymeng.com  -> ESB TCP (chat/family, minimal)
"""
import os
import socketserver
import sys
import threading
import traceback
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import desapi  # noqa: E402
import farmzone  # noqa: E402
import httpapi  # noqa: E402
import store  # noqa: E402

VERBOSE = True
LOGFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.log")


def log(*a):
    if VERBOSE:
        import time as _t
        line = "[%s]" % _t.strftime("%m-%d %H:%M:%S"), *a
        msg = " ".join(str(x) for x in line)
        print(msg, flush=True)
        try:
            with open(LOGFILE, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except Exception:
            pass


class BearHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "nginx"

    def log_message(self, fmt, *args):
        pass

    # ---- helpers ----
    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length > 0 else b""

    def _send(self, status, body, headers=None, ctype="text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or []):
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _parse_query(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        return parsed.path, {k: v[0] for k, v in qs.items()}, qs

    def _handle_farmzone(self):
        path, params, _ = self._parse_query()
        body = self._read_body()
        if self.command == "POST":
            ctype = self.headers.get("Content-Type", "")
            if ctype.startswith("multipart/form-data"):
                self._parse_multipart(ctype, body, params)
            elif "json" in ctype:
                import json as _json
                try:
                    params.update(_json.loads(body.decode("utf-8", "replace")))
                except ValueError:
                    pass
            else:
                form = urllib.parse.parse_qs(body.decode("utf-8", "replace"), keep_blank_values=True)
                for k, v in form.items():
                    params[k] = v[0]
        log("FZ", self.command, path, {k: v for k, v in params.items()
                                        if not str(v).startswith("--") and len(str(v)) < 200})
        try:
            status, resp, extra = farmzone.handle(None, params, self.command, body)
            headers = [("Connection", "close")]
            headers += extra
            self._send(status, resp, headers)
        except Exception:
            traceback.print_exc()
            self._send(200, b"1", [("Connection", "close")])

    def _parse_multipart(self, ctype, body, params):
        import re
        m = re.search(r'boundary="?([^";]+)"?', ctype)
        if not m:
            return
        bnd = m.group(1).encode()
        for part in body.split(b"--" + bnd):
            part = part.strip(b"\r\n")
            if not part or part == b"--":
                continue
            if b"\r\n\r\n" not in part:
                continue
            head, _, val = part.partition(b"\r\n\r\n")
            hm = re.search(rb'name="([^"]+)"', head)
            if not hm:
                continue
            name = hm.group(1).decode("utf-8", "replace")
            params[name] = val.decode("utf-8", "replace")
            # also expose the clean name without the ",type" suffix
            if "," in name:
                params[name.split(",")[0]] = val.decode("utf-8", "replace")

    def _handle_des_api(self, path):
        body = self._read_body()
        try:
            params = desapi.decrypt_body(body)
        except Exception as e:
            log("DES decode failed:", e)
            self._send(200, desapi.fail("bad request").encode(), [("Connection", "close")])
            return
        route = path.strip("/")
        log("API", route, {k: (str(v)[:80]) for k, v in params.items()})
        try:
            enc = httpapi.route(route, params)
            self._send(200, enc.encode(), [("Connection", "close")])
        except Exception:
            traceback.print_exc()
            self._send(200, desapi.fail("server error").encode(), [("Connection", "close")])

    def _handle_static(self, path):
        # hijoyres.joymeng.com/260/<file>
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "res")
        rel = path.strip("/").replace("..", "")
        full = os.path.join(base, rel)
        if os.path.isfile(full):
            data = open(full, "rb").read()
            self._send(200, data, [("Connection", "close")])
        else:
            self._send(404, b"", [("Connection", "close")])

    def _handle_packs(self):
        # hijoyusers.joymeng.com:8100/bigbear/getPacksList (plain HTTP GET)
        import json as _json
        params = self._parse_query()[1]
        resp = {
            "status": 1, "param": {
                "IsMonthcardbuyed": 0, "MonthcardCollect": False,
                "IsMonthcardbuyedCu": 0, "MonthcardCollectCu": False,
                "comeBackFromFriend": False, "ShowBtUI": 1, "showRoleBuy": "true",
                "isShowUnicomGift": "false", "RandomControl": 0, "iscode": 0,
                "isOpenADS": 0, "ShowGiftsbox": "", "GeneralControl": "0",
                "Youlechang": "0", "CatchCowRatio": 100, "SpecialControl": False,
                "IsShowCMMonthlyGift": 0, "monthGiftPriceRange": "0,0",
                "commentCount": "0",
            },
        }
        self._send(200, _json.dumps(resp).encode(), [("Connection", "close")])

    def _route(self):
        path, params, _ = self._parse_query()
        if path.startswith("/BearFarm/Bear"):
            self._handle_farmzone()
        elif path.startswith("/bigbear/getPacksList") and self.command == "GET" and "data=" not in path:
            self._handle_packs()
        elif path.startswith("/farm/") or path.startswith("/user/") or path.startswith("/game/") \
                or path.startswith("/ranks/") or path.startswith("/bigbear/") or path.startswith("/shop/") \
                or path.startswith("/mail/") or path.startswith("/msg/") or path.startswith("/car/") \
                or path.startswith("/work/") or path.startswith("/rank/") or path.startswith("/apporder/") \
                or path.startswith("/log/") or path.startswith("/commonpvp/") or path.startswith("/arena/") \
                or path.startswith("/dreammarket/") or path.startswith("/ultramanhelp/") or path.startswith("/sdk/") \
                or path.startswith("/ltad/") or path.startswith("/biddingad/") or path.startswith("/gamedataconfig/"):
            self._handle_des_api(path)
        elif path == "/user/login" or path == "/user/quickReg":
            # netuser plain HTTP account: GET /user/login?uname=&password=
            uname = params.get("uname", "")
            import json as _json
            if uname:
                user = store.get_or_create_user_by_guid("lt_" + uname)
                resp = _json.dumps({"status": 1, "uid": user["uid"], "token": "token",
                                    "username": uname}).encode()
            else:
                resp = _json.dumps({"status": -1, "msg": "账户密码不能为空!"}).encode("utf-8")
            self._send(200, resp, [("Connection", "close")])
        else:
            self._handle_static(path)

    def do_GET(self):
        try:
            self._route()
        except Exception:
            traceback.print_exc()

    def do_POST(self):
        try:
            self._route()
        except Exception:
            traceback.print_exc()


class ESBHandler(socketserver.BaseRequestHandler):
    """Minimal ESB: sends redirect loopback, accepts login, ignores traffic."""
    def handle(self):
        import struct
        try:
            # ServerRedirResponse (protocol 0xFF): port + string8 host -> redirect to self
            host = self.request.getsockname()[0]
            port = ESB_PORT
            body = struct.pack(">i", port) + bytes([len(host)]) + host.encode()
            self.request.sendall(struct.pack(">I", len(body)) + body)
        except Exception:
            pass


ESB_PORT = 60000


class ESBServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    store.init()
    farm_port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    api_port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    global ESB_PORT
    ESB_PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 60000
    packs_port = int(sys.argv[4]) if len(sys.argv) > 4 else 8100

    farm_srv = ThreadingHTTPServer(("0.0.0.0", farm_port), BearHandler)
    api_srv = ThreadingHTTPServer(("0.0.0.0", api_port), BearHandler)
    packs_srv = ThreadingHTTPServer(("0.0.0.0", packs_port), BearHandler)
    esb_srv = ESBServer(("0.0.0.0", ESB_PORT), ESBHandler)

    threading.Thread(target=esb_srv.serve_forever, daemon=True).start()
    threading.Thread(target=api_srv.serve_forever, daemon=True).start()
    threading.Thread(target=packs_srv.serve_forever, daemon=True).start()
    print(f"[bearfarm-server] farmzone :{farm_port}  api :{api_port}  esb :{ESB_PORT}  packs :{packs_port}", flush=True)
    try:
        farm_srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
