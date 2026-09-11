"""Read-only, deterministic geometry candidate for licensed Kairos issue 453.

No application imports, network, inferred substances, arithmetic prices or writes
to the repository. Default is a dry run. --write-candidate requires a new /tmp
directory; all monetary strings come directly from positioned PDF glyphs.
Coordinates are MediaBox points with top-left origin, NOT cropped PNG pixels.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

import pdfplumber

FIELDS = ('pf20', 'pmc20', 'pf18', 'pmc18', 'pf17', 'pmc17', 'pf12', 'pmc12')
RIGHT_EDGES = (172.174, 196.267, 219.228, 243.037, 267.135, 289.811, 312.487, 336.013)
SIDES = (('left', 72.266, 337.021, 0.0), ('right', 343.259, 608.014, 270.993))
EXPECTED_SHA = '32e4dff5205f7387040900df9820a65b78825e12028db698aa11c482297bc142'


def box(chars):
    return [round(min(c['x0'] for c in chars), 4), round(min(c['top'] for c in chars), 4),
            round(max(c['x1'] for c in chars), 4), round(max(c['bottom'] for c in chars), 4)] if chars else None


def text(chars):
    """Keep literal glyphs and spaces; insert only visible >0.8 pt word gaps."""
    ordered = sorted(chars, key=lambda c: c['x0'])
    result = ''
    previous = None
    for c in ordered:
        if previous and c['x0'] - previous['x1'] > .8 and not result.endswith(' ') and c['text'] != ' ':
            result += ' '
        result += c['text']
        previous = c
    return re.sub(r'\s+', ' ', result).strip()


def rows(chars):
    grouped = []
    for c in sorted(chars, key=lambda c: (c['top'], c['x0'])):
        if not grouped or c['top'] - grouped[-1][0]['top'] > 1.15:
            grouped.append([c])
        else:
            grouped[-1].append(c)
    return grouped


def font(c):
    return c['fontname'].split('+')[-1]


def is_bold(c):
    return 'Bold' in font(c) and abs(c['size'] - 5.5) < .1


def normal(value):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower())


def duplicate_key(value):
    return ''.join(unicodedata.normalize('NFKC', value or '').casefold().split())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--schema-template', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--write-candidate', action='store_true')
    args = parser.parse_args()
    with args.source.open('rb') as handle:
        source_hash = hashlib.file_digest(handle, 'sha256').hexdigest()
    if source_hash != EXPECTED_SHA:
        parser.error('Source SHA differs: this candidate is pinned to the inspected issue, not a generic parser.')
    if args.write_candidate:
        if not args.output_dir or not str(args.output_dir.resolve()).startswith(('/tmp/', '/private/tmp/')):
            parser.error('--write-candidate requires an explicit new directory under /tmp')
        args.output_dir.mkdir(parents=False, exist_ok=False)
    template = json.loads(args.schema_template.read_text())
    snapshot = {k: v for k, v in template.items() if k != 'records'}
    snapshot['records'] = []
    snapshot['parse_evidence'] = {
        'status': 'candidate_not_active', 'source_sha256': source_hash, 'source_file': args.source.name,
        'pages_requested': [8, 78], 'coordinate_system': 'MediaBox points, top-left origin',
        'method': 'native glyph fonts, row baselines and fixed right-edge anchors; no OCR or inferred prices/substances',
        'scope_note': 'All extractable price rows in physical pages 8–78; not a claim of full market or regulatory coverage.',
    }
    report = {'source_sha256': source_hash, 'status': 'candidate_not_active', 'warnings': [],
              'quarantined': [], 'pages': [], 'continuations': [], 'duplicate_presentations': [], 'baseline_comparison': [],
              'baseline_substance_comparison': [], 'activation_permitted': False}
    records = {}
    current = None
    pending = []
    all_fonts = Counter()
    total_numeric_tokens = 0

    def warn(code, location, **details):
        report['warnings'].append({'code': code, **location, **details})

    def location(number, side, line, chars):
        return {'page': number, 'source_side': side, 'source_line': line, 'bbox': box(chars)}

    def emit(prices, price_location, price_glyphs, parse_notes=()):
        nonlocal pending
        presentation_text = ' '.join(item['text'] for item in pending).strip()
        evidence = {'source_side': price_location['source_side'], 'source_line': price_location['source_line'],
                    'source_page': price_location['page'], 'bbox': price_location['bbox'],
                    'source_description_lines': pending, 'source_price_glyphs': price_glyphs,
                    'parse_notes': list(parse_notes)}
        if not current or not current.get('product') or not current.get('laboratory') or not presentation_text:
            report['quarantined'].append({'reason': 'incomplete_identity_or_presentation', 'identity': current,
                                          'presentation': presentation_text, 'prices': prices, **evidence})
            pending = []
            return
        key = (current['id'], price_location['page'])
        if key not in records:
            record = {k: current[k] for k in ('product', 'laboratory', 'substance')}
            record.update(page=price_location['page'], presentations=[], source_header=current['source_header'],
                          source_substance_lines=current['source_substance_lines'],
                          source_header_markers=current['source_header_markers'],
                          source_record_id=f"kairos453-p{current['id'][0]}-{current['id'][1]}-l{current['id'][2]}-pricesp{price_location['page']}")
            records[key] = record
            snapshot['records'].append(record)
        record = records[key]
        record['substance'] = current['substance']
        record['substance_parse_status'] = ('ambiguous_superscript_annotation' if current.get('ambiguous_substance')
                                            else 'explicit' if current['substance'] else 'not_printed')
        record['presentations'].append({'presentation': presentation_text, **prices, **evidence})
        if any(item['page'] != price_location['page'] or item['source_side'] != price_location['source_side'] for item in pending):
            report['continuations'].append({'type': 'presentation_description_continues', 'product': current['product'],
                                            'price_location': price_location, 'description_locations': pending})
        pending = []

    with pdfplumber.open(args.source) as pdf:
        if len(pdf.pages) != 80:
            parser.error('Expected 80 physical pages')
        for number in range(8, 79):
            page = pdf.pages[number - 1]
            if (round(page.width), round(page.height)) != (680, 907):
                raise ValueError(f'Unexpected MediaBox on page {number}')
            page_info = {'page': number, 'size': [page.width, page.height], 'cropbox': list(page.cropbox), 'sides': []}
            for side, x0, x1, shift in SIDES:
                # Header font size distinguishes the four tax labels from the
                # smaller state/tax legend. Both PF/PMC header rows are checked.
                header = [c for c in page.chars if x0 - .5 <= c['x0'] <= x1 and 7.9 <= c['size'] < 8.1 and c['top'] < 215]
                header_rows = rows(header)
                pf_headers = [r for r in header_rows if 'PF' in text(r) and 'PMC' in text(r)]
                if len(pf_headers) != 1 or re.sub(r'\s', '', text(pf_headers[0])) != 'PFPMCPFPMCPFPMCPFPMC':
                    raise ValueError(f'Unrecognized tax header page {number} {side}')
                body_top = max(c['bottom'] for c in pf_headers[0]) + .5
                chars = [c for c in page.chars if x0 - .5 <= c['x0'] and c['x1'] <= x1 + .5 and body_top <= c['top'] < 816]
                all_fonts.update((font(c), round(c['size'], 2)) for c in chars)
                lines = rows(chars)
                page_info['sides'].append({'side': side, 'x_range': [x0, x1], 'body_top': body_top, 'body_bottom': 816,
                                           'lines': len(lines), 'price_right_edges': [round(a + shift, 3) for a in RIGHT_EDGES]})
                previous_header = current['product'] if current else None
                first_data = True
                for line_number, line in enumerate(lines, start=1):
                    loc = location(number, side, line_number, line)
                    useful = [c for c in line if c['text'].strip() and 'Dingbats' not in font(c)]
                    if not useful:
                        continue
                    # Large alphabetical navigation glyphs are not products.
                    if all(c['size'] >= 12 for c in useful):
                        continue
                    bold = [c for c in useful if is_bold(c)]
                    title_start = [c for c in bold if c['x0'] < x0 + 10 and re.search(r'[A-Za-zÀ-ÿ]', c['text'])]
                    laboratory_chars = [c for c in useful if font(c) == 'HelveticaLTStdCond' and abs(c['size'] - 6) < .1]
                    if title_start:
                        if pending:
                            warn('unpriced_description_before_header', loc, product=current['product'] if current else None, description=pending)
                            emit({}, pending[-1], [], ['no_price_row_before_next_header'])
                        product = text(bold)
                        laboratory = text(laboratory_chars)
                        current = {'id': (number, side, line_number), 'product': product, 'laboratory': laboratory,
                                   'substance': None, 'source_header': loc, 'source_substance_lines': [],
                                   'source_header_markers': [{'glyph': c['text'], 'font': font(c), 'bbox': box([c])}
                                                             for c in line if 'Dingbats' in font(c)]}
                        if not laboratory:
                            warn('header_without_laboratory', loc, product=product, raw_line=text(useful))
                        if first_data:
                            first_data = False
                        continue
                    if first_data:
                        report['continuations'].append({'type': 'column_or_page_inherits_header', **loc, 'product': previous_header,
                                                        'header_location': current['source_header'] if current else None})
                        first_data = False
                    small = [c for c in useful if 3 <= c['size'] <= 4.1 and 'Dingbats' not in font(c)]
                    descriptions = [c for c in useful if 'CondLight' in font(c) and 5.4 <= c['size'] <= 6.1]
                    known = set(map(id, bold + small + descriptions + laboratory_chars))
                    unknown = [c for c in useful if id(c) not in known and not (c['size'] >= 12 and c['text'].strip())]
                    annotations = [c for c in unknown if font(c) == 'HelveticaCondensed' and abs(c['size'] - 2) < .1]
                    if annotations and len(annotations) == len(unknown) and small and current and not pending:
                        # A 2 pt elevated glyph is visible in the source but is
                        # not safely interpretable as part of an ingredient.
                        # Keep raw positioned glyphs; never concatenate 3350+2
                        # into a different substance or silently drop it.
                        current['ambiguous_substance'] = True
                        warn('ambiguous_substance_annotation', loc, product=current['product'],
                             base_text=text(small), annotations=[{'glyph': c['text'], 'font': font(c),
                                                                  'size': c['size'], 'bbox': box([c])} for c in annotations],
                             treatment='substance=null; full glyph evidence retained; editorial review required')
                    elif unknown:
                        warn('unknown_glyph_style', loc, raw=text(unknown), styles=sorted({(font(c), round(c['size'], 2)) for c in unknown}))
                    if laboratory_chars:
                        warn('laboratory_without_same_line_header', loc, raw=text(laboratory_chars))
                    if small:
                        raw_substance = text(small)
                        if current and not pending and re.search(r'[A-Za-zÀ-ÿ]', raw_substance):
                            evidence = {'text': raw_substance, **loc}
                            if annotations:
                                evidence['source_glyphs'] = [{'text': c['text'], 'font': font(c), 'size': c['size'], 'bbox': box([c])}
                                                             for c in sorted(small + annotations, key=lambda c: c['x0'])]
                            current['source_substance_lines'].append(evidence)
                            current['substance'] = None if current.get('ambiguous_substance') else ' '.join(row['text'] for row in current['source_substance_lines'])
                        else:
                            warn('unattached_small_type', loc, raw=raw_substance)
                    if descriptions:
                        pending.append({'text': text(descriptions), **loc})
                    if not bold:
                        continue
                    numeric_chars = sorted(bold, key=lambda c: c['x0'])
                    raw = ''.join(c['text'] for c in numeric_chars)
                    matches = list(re.finditer(r'\d+,\d{2}', raw))
                    prices, glyphs, errors = {}, [], []
                    used = set()
                    for match in matches:
                        selected = numeric_chars[match.start():match.end()]
                        end = selected[-1]['x1']
                        distances = [abs(end - (anchor + shift)) for anchor in RIGHT_EDGES]
                        slot = min(range(8), key=lambda i: distances[i])
                        total_numeric_tokens += 1
                        item = {'raw': match.group(), 'bbox': box(selected), 'slot': FIELDS[slot], 'right_edge_error': round(distances[slot], 4)}
                        glyphs.append(item)
                        used.update(range(match.start(), match.end()))
                        if distances[slot] > 1.0:
                            errors.append({'reason': 'price_outside_slot_anchor', **item})
                        elif FIELDS[slot] in prices:
                            errors.append({'reason': 'duplicate_price_slot', **item})
                        else:
                            prices[FIELDS[slot]] = match.group()
                    remainder = ''.join(c['text'] for i, c in enumerate(numeric_chars) if i not in used).strip()
                    if remainder:
                        errors.append({'reason': 'unparsed_bold_glyphs', 'raw': remainder})
                    if errors:
                        report['quarantined'].append({'reason': 'ambiguous_price_row', **loc, 'identity': current,
                                                      'description': pending, 'glyphs': glyphs, 'errors': errors})
                        warn('ambiguous_price_row', loc, errors=errors)
                        pending = []
                    elif prices:
                        emit(prices, loc, glyphs)
            report['pages'].append(page_info)
            page.close()
            if number % 10 == 0:
                print(f'parsed page {number}; records={len(records)} warnings={len(report["warnings"])} quarantined={len(report["quarantined"])}', file=sys.stderr)
    if pending:
        warn('unpriced_final_description', pending[-1], description=pending)
        emit({}, pending[-1], [], ['no_price_row_at_end_of_document'])
    duplicate_groups = defaultdict(list)
    for record in snapshot['records']:
        for presentation in record['presentations']:
            key = tuple(duplicate_key(value) for value in (record['product'], record['laboratory'], presentation['presentation']))
            duplicate_groups[key].append({'product': record['product'], 'laboratory': record['laboratory'], 'presentation': presentation['presentation'],
                                           'substance': record['substance'], 'page': record['page'], 'side': presentation['source_side'], 'line': presentation['source_line'],
                                           'prices': {f: presentation[f] for f in FIELDS if f in presentation}})
    for key, entries in duplicate_groups.items():
        if len(entries) > 1:
            report['duplicate_presentations'].append({'product': entries[0]['product'], 'laboratory': entries[0]['laboratory'],
                                                      'presentation': entries[0]['presentation'], 'occurrences': entries,
                                                      'conflicting_prices': any(len({e['prices'][f] for e in entries if f in e['prices']}) > 1 for f in FIELDS),
                                                      'different_price_coverage': len({tuple(e['prices']) for e in entries}) > 1,
                                                      'conflicting_substance': len({duplicate_key(e['substance']) for e in entries}) > 1})
    for baseline in template['records']:
        candidates = [r for r in snapshot['records'] if normal(r['product']) == normal(baseline['product']) and normal(r['laboratory']) == normal(baseline['laboratory'])]
        report['baseline_substance_comparison'].append({'product': baseline['product'], 'laboratory': baseline['laboratory'],
                                                        'baseline_substance': baseline['substance'], 'pdf_substances': [r['substance'] for r in candidates],
                                                        'status': 'same_explicit_text' if any(normal(r['substance'] or '') == normal(baseline['substance']) for r in candidates)
                                                        else 'not_printed_or_different_do_not_infer'})
        for old in baseline['presentations']:
            exact = [(r, p) for r in candidates for p in r['presentations'] if normal(p['presentation']) == normal(old['presentation'])]
            price_equal = [(r, p) for r in candidates for p in r['presentations'] if all(p.get(f) == old.get(f) for f in FIELDS)]
            status = 'exact_text_prices' if any(all(p.get(f) == old.get(f) for f in FIELDS) for _, p in exact) else ('same_prices_text_variant' if price_equal else 'unmatched_or_different_prices')
            report['baseline_comparison'].append({'product': baseline['product'], 'laboratory': baseline['laboratory'], 'page': baseline['page'],
                                                  'presentation': old['presentation'], 'status': status,
                                                  'matches': [{'page': r['page'], 'presentation': p['presentation']} for r, p in (exact or price_equal)],
                                                  'diagnostic_nearest_text': max((p['presentation'] for r in candidates for p in r['presentations']), key=lambda v: SequenceMatcher(None, normal(v), normal(old['presentation'])).ratio(), default=None)})
    presentations = [p for r in snapshot['records'] for p in r['presentations']]
    report['summary'] = {'pages_parsed': len(report['pages']), 'records_grouped_by_header_and_page': len(snapshot['records']),
                         'distinct_product_laboratory': len({(r['product'], r['laboratory']) for r in snapshot['records']}),
                         'presentations': len(presentations), 'prices': sum(f in p for p in presentations for f in FIELDS),
                         'numeric_tokens_seen': total_numeric_tokens, 'substance_status': dict(Counter(r['substance_parse_status'] for r in snapshot['records'])),
                         'price_field_patterns': dict(Counter(','.join(f for f in FIELDS if f in p) for p in presentations)),
                         'warnings_by_code': dict(Counter(w['code'] for w in report['warnings'])), 'quarantined': len(report['quarantined']),
                         'duplicate_presentations': len(report['duplicate_presentations']),
                         'conflicting_duplicate_groups': sum(row['conflicting_prices'] or row['conflicting_substance'] for row in report['duplicate_presentations']),
                         'conflicting_duplicate_occurrences': sum(len(row['occurrences']) for row in report['duplicate_presentations'] if row['conflicting_prices'] or row['conflicting_substance']),
                         'baseline_rows': len(report['baseline_comparison']), 'baseline_status': dict(Counter(row['status'] for row in report['baseline_comparison']))}
    report['fonts'] = [{'font': key[0], 'size': key[1], 'glyphs': value} for key, value in all_fonts.most_common()]
    report['extraction_completed'] = len(report['pages']) == 71
    report['needs_editorial_review'] = bool(report['quarantined'] or report['warnings'] or report['duplicate_presentations'])
    if args.write_candidate:
        for name, value in (('candidate.json', snapshot), ('audit.json', report)):
            with (args.output_dir / name).open('x', encoding='utf-8') as handle:
                json.dump(value, handle, ensure_ascii=False, indent=2)
        print('Output directory:', args.output_dir)
    print(json.dumps(report['summary'], ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
