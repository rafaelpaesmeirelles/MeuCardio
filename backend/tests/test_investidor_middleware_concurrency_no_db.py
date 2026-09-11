"""ASGI concurrency regression without importing the app or touching a database.

Uses the actual middleware classes, Starlette responses/threadpool and a small
thread-affine session pool. Integrated auth/ORM tests remain separate.
"""
import ast
import asyncio
from datetime import datetime, timedelta
from hashlib import sha256
import json
from pathlib import Path
import threading
import time
from types import SimpleNamespace
import unittest
from zoneinfo import ZoneInfo

from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse


ROOT = Path(__file__).resolve().parents[1]


def namespace(filename, names):
    source = ROOT / "app/services" / filename
    tree = ast.parse(source.read_text())
    nodes = []
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names:
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            nodes.append(node)
    env = dict(Request=Request, JSONResponse=JSONResponse, run_in_threadpool=run_in_threadpool,
               sha256=sha256, datetime=datetime, timedelta=timedelta, ZoneInfo=ZoneInfo,
               AUTH_COOKIE_NAME="test-session", ambiente_atual=lambda: "production",
               MENSAGEM_MODO_INVESTIDOR="Somente leitura", MENSAGEM_AGENDA_DEMO="Agenda sintética")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), env)
    return env


class MiddlewareConcurrency(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        common = {"_token_da_requisicao"}
        self.readonly = namespace("investidor_demo.py", common | {
            "InvestidorReadOnlyMiddleware", "_get_com_efeito_colateral", "_agenda_demo",
            "_ESCRITAS_AUTH_PERMITIDAS", "_ESCRITAS_UX_SIMULADAS",
        })
        self.ephemeral = namespace("investidor_ephemeral_ux.py", common | {
            "InvestidorEphemeralUxMiddleware", "_marcador", "_set_cookie_sessao",
            "_COOKIE_ONBOARDING", "_COOKIE_BOAS_VINDAS",
        })
        self.sessions = []
        self.query_delay = 0
        self.investidor = False
        self.lookup_error = None
        self.loop_thread = threading.get_ident()
        self.pool = threading.BoundedSemaphore(2)
        test = self

        class Session:
            def __init__(self):
                test.assertNotEqual(threading.get_ident(), test.loop_thread)
                test.assertTrue(test.pool.acquire(timeout=2), "pool starved")
                self.thread = threading.get_ident()
                self.closed = False
                test.sessions.append(self)

            def close(self):
                test.assertEqual(threading.get_ident(), self.thread)
                test.assertFalse(self.closed)
                self.closed = True
                test.pool.release()

        def lookup(db, token):
            self.assertEqual(db.thread, threading.get_ident())
            time.sleep(self.query_delay)
            if self.lookup_error:
                raise self.lookup_error
            return None if token == "invalid" else SimpleNamespace(investidor=self.investidor)

        for env in (self.readonly, self.ephemeral):
            env.update(SessionLocal=Session, usuario_por_token_app=lookup)

    async def request(self, env, name, path, method="GET", token="fixture", downstream=None):
        messages = []
        called = []

        async def app(scope, receive, send):
            called.append(scope["path"])
            if downstream:
                await downstream()
            await JSONResponse({"downstream": True})(scope, receive, send)

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            # For a single request all opened sessions must be closed before
            # any response is sent. Concurrent tests assert this at completion.
            messages.append(message)

        headers = [(b"cookie", f"test-session={token}".encode())] if token else []
        await env[name](app)({"type": "http", "method": method, "path": path, "headers": headers, "query_string": b""}, receive, send)
        start = next(m for m in messages if m["type"] == "http.response.start")
        body = json.loads(b"".join(m.get("body", b"") for m in messages if m["type"] == "http.response.body"))
        return start, body, called

    async def test_ephemeral_skips_database_for_research_and_unrelated_api_reads(self):
        for path in ["/api/studies", "/api/favorites/status", "/api/billing/status", "/api/library/documents", "/api/casos-clinicos"]:
            _, _, called = await self.request(self.ephemeral, "InvestidorEphemeralUxMiddleware", path)
            self.assertEqual(called, [path])
        self.assertEqual(self.sessions, [])

    async def test_ephemeral_closes_session_before_downstream(self):
        async def check():
            self.assertTrue(all(s.closed for s in self.sessions))
        await self.request(self.ephemeral, "InvestidorEphemeralUxMiddleware", "/api/auth/me", downstream=check)
        self.assertEqual(len(self.sessions), 1)

    async def test_investor_ux_cookie_is_session_scoped_and_no_downstream_write(self):
        self.investidor = True
        for path, flag in [("/api/auth/me/onboarding-concluido", "onboarding_pendente"), ("/api/auth/me/boas-vindas-vista", "boas_vindas_pendente")]:
            start, body, called = await self.request(self.ephemeral, "InvestidorEphemeralUxMiddleware", path, "POST")
            self.assertEqual((start["status"], body, called), (200, {flag: False}, []))
            cookie = dict(start["headers"])[b"set-cookie"].lower()
            for attribute in [b"httponly", b"secure", b"samesite=lax"]:
                self.assertIn(attribute, cookie)
            self.assertNotIn(b"max-age", cookie)
            self.assertTrue(all(s.closed for s in self.sessions))

    async def test_investor_oauth_start_is_still_denied(self):
        self.investidor = True
        start, _, called = await self.request(self.ephemeral, "InvestidorEphemeralUxMiddleware", "/api/agenda/oauth/google/start")
        self.assertEqual((start["status"], called), (403, []))
        self.assertTrue(all(s.closed for s in self.sessions))

    async def test_readonly_preserves_unknown_mutation_and_operational_read_denial(self):
        self.investidor = True
        for path, method in [("/api/new-feature", "POST"), ("/api/new-feature", "DELETE"), ("/api/prescriptions/1/imprimir", "GET"), ("/api/agenda/unknown", "GET")]:
            start, _, called = await self.request(self.readonly, "InvestidorReadOnlyMiddleware", path, method)
            self.assertEqual((start["status"], called), (403, []))
        self.assertTrue(all(s.closed for s in self.sessions))

    async def test_readonly_allows_passive_science_read_and_auth_infrastructure(self):
        self.investidor = True
        for path, method in [("/api/studies", "GET"), ("/api/auth/sair", "POST")]:
            start, _, called = await self.request(self.readonly, "InvestidorReadOnlyMiddleware", path, method)
            self.assertEqual((start["status"], called), (200, [path]))

    async def test_database_failure_propagates_and_closes_without_permissive_fallback(self):
        self.lookup_error = RuntimeError("pool unavailable")
        for env, name, path in [(self.readonly, "InvestidorReadOnlyMiddleware", "/api/studies"), (self.ephemeral, "InvestidorEphemeralUxMiddleware", "/api/auth/me")]:
            with self.assertRaisesRegex(RuntimeError, "pool unavailable"):
                await self.request(env, name, path)
        self.assertTrue(all(s.closed for s in self.sessions))

    async def test_parallel_requests_do_not_block_loop_or_exhaust_two_connection_pool(self):
        self.query_delay = .04
        ticks = 0
        running = True
        async def clock():
            nonlocal ticks
            while running:
                ticks += 1
                await asyncio.sleep(.005)
        ticker = asyncio.create_task(clock())
        try:
            await asyncio.wait_for(asyncio.gather(*[
                self.request(self.readonly, "InvestidorReadOnlyMiddleware", "/api/studies") for _ in range(24)
            ]), timeout=3)
        finally:
            running = False
            await ticker
        self.assertGreater(ticks, 10, "database work blocked the ASGI event loop")
        self.assertEqual(len(self.sessions), 24)
        self.assertTrue(all(s.closed for s in self.sessions))


if __name__ == "__main__":
    unittest.main(verbosity=2)
