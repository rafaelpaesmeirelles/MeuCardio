"""Regression gates for PR #833 ingestion, taxonomy and actual library links."""
import ast
from collections import defaultdict
from pathlib import Path
import re

import frontmatter
import pytest

ROOT = Path(__file__).resolve().parents[2]
SLUGS = (
    'sinalizadores-ambulatoriais-de-isquemia-critica-ameacadora-de-membro-clti',
    'sinalizadores-ambulatoriais-de-aneurisma-de-aorta-abdominal-ameaca-de-rotura',
    'fluxograma-ambulatorial-dap-quando-encaminhar-urgencia-versus-vascular',
)


@pytest.fixture(scope='module')
def documents():
    result = defaultdict(list)
    for path in (ROOT / 'content').rglob('*.md'):
        post = frontmatter.load(path)
        result[post.get('slug', path.stem)].append((path, post))
    return result


@pytest.fixture(scope='module')
def normalize():
    # Execute the production normalizer without importing unrelated DB/API services.
    tree = ast.parse((ROOT / 'backend/app/api/library.py').read_text(encoding='utf-8'))
    nodes = [node for node in tree.body if (
        isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == '_RELATIVE_DOCUMENT_LINK'
            for t in node.targets
        )
    ) or (isinstance(node, ast.FunctionDef) and node.name == '_library_document_links')]
    assert len(nodes) == 2
    namespace = {'re': re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'library.py', 'exec'), namespace)
    return namespace['_library_document_links']


@pytest.mark.parametrize('slug', SLUGS)
def test_import_metadata_and_flowchart_catalog(slug, documents):
    assert len(documents[slug]) == 1
    path, post = documents[slug][0]
    assert path.stem == slug
    assert post['theme'] == 'Aorta e doença arterial periférica'
    assert post['kind'] == ('fluxograma' if slug.startswith('fluxograma-') else 'protocolo')
    assert isinstance(post['source_refs'], list)
    assert all(isinstance(ref, str) for ref in post['source_refs'])
    assert '10.1093/eurheartj/ehae179' in post['source_refs'][0]
    assert '39210722' in post['source_refs'][0]


@pytest.mark.parametrize('slug', SLUGS)
def test_every_link_resolves_through_actual_app_normalizer(slug, documents, normalize):
    path, post = documents[slug][0]
    links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', post.content)
    assert links, 'Clinical cross-links must be navigable, not bare code spans.'
    for target in links:
        assert target.endswith('.md') and not target.startswith(('http', '/'))
        target_slug = Path(target).stem
        assert len(documents[target_slug]) == 1, (slug, target)
        target_path, target_post = documents[target_slug][0]
        assert (path.parent / target).resolve() == target_path.resolve()
        assert target_post['review_status'] == 'revisado' or target_slug in SLUGS
        assert normalize(f'[open]({target})') == f'[open](/biblioteca/{target_slug})'
    assert 'corvia-intelligence-' not in post.content
    assert not re.search(r'`(?:sinalizadores|fluxograma|doenca|aneurisma|isquemia)-[^`]+`', post.content)
