"""Loopback-only fixture demo, never a production HTTP service."""
from __future__ import annotations

import argparse
import json
import secrets
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .contracts import ContractError, _pairs, _constant
from .presentation import snapshot
from .runtime import Conflict, Denied, Host, Principal, Provider

BUILD = Path(__file__).resolve().parents[2] / "ui/dist"


class Controller:
    def __init__(self, directory):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        fresh = not (directory / "host.sqlite3").exists()
        self.principal = Principal("alice-fixture", "sandbox")
        self.host = Host(directory / "host.sqlite3", Provider(directory / "provider.sqlite3"))
        self.token = secrets.token_urlsafe(32)
        if fresh:
            for action in ("publish", "correct", "withdraw"):
                self.host.set_permission(self.principal, "project-board", True, action=action)

    def state(self):
        return {**snapshot(self.host, self.principal), "csrfToken": self.token}

    def command(self, path, data):
        required = {
            "/api/proposals": {"content"},
            "/api/recovery": {"originalId", "action", "content"},
            "/api/decision": {"proposalId", "proposalVersion", "decision"},
            "/api/execute": {"proposalId", "proposalVersion", "loseResponse"},
            "/api/reconcile": {"operationId"},
        }
        if path not in required or type(data) is not dict or set(data) != required[path]:
            raise ContractError("unexpected command fields")
        for name, value in data.items():
            if name == "loseResponse":
                if type(value) is not bool:
                    raise ContractError("invalid fault flag")
            elif name == "content":
                if path == "/api/recovery" and data.get("action") == "withdraw" and value is None:
                    continue
                if not isinstance(value, str) or not value.strip() or len(value) > 4096:
                    raise ContractError("invalid content")
            elif not isinstance(value, str) or not value or len(value) > 128:
                raise ContractError("invalid reference")
        p = self.principal
        if path == "/api/proposals":
            self.host.propose(p, "project-board", data["content"])
        elif path == "/api/recovery":
            self.host.propose_recovery(p, data["originalId"], data["action"], data["content"])
        elif path == "/api/reconcile":
            self.host.reconcile(p, data["operationId"])
        else:
            ref = {"id": data["proposalId"], "version": data["proposalVersion"]}
            submission = f"web-{ref['id']}-{ref['version']}"
            if path == "/api/decision":
                self.host.decide(p, ref, data["decision"], submission)
            else:
                op = self.host.reserve(p, ref, submission)
                self.host.dispatch(p, op, fault="lost-response" if data["loseResponse"] else None)
        return self.state()


def make_server(controller, port=8765, build=BUILD):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def send(self, status, body, content_type="application/json"):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                             "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(body)

        def json(self, status, body):
            self.send(status, json.dumps(body).encode("utf-8"))

        def boundary(self, mutation=False):
            authority = f"127.0.0.1:{self.server.server_port}"
            if self.headers.get_all("Host") != [authority]:
                raise Denied("unexpected host")
            site = self.headers.get("Sec-Fetch-Site")
            if site and site not in ("same-origin", "none"):
                raise Denied("cross-site requests are not allowed")
            if mutation and (self.headers.get_all("Origin") != [f"http://{authority}"]
                             or self.headers.get_all("X-TUN-CSRF") != [controller.token]):
                raise Denied("origin or request token mismatch")

        def do_GET(self):
            try:
                self.boundary()
                if self.path == "/api/state":
                    self.json(200, controller.state())
                    return
                path = unquote(urlsplit(self.path).path)
                if path != "/" and not path.startswith("/assets/"):
                    self.json(404, {"error": "route not found"})
                    return
                asset = (build / ("index.html" if path == "/" else path.lstrip("/"))).resolve()
                if not asset.is_relative_to(build.resolve()) or not asset.is_file():
                    self.json(404, {"error": "build the UI before starting the demo"})
                    return
                content_type = {".js": "text/javascript", ".css": "text/css", ".html": "text/html"}.get(asset.suffix)
                if content_type is None:
                    self.json(404, {"error": "asset not found"})
                    return
                self.send(200, asset.read_bytes(), content_type + "; charset=utf-8")
            except Denied:
                self.json(403, {"error": "local request boundary denied"})
            except Exception:
                self.json(503, {"error": "state unavailable; inspect local fixture records"})

        def do_POST(self):
            try:
                self.boundary(mutation=True)
                if self.headers.get_content_type() != "application/json" or self.headers.get("Transfer-Encoding"):
                    raise ContractError("JSON body required")
                lengths = self.headers.get_all("Content-Length")
                if not lengths or len(lengths) != 1 or not lengths[0].isdigit() or not 0 < int(lengths[0]) <= 32768:
                    raise ContractError("bounded content length required")
                raw = self.rfile.read(int(lengths[0])).decode("utf-8")
                data = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)
                self.json(200, controller.command(self.path, data))
            except Denied:
                self.json(403, {"error": "current authority or record access denied"})
            except (ContractError, Conflict, ValueError, RecursionError):
                self.json(409, {"error": "command rejected; refresh history and review the current proposal"})
            except Exception:
                self.json(503, {"error": "outcome may be unknown; refresh history before further action"})

    return HTTPServer(("127.0.0.1", port), Handler)


def serve(directory, port):
    controller = Controller(directory)
    with make_server(controller, port) as server:
        print(f"Local fixture demo: http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, help="Retain or reopen v0.2 fixture stores; never use real data")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.directory:
        serve(args.directory, args.port)
    else:
        with tempfile.TemporaryDirectory(prefix="tse-review-") as directory:
            serve(Path(directory), args.port)


if __name__ == "__main__":
    main()
