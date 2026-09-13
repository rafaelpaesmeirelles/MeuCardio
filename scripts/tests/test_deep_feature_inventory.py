import importlib.util
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "deep_feature_inventory", Path(__file__).resolve().parents[1] / "deep_feature_inventory.py",
)
INVENTORY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INVENTORY)


def paths(source):
    return {INVENTORY.canonical_api_path(value) for value in INVENTORY.api_references(source)}


class ApiInventoryTests(unittest.TestCase):
    def test_real_search_helper_preserves_search_and_pagination_endpoint(self):
        previous = '''
          api.get<SearchResponse>(`/search?q=${encodeURIComponent(termo)}&limit=100`);
          api.get<SearchResponse>(`/search?q=${encodeURIComponent(assunto)}&limit=100&offset=${nextOffset}`);
          api.get<SearchResponse>(`/search?${query}`);
        '''
        current = '''
          function searchQuery(subject: string, filters: Filters, offset?: number) {
            const query = new URLSearchParams({ q: subject, limit: "100" });
            if (filters.frente) query.set("frente", filters.frente);
            if (offset !== undefined) query.set("offset", String(offset));
            return `/search?${query}`;
          }
          api.get<SearchResponse>(searchQuery(termo, filters), options);
          api.get<SearchResponse>(searchQuery(assunto, filters, nextOffset), options);
        '''
        self.assertEqual(paths(previous), {"/search"})
        self.assertEqual(paths(current), paths(previous))
        self.assertEqual(len(INVENTORY.api_references(current)), 2)

    def test_used_conditional_endpoint_keeps_dedicated_disease_and_drug_paths(self):
        source = '''
          const endpoint = medicamentoSlug
            ? `/relacionados/medicamento/${encodeURIComponent(medicamentoSlug)}`
            : doencaSlug ? `/relacionados/doenca/${encodeURIComponent(doencaSlug)}`
            : `/relacionados?${params.toString()}`;
          api
            .get<Resposta>(endpoint);
        '''
        self.assertEqual(paths(source), {
            "/relacionados/medicamento/{param}", "/relacionados/doenca/{param}", "/relacionados",
        })

    def test_encoding_and_query_variants_do_not_change_endpoint_identity(self):
        self.assertEqual(paths('api.get(`/drug-insights/${medicamentoSlug}`)'),
                         paths('api.get(`/drug-insights/${encodeURIComponent(medicamentoSlug)}`)'))
        self.assertEqual(paths('fetch("https://example.org/api/items?offset=10")'),
                         {"https://example.org/api/items"})

    def test_uncalled_helpers_comments_and_unrelated_variables_do_not_create_paths(self):
        source = '''
          function unused() { return "/dead-helper"; }
          const unusedEndpoint = "/dead-variable";
          // api.get("/commented");
          /* fetch("/also-commented"); */
          function actual() {
            const object = { value: "closing } brace" };
            return `/real/${object.value}`;
          }
          api.get(actual());
        '''
        self.assertEqual(paths(source), {"/real/{param}"})

    def test_local_helper_cannot_be_borrowed_from_another_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "frontend/src"
            source.mkdir(parents=True)
            (source / "caller.ts").write_text("api.get(other());", encoding="utf-8")
            (source / "unrelated.ts").write_text('function other() { return "/unused"; }', encoding="utf-8")
            self.assertEqual(INVENTORY.inventory(root)["api_paths"], [])

    def test_homonymous_declarations_in_other_scopes_are_not_references(self):
        source = '''
          const endpoint = "/shadowed-global";
          function unused() {
            const endpoint = "/dead-sibling";
            function path() { return "/dead-helper"; }
          }
          function actual() {
            const endpoint = "/real-local";
            function path() { return "/real-helper"; }
            api.get(endpoint);
            api.get(path());
          }
        '''
        self.assertEqual(paths(source), {"/real-local", "/real-helper"})

    def test_removing_a_real_endpoint_still_fails_the_unchanged_comparison(self):
        metrics = {key: 100 for key in (
            "backend_endpoints", "frontend_routes", "imported_pages", "interactive_controls",
            "event_bindings", "named_handlers", "api_calls",
        )}
        before = {**metrics, "unique_api_paths": len(paths('api.get("/one"); api.get("/two");'))}
        after = {**metrics, "unique_api_paths": len(paths('api.get("/one?offset=20");'))}
        with self.assertRaisesRegex(AssertionError, "unique_api_paths: 1 < baseline 2"):
            INVENTORY.compare(after, before)


if __name__ == "__main__":
    unittest.main()
