"""Offline regression tests for native-app retirement and its release contract."""
from __future__ import annotations

import ast
from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
import importlib.util
import io
import json
from pathlib import Path
import re
import ssl
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "public_app_retirement_gate", ROOT / "scripts/validate_public_app_artifacts.py",
)
assert SPEC and SPEC.loader
GATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GATE
SPEC.loader.exec_module(GATE)


def response_headers(cache_control="no-store, no-cache", location=None):
    headers = Message()
    if cache_control is not None:
        headers["Cache-Control"] = cache_control
    if location is not None:
        headers["Location"] = location
    return headers


class RetirementTests(unittest.TestCase):
    def install_opener(self, *, status=410, cache_control="no-store", location=None):
        calls = []
        opener = Mock()
        def open_request(request, timeout):
            calls.append((request, timeout))
            raise urllib.error.HTTPError(
                request.full_url, status, "test response",
                response_headers(cache_control, location), io.BytesIO(b""),
            )
        opener.open.side_effect = open_request
        mocked = patch.object(GATE.urllib.request, "build_opener", return_value=opener)
        build = mocked.start()
        self.addCleanup(mocked.stop)
        return calls, opener, build

    def test_all_aliases_and_sidecars_are_checked(self):
        calls, _, _ = self.install_opener()
        report = GATE.validate_retired(GATE.DEFAULT_BASE_URL, ("android", "windows"))
        expected = {
            GATE.DEFAULT_BASE_URL + path + suffix
            for paths in GATE.RETIRED_PATHS.values()
            for path in paths for suffix in ("", ".sha256")
        }
        self.assertEqual({request.full_url for request, _ in calls}, expected)
        self.assertEqual(len(calls), 16)
        self.assertEqual(report["release_status"], {"android": "retired", "windows": "retired"})
        self.assertEqual(sum(map(len, report["retired_routes"].values())), 16)

    def test_original_and_cache_busted_urls_are_both_checked(self):
        calls, _, _ = self.install_opener()
        GATE.validate_retired(GATE.DEFAULT_BASE_URL, ("android", "windows"), "release / 123")
        self.assertEqual(len(calls), 32)
        for position in range(0, len(calls), 2):
            original = urllib.parse.urlsplit(calls[position][0].full_url)
            fresh = urllib.parse.urlsplit(calls[position + 1][0].full_url)
            self.assertEqual(original.path, fresh.path)
            self.assertEqual(original.query, "")
            self.assertEqual(urllib.parse.parse_qs(fresh.query), {"release": ["release / 123"]})

    def test_selected_apps_only_and_no_duplicate_requests(self):
        calls, _, _ = self.install_opener()
        report = GATE.validate_retired(GATE.DEFAULT_BASE_URL, ("windows", "windows"))
        self.assertEqual(len(calls), 6)
        self.assertEqual(report["release_status"], {"android": "not_checked", "windows": "retired"})

    def test_all_non_gone_statuses_fail_closed(self):
        calls, opener, _ = self.install_opener()
        for code in (200, 204, 301, 302, 303, 307, 308, 401, 403, 404, 500, 502):
            with self.subTest(code=code):
                opener.open.side_effect = urllib.error.HTTPError(
                    GATE.DEFAULT_BASE_URL, code, "not retired", response_headers(), io.BytesIO(),
                )
                with self.assertRaisesRegex(AssertionError, "expected retired status 410"):
                    GATE.validate_retired(GATE.DEFAULT_BASE_URL, ("android",))

    def test_successful_binary_response_is_rejected_without_reading_body(self):
        _, opener, _ = self.install_opener()
        response = Mock()
        response.getcode.return_value = 200
        response.headers = response_headers("public, max-age=31536000, immutable")
        response.read.side_effect = AssertionError("Must never download binary")
        context = Mock()
        context.__enter__ = Mock(return_value=response)
        context.__exit__ = Mock(return_value=False)
        opener.open.side_effect = None
        opener.open.return_value = context
        with self.assertRaisesRegex(AssertionError, "got 200"):
            GATE.validate_retired(GATE.DEFAULT_BASE_URL, ("android",))
        response.read.assert_not_called()

    def test_missing_or_inadequate_cache_control_fails(self):
        _, opener, _ = self.install_opener()
        for header in (None, "", "public, max-age=31536000, immutable", "no-cache", "x-no-store"):
            with self.subTest(header=header):
                opener.open.side_effect = urllib.error.HTTPError(
                    GATE.DEFAULT_BASE_URL, 410, "gone", response_headers(header), io.BytesIO(),
                )
                with self.assertRaisesRegex(AssertionError, "lacks no-store"):
                    GATE.validate_retired(GATE.DEFAULT_BASE_URL, ("android",))

    def test_cache_control_is_case_insensitive(self):
        self.install_opener(cache_control="No-Cache, No-Store, max-age=0")
        self.assertEqual(GATE.validate_retired(GATE.DEFAULT_BASE_URL, ("android",))["release_status"]["android"], "retired")

    def test_retired_response_with_location_is_rejected(self):
        self.install_opener(location="https://corvia.med.br/live.apk")
        with self.assertRaisesRegex(AssertionError, "has Location"):
            GATE.validate_retired(GATE.DEFAULT_BASE_URL, ("android",))

    def test_unknown_or_empty_selection_never_opens_network(self):
        with patch.object(GATE.urllib.request, "build_opener") as build:
            for names in ((), ("linux",), ("android", "linux")):
                with self.subTest(names=names), self.assertRaises(AssertionError):
                    GATE.validate_retired(GATE.DEFAULT_BASE_URL, names)
            build.assert_not_called()

    def test_only_authorized_https_origin_is_allowed(self):
        with patch.object(GATE.urllib.request, "build_opener") as build:
            for url in (
                "http://corvia.med.br", "https://example.test", "https://corvia.med.br.evil.test",
                "https://user:pass@corvia.med.br", "https://corvia.med.br:444",
                "https://corvia.med.br/prefix", "https://corvia.med.br?q=x", "https://corvia.med.br#x",
            ):
                with self.subTest(url=url), self.assertRaises(AssertionError):
                    GATE.validate_retired(url, ("android",))
            build.assert_not_called()

    def test_opener_rejects_redirects_and_verifies_tls(self):
        _, _, build = self.install_opener()
        GATE.validate_retired(GATE.DEFAULT_BASE_URL, ("android",))
        https, redirects = build.call_args.args
        self.assertIsInstance(https, urllib.request.HTTPSHandler)
        self.assertEqual(https._context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(https._context.check_hostname)
        self.assertIsInstance(redirects, GATE._NoRedirects)
        self.assertIsNone(redirects.redirect_request(None, None, 308, "redirect", {}, "https://example.test"))

    def test_requests_have_bounded_timeout_and_cache_revalidation(self):
        calls, _, _ = self.install_opener()
        GATE.validate_retired(GATE.DEFAULT_BASE_URL, ("android",))
        for request, timeout in calls:
            self.assertEqual(timeout, 30)
            self.assertEqual(request.get_method(), "GET")
            self.assertIn("no-store", request.get_header("Cache-control"))

    def test_network_errors_are_not_reported_as_retired(self):
        _, opener, _ = self.install_opener()
        opener.open.side_effect = urllib.error.URLError("unavailable")
        with self.assertRaises(urllib.error.URLError):
            GATE.validate_retired(GATE.DEFAULT_BASE_URL, ("android",))


class CommandLineTests(unittest.TestCase):
    def invoke(self, *arguments):
        output = io.StringIO()
        with patch.object(sys, "argv", ["gate", *arguments]), redirect_stdout(output), redirect_stderr(io.StringIO()):
            code = GATE.main()
        return code, output.getvalue()

    def test_retirement_mode_does_not_call_published_binary_validator(self):
        report = {"release_status": {"android": "retired", "windows": "retired"}}
        with patch.object(GATE, "validate_retired", return_value=report) as retired, patch.object(GATE, "validate") as published:
            code, output = self.invoke("--retired", "android", "windows", "--cache-buster", "sha")
        self.assertEqual(code, 0)
        retired.assert_called_once_with(GATE.DEFAULT_BASE_URL, ("android", "windows"), "sha")
        published.assert_not_called()
        self.assertEqual(json.loads(output), report)

    def test_default_published_mode_is_backward_compatible(self):
        with patch.object(GATE, "validate", return_value={}) as published, patch.object(GATE, "validate_retired") as retired:
            code, output = self.invoke()
        self.assertEqual(code, 0)
        self.assertEqual(published.call_args.kwargs["specs"], GATE.SPECS)
        retired.assert_not_called()
        self.assertEqual(json.loads(output)["release_status"], {"android": "published", "windows": "published"})

    def test_explicit_published_selection_is_preserved(self):
        with patch.object(GATE, "validate", return_value={}) as published:
            code, output = self.invoke("--artifacts", "android")
        self.assertEqual([spec.name for spec in published.call_args.kwargs["specs"]], ["android"])
        self.assertEqual(json.loads(output)["release_status"]["windows"], "pending")

    def test_published_and_retired_modes_are_mutually_exclusive(self):
        with self.assertRaises(SystemExit) as caught:
            self.invoke("--retired", "android", "--artifacts", "windows")
        self.assertEqual(caught.exception.code, 2)

    def test_retirement_rejects_binary_digest_arguments(self):
        with self.assertRaises(SystemExit) as caught:
            self.invoke("--retired", "android", "--expected-android-sha256", "a" * 64)
        self.assertEqual(caught.exception.code, 2)

    def test_retirement_failure_exits_nonzero_without_success_report(self):
        with patch.object(GATE, "validate_retired", side_effect=AssertionError("still live")):
            code, output = self.invoke("--retired", "android", "windows")
        self.assertEqual(code, 1)
        self.assertEqual(output, "")

    def test_retirement_report_is_written_after_success(self):
        report = {"release_status": {"android": "retired", "windows": "retired"}}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "reports/native.json"
            with patch.object(GATE, "validate_retired", return_value=report):
                code, _ = self.invoke("--retired", "android", "windows", "--report", str(path))
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(path.read_text()), report)


