import copy
from datetime import date
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError, URLError

spec = importlib.util.spec_from_file_location('website', Path(__file__).resolve().parents[1] / 'tools/site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


def example():
    return {'schema_version': 1, 'identity': {'name': 'Example Owner', 'role': 'Researcher',
            'affiliation': 'Example University', 'email': 'example@example.org',
            'author_aliases': ['Owner J'], 'links': []}, 'works': [{
        'id': 'example-work', 'kind': 'article', 'status': 'published', 'title': 'A synthetic study',
        'authors': [{'display': 'Do A', 'bibtex': 'Do, A.'}, {'display': 'Owner J', 'bibtex': 'Owner, J.'},
                    {'display': 'García M', 'bibtex': 'García, M.'}, {'display': 'Study Group', 'bibtex': '{Study Group}'}],
        'owner_author_index': 1, 'venue': 'Example Journal', 'date': '2025',
        'doi': '10.1234/example', 'doi_scope': 'work', 'sources': ['https://example.org/paper'],
        'links': [{'label': 'Paper', 'url': 'https://example.org/paper'}], 'related_ids': []}]}


class PublicContractTests(unittest.TestCase):
    def test_private_fields_rejected_at_each_level(self):
        for place in ('root', 'identity', 'work', 'author'):
            d = example()
            target = {'root': d, 'identity': d['identity'], 'work': d['works'][0], 'author': d['works'][0]['authors'][0]}[place]
            target['private_review'] = 'synthetic private content'
            with self.assertRaises(ValueError): site.validate(d)

    def test_owner_position_requires_exact_alias(self):
        for index in (0, 2, 3, 9):
            d = example(); d['works'][0]['owner_author_index'] = index
            with self.assertRaises(ValueError): site.validate(d)

    def test_first_middle_and_later_owner_positions(self):
        for index in (0, 1, 3):
            d = example(); a = d['works'][0]['authors']; owner = a.pop(1); a.insert(index, owner)
            d['works'][0]['owner_author_index'] = index
            site.validate(d)

    def test_duplicate_article_doi_is_normalized(self):
        d = example(); w = copy.deepcopy(d['works'][0]); w['id'] = 'other-work'; w['doi'] = '10.1234/EXAMPLE'; d['works'].append(w)
        with self.assertRaisesRegex(ValueError, 'Duplicate article DOI'): site.validate(d)

    def test_shared_supplement_doi_keeps_abstracts_distinct(self):
        d = example(); w = d['works'][0]; w.update(kind='published_abstract', doi_scope='supplement')
        other = copy.deepcopy(w); other['id'] = 'other-abstract'; d['works'].append(other)
        self.assertEqual(len(site.validate(d)['works']), 2)

    def test_types_and_future_dates(self):
        d = example(); w = d['works'][0]; w['kind'] = 'preprint'
        with self.assertRaises(ValueError): site.validate(d)
        w.update(kind='presentation', status='presented', date='2099-01-01')
        with self.assertRaises(ValueError): site.validate(d, today=date(2026, 11, 7))
        w['status'] = 'accepted'; site.validate(d)

    def test_precision_and_calendar_dates(self):
        d = example()
        for value in ('2025', '2025-02', '2025-02-28'):
            d['works'][0]['date'] = value; site.validate(d)
        d['works'][0]['date'] = '2025-02-30'
        with self.assertRaises(ValueError): site.validate(d)

    def test_unknown_related_output_rejected(self):
        d = example(); d['works'][0]['related_ids'] = ['unknown-work']
        with self.assertRaises(ValueError): site.validate(d)

    def test_conference_identifiers_and_date_ranges(self):
        d = example(); w = d['works'][0]
        w.update(kind='presentation', status='presented', date='2025-09-04', end_date='2025-09-07', abstract_number='P-107', location='Example City')
        site.validate(d)
        with tempfile.TemporaryDirectory() as t:
            site.generate(d, t)
            generated = site.read_json(Path(t) / '_data/publications.json')['works'][0]
            self.assertEqual(generated['date_label'], 'Sep 4–7, 2025')
            self.assertEqual(generated['abstract_number'], 'P-107')
        w['end_date'] = '2025-09-03'
        with self.assertRaises(ValueError): site.validate(d)
        w.pop('end_date'); w.update(kind='article', status='published')
        with self.assertRaises(ValueError): site.validate(d)

    def test_published_abstract_number_reaches_bibtex(self):
        d = example(); w = d['works'][0]; w.update(kind='published_abstract', abstract_number='D-107')
        site.validate(d)
        self.assertIn('Abstract D-107', site.bibliography(d))

    def test_bibliography_is_deterministic_and_preserves_names(self):
        d = example()
        self.assertEqual(site.bibliography(d), site.bibliography(copy.deepcopy(d)))
        bib = site.bibliography(d)
        self.assertIn('García, M.', bib); self.assertIn('{Study Group}', bib)
        self.assertNotIn('<strong>', bib)

    def test_generation_preserves_year_only_and_source(self):
        d = example(); original = copy.deepcopy(d)
        with tempfile.TemporaryDirectory() as t:
            site.generate(d, t); first = (Path(t) / '_bibliography/papers.bib').read_bytes()
            site.generate(d, t)
            self.assertEqual(first, (Path(t) / '_bibliography/papers.bib').read_bytes())
            self.assertEqual(site.read_json(Path(t) / '_data/publications.json')['works'][0]['date_label'], '2025')
        self.assertEqual(d, original)

    def test_removed_work_does_not_leave_a_stale_bib_download(self):
        with tempfile.TemporaryDirectory() as t:
            folder = Path(t) / 'assets/bib'; folder.mkdir(parents=True)
            (folder / 'deleted-work.bib').write_text('synthetic stale export')
            site.generate(example(), t)
            self.assertFalse((folder / 'deleted-work.bib').exists())

    def test_metrics_require_source_date_and_reject_private_extensions(self):
        d = example()
        m = {'source': 'Google Scholar', 'source_url': 'https://scholar.google.com/citations?user=synthetic',
             'as_of': '2025-11-01', 'citations': 12, 'h_index': 2, 'i10_index': 1}
        d['identity']['metrics'] = m; site.validate(d)
        m['as_of'] = '2099-01-01'
        with self.assertRaises(ValueError): site.validate(d)
        m['as_of'] = '2025-11-01'; m['private_note'] = 'synthetic'
        with self.assertRaises(ValueError): site.validate(d)

    def test_career_snapshot_rejects_private_fields(self):
        for key in ('education', 'appointments', 'honors'):
            d = example(); d[key] = [{'title': 'Example item', 'organization': 'Example University', 'dates': '2025', 'private_note': 'synthetic'}]
            with self.assertRaises(ValueError): site.validate(d)

    def test_export_uses_allowlist_and_rejects_first_author_conflict(self):
        raw = {'private_notes': 'do not export', 'scholarly_works': {'entries': [{
            'work_id': 'private-source', 'title': 'Example paper', 'authors': ['Owner J'],
            'first_author': True, 'publication_date': '2025', 'name': 'Example Journal', 'phone': 'synthetic'}]}}
        pick = {'identity': example()['identity'], 'records': [{'work_id': 'private-source', 'id': 'example-work',
                'kind': 'article', 'status': 'published', 'sources': ['https://example.org/paper'], 'owner_token': 'Owner J'}]}
        result = site.export_profile(raw, pick)
        self.assertNotIn('private_notes', json.dumps(result)); self.assertNotIn('phone', json.dumps(result))
        raw['scholarly_works']['entries'][0]['first_author'] = False
        with self.assertRaises(ValueError): site.export_profile(raw, pick)

    def test_private_staging_cannot_be_inside_checkout(self):
        with self.assertRaises(ValueError): site.external_path(site.ROOT / 'ignored-private.json')

    def test_ambiguous_author_requires_review(self):
        for name in ('van der Example J', 'Study Group', 'Owner J Jr'):
            with self.assertRaises(ValueError): site.author_from_token(name)

    def test_abstract_requires_reuse_basis(self):
        d = example(); d['works'][0]['summary'] = {'kind': 'Abstract', 'text': 'Synthetic', 'source': 'https://example.org'}
        with self.assertRaises(ValueError): site.validate(d)


class MetadataTests(unittest.TestCase):
    def test_malformed_and_incomplete_responses(self):
        with self.assertRaises(ValueError): site.crossref_metadata(b'bad json')
        with self.assertRaises(Exception): site.pubmed_metadata(b'<broken>')
        self.assertEqual(site.crossref_metadata(b'{"message":{}}'), {})
        self.assertEqual(site.pubmed_metadata(b'<PubmedArticleSet/>'), {})
        for bad in (b'[]', b'{"message":null}', b'{"message":[]}'):
            with self.assertRaises(ValueError): site.crossref_metadata(bad)

    def test_timeout_404_and_malformed_payload_preserve_approved_snapshot(self):
        for failure in (TimeoutError(), HTTPError('https://example.org', 404, 'absent', {}, None), ValueError('malformed')):
            d = example(); original = copy.deepcopy(d)
            def failed(*args): raise failure
            with tempfile.TemporaryDirectory() as t:
                result = site.refresh(d, t, 'example@example.org', fetch=failed)
                self.assertTrue(all(r['status'] == 'error' for r in result))
            self.assertEqual(d, original)

    def test_candidate_response_never_overwrites_approved(self):
        d = example(); original = copy.deepcopy(d)
        with tempfile.TemporaryDirectory() as t:
            result = site.refresh(d, t, 'example@example.org', fetch=lambda *args: b'{"message":{"title":["Changed title"]}}')
            self.assertEqual(result[0]['candidate']['title'], 'Changed title')
            self.assertEqual(result[0]['status'], 'review')
        self.assertEqual(d, original)

    def test_cache_and_bounded_retries(self):
        attempts = []
        def flaky(*args, **kwargs):
            attempts.append(1)
            if len(attempts) < 3: raise URLError('transient')
            return io.BytesIO(b'{"message":{}}')
        with tempfile.TemporaryDirectory() as t:
            args = ('https://example.org', t, 'test', 'application/json', .4)
            site.cached_request(*args, opener=flaky, sleeper=lambda _: None)
            site.cached_request(*args, opener=flaky, sleeper=lambda _: None)
        self.assertEqual(len(attempts), 3)

    def test_long_provider_retry_after_stops_instead_of_retrying_early(self):
        attempts = []
        def limited(*args, **kwargs):
            attempts.append(1)
            raise HTTPError('https://example.org', 429, 'limited', {'Retry-After': '120'}, None)
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(HTTPError):
                site.cached_request('https://example.org', t, 'test', 'application/json', .4, opener=limited, sleeper=lambda _: None)
        self.assertEqual(len(attempts), 1)

    def test_authorship_and_correction_conflicts_are_flagged(self):
        payload = b'{"message":{"author":[{"family":"Other","given":"Alex"}],"update-to":[{"type":"correction"}]}}'
        with tempfile.TemporaryDirectory() as t:
            result = site.refresh(example(), t, 'example@example.org', fetch=lambda *args: payload)
            self.assertIn('authors', result[0]['changes'])
            self.assertEqual(len(result[0]['alerts']), 2)


class ArtifactTests(unittest.TestCase):
    def test_unknown_files_and_broken_anchors_fail(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); (root / 'index.html').write_text('<a href="#absent">link</a>')
            with self.assertRaisesRegex(ValueError, 'Broken anchor'): site.audit_artifact(root)
            (root / 'index.html').write_text('<h1 id="ok">Example</h1>')
            (root / 'private.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'Unexpected artifact'): site.audit_artifact(root)


if __name__ == '__main__': unittest.main()
