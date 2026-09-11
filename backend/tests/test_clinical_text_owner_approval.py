"""Pure display-proof tests: no database, clinical publication or approval writes."""
import copy
import hashlib
import json
from types import SimpleNamespace
import unittest

import pytest

from app.services.clinical_text import _approved_change_payload


@pytest.fixture(autouse=True)
def _banco_limpo():
    yield


class ApprovedClinicalDisplayTests(unittest.TestCase):
    def setUp(self):
        self.impact = {'item_type': 'disease', 'item_id': 7, 'target_section': 'definicao',
            'override_pt': 'Texto de teste, não recomendação clínica.',
            'change_summary_pt': 'Alteração sintética', 'source_url': 'https://example.test/source'}
        self.source = {'id': 3, 'source_fingerprint': 'a' * 64, 'superseded_by_id': None}
        self.before = {'slug': 'synthetic-disease', 'summary': 'Definição intacta', 'version': 1}
        self.after = {**self.before, 'version': 2}
        change = {'item_type': 'disease', 'item_id': 7, 'slug': 'synthetic-disease',
            'before': self.before, 'after': self.after, 'impact': self.impact,
            'source_url': self.impact['source_url'], 'change_summary_pt': self.impact['change_summary_pt']}
        payload = {'source': self.source, 'changes': [change]}
        fingerprint = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
            separators=(',', ':')).encode()).hexdigest()
        self.proposal = SimpleNamespace(id=5, guideline_id=3, status='approved', reviewer_id=11,
            reviewed_at='2026-09-11T00:00:00Z', payload=payload, fingerprint=fingerprint)
        self.link = {**self.impact, 'proposal_id': 5, 'fingerprint': fingerprint, 'reviewer_id': 11,
            'mode': 'owner_approved_exact_snapshot', 'before': self.before, 'applied_at': '2026-09-11T00:00:00Z'}
        self.context = {'item_type': 'disease', 'item_id': 7, 'slug': 'synthetic-disease',
            'source_snapshot': self.source, 'target_snapshot': self.after, 'approval_proven': True}

    def result(self, link=None, proposal=None, **context):
        return _approved_change_payload(self.link if link is None else link,
            self.proposal if proposal is None else proposal, **{**self.context, **context})

    def test_exact_applied_owner_approval_is_visible_without_mutating_records(self):
        original = copy.deepcopy((self.link, self.proposal.__dict__, self.context))
        result = self.result()
        self.assertEqual(result, {**self.impact, 'applied_at': self.link['applied_at']})
        self.assertEqual((self.link, self.proposal.__dict__, self.context), original)

    def test_missing_pending_rejected_or_unproven_approval_is_not_visible(self):
        self.assertIsNone(_approved_change_payload(self.link, None, **self.context))
        self.assertIsNone(self.result(approval_proven=False))
        for status in ('pending', 'rejected'):
            with self.subTest(status=status):
                self.assertIsNone(self.result(proposal=SimpleNamespace(**{**self.proposal.__dict__, 'status': status})))
        for field in ('reviewer_id', 'reviewed_at'):
            self.assertIsNone(self.result(proposal=SimpleNamespace(**{**self.proposal.__dict__, field: None})))

    def test_link_cannot_borrow_an_approval_for_another_entity_or_field(self):
        for field, value in (('proposal_id', 999), ('reviewer_id', 999), ('fingerprint', 'b' * 64),
                             ('mode', 'intelligence'), ('item_type', 'drug'), ('item_id', 8),
                             ('target_section', 'tratamento'), ('override_pt', 'Outro texto'),
                             ('source_url', 'https://example.test/other'), ('before', {})):
            with self.subTest(field=field):
                self.assertIsNone(self.result(link={**self.link, field: value}))
        for field, value in (('item_type', 'drug'), ('item_id', 8), ('slug', 'another-disease')):
            with self.subTest(context=field):
                self.assertIsNone(self.result(**{field: value}))

    def test_changed_payload_source_or_current_content_invalidates_the_display_proof(self):
        changed = copy.deepcopy(self.proposal)
        changed.payload['changes'][0]['after']['summary'] = 'Conteúdo diferente'
        self.assertIsNone(self.result(proposal=changed))
        for source in ({**self.source, 'source_fingerprint': 'b' * 64},
                       {**self.source, 'id': 4}, {**self.source, 'superseded_by_id': 4}):
            self.assertIsNone(self.result(source_snapshot=source))
        self.assertIsNone(self.result(target_snapshot={**self.after, 'summary': 'Revisão posterior'}))
        self.assertIsNone(self.result(target_snapshot=self.before))


if __name__ == '__main__':
    unittest.main()