class ReleaseAndProxyContractTests(unittest.TestCase):
    def test_all_known_and_future_native_paths_match_retirement_rule(self):
        source = (ROOT / "infra/Caddyfile").read_text()
        pattern = next(line.strip().split(maxsplit=3)[3] for line in source.splitlines() if "@native_apps_retired path_regexp " in line)
        routes = [path + suffix for paths in GATE.RETIRED_PATHS.values() for path in paths for suffix in ("", ".sha256")]
        routes += ["/downloads/corvia-cardiology-spaces-android-9.9.9.apk", "/downloads/corvia-os-windows-9.9.9.zip.sha256"]
        for route in routes:
            with self.subTest(route=route):
                self.assertIsNotNone(re.fullmatch(pattern, route))
        for route in ("/assets/logo.svg", "/galeria/heart.png", "/downloads/report.pdf", "/api/ready"):
            with self.subTest(route=route):
                self.assertIsNone(re.fullmatch(pattern, route))
        body = re.search(r"handle @native_apps_retired \{([^}]+)\}", source).group(1)
        self.assertIn('respond "Aplicativos Android e Windows descontinuados" 410', body)
        self.assertIn("no-store", body)
        self.assertNotIn("file_server", body)
        self.assertNotIn("redir /downloads/", source)
        self.assertNotIn("root * /downloads", source)

    def test_documentation_deny_is_inside_api_handler_before_proxy(self):
        source = (ROOT / "infra/Caddyfile").read_text()
        body = re.search(r"handle /api/\* \{([^}]+)\}", source).group(1)
        self.assertLess(body.index("respond @private_backend_docs 404"), body.index("reverse_proxy backend:8000"))
        matcher = next(line for line in source.splitlines() if "@private_backend_docs path " in line)
        for path in ("/api/docs", "/api/openapi.json", "/api/redoc"):
            self.assertIn(path, matcher)
        for path in ("/api/health", "/api/ready", "/api/version", "/api/auth"):
            self.assertNotIn(path, matcher)
        private = re.search(r"handle @private_public_metadata \{([^}]+)\}", source).group(1)
        self.assertIn("respond 404", private)
        self.assertIn("no-store", private)
        self.assertIn("/.vite/*", source)

    def test_actual_deploy_policy_method_still_requires_every_gate(self):
        # Execute the existing, targeted unittest method without importing the
        # unrelated risk classifier and its repository-wide path fixtures.
        source = (ROOT / "scripts/tests/test_ci_backend_policy.py").read_text()
        cls = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef) and node.name == "WorkflowPolicyContractTests")
        method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "test_deploy_requires_backend_risk_gate_from_ci")
        namespace = {"ROOT": ROOT}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), "deploy_policy_contract", "exec"), namespace)
        namespace[method.name](self)

    def test_real_postdeploy_commands_enforce_retirement_and_private_metadata(self):
        workflow = (ROOT / ".github/workflows/deploy-production.yml").read_text()
        normalized = workflow.replace("\\\n", " ")
        self.assertRegex(normalized, r'python3 scripts/validate_public_app_artifacts\.py\s+--base-url "\$PUBLIC_URL" --retired android windows')
        self.assertIn('--report "$RUNNER_TEMP/retired-apps.json"', workflow)
        self.assertIn('[[ "$status" == 404 ]]', workflow)
        self.assertNotIn("continue-on-error", workflow)
        self.assertIn("/.vite/manifest.json", workflow)
        self.assertIn("Mandatory gates are not all green for this exact SHA", workflow)


if __name__ == "__main__":
    unittest.main()
