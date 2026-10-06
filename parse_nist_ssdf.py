#!/usr/bin/env python3
"""Extract SSDF Table 1 from NIST SP 800-218 into JSON, CSV, and TXT.
Requires: pip install pymupdf
Usage: python parse_nist_ssdf.py 'NIST.SP.800-218(2).pdf'
"""
import argparse
import csv
import json
import re
from pathlib import Path
import fitz

TASK = re.compile(r'^(PO|PS|PW|RV)\.\d+\.\d+:')
PRACTICE = re.compile(r'\(((?:PO|PS|PW|RV)\.\d+)\):')
REF = re.compile(r'^([A-Z][A-Z0-9]+):\s*(.*)$')
COLUMNS = ('practice', 'task', 'examples', 'references')
FIELDS = ('practice_id', 'practice_name', 'task_id', 'task_description', 'notional_implementation_examples', 'references')


def clean(s):
    s = re.sub(r'\s+', ' ', s).strip()
    return re.sub(r'(?<=\w)- (?=\w)', '', s)


def lines_by_column(page):
    # Fixed column boundaries in the landscape SSDF Table 1.
    buckets = {key: [] for key in COLUMNS}
    for line in page.get_text('dict')['blocks']:
        if 'lines' not in line:
            continue
        for ln in line['lines']:
            spans = ln['spans']
            if not spans:
                continue
            x = min(s['bbox'][0] for s in spans)
            y = min(s['bbox'][1] for s in spans)
            if y < 106 or y > 715 or x < 35:
                continue
            value = clean(''.join(s['text'] for s in spans))
            if not value:
                continue
            key = 'practice' if x < 245 else 'task' if x < 460 else 'examples' if x < 805 else 'references'
            buckets[key].append((y, x, value))
    for key in buckets:
        buckets[key].sort()
    return buckets


def extract(pdf):
    document = fitz.open(pdf)
    rows = []
    practice_names = {}
    current_practice = None
    current_row = None
    for page in document:
        if not page.rect.width > page.rect.height:
            continue
        cols = lines_by_column(page)
        # Identify task row boundaries using the task column's vertical positions.
        starts = [(y, clean(text)) for y, x, text in cols['task'] if TASK.match(text)]
        if not starts:
            continue
        practice_text = cols['practice']
        for index, (start_y, first_line) in enumerate(starts):
            end_y = starts[index + 1][0] if index + 1 < len(starts) else 716
            # A new practice heading can occur partway down the left column.
            for j, (y, x, val) in enumerate(practice_text):
                if y > start_y + 14:
                    break
                m = PRACTICE.search(val)
                if not m:
                    continue
                pid = m.group(1)
                # Practice name may wrap across preceding lines.
                preceding = [v for yy, xx, v in practice_text[max(0,j-5):j] if y-yy < 55]
                name = clean(' '.join(preceding + [val.split('('+pid+'):',1)[0]]))
                # Trim off previous practice descriptions and group headings.
                name = re.split(r'(?<=\.)\s+(?=[A-Z])', name)[-1]
                practice_names[pid] = name
                current_practice = pid
            task_id = first_line.split(':', 1)[0]
            pid = '.'.join(task_id.split('.')[:2])
            current_practice = pid
            task_lines = [v for y,x,v in cols['task'] if start_y-1 <= y < end_y-1]
            description = clean(' '.join(task_lines))
            description = description.split(':',1)[1].strip() if ':' in description else description
            ex_lines = [v for y,x,v in cols['examples'] if start_y-5 <= y < end_y-3]
            examples = []
            for val in ex_lines:
                match = re.match(r'^Example\s+\d+:\s*(.*)', val)
                if match:
                    examples.append(match.group(1))
                elif examples:
                    examples[-1] += ' ' + val
            examples = [clean(e) for e in examples]
            ref_lines = [v for y,x,v in cols['references'] if start_y-5 <= y < end_y-3]
            references = {}
            for val in ref_lines:
                m = REF.match(val)
                if m:
                    references[m.group(1)] = m.group(2)
                elif references:
                    last = next(reversed(references))
                    references[last] += ' ' + val
            references = {k: clean(v) for k,v in references.items()}
            rows.append(dict(practice_id=pid, practice_name='', task_id=task_id,
                             task_description=description, notional_implementation_examples=examples,
                             references=references))
    # Resolve practice names from the complete left-column text across table pages.
    for page in document:
        if page.rect.width <= page.rect.height:
            continue
        left = lines_by_column(page)['practice']
        for i, (y,x,val) in enumerate(left):
            m = PRACTICE.search(val)
            if m:
                pid = m.group(1)
                parts = [val.split('('+pid+'):',1)[0]]
                k = i-1
                while k >= 0 and y-left[k][0] < 48 and len(parts) < 5:
                    prior = left[k][2]
                    if PRACTICE.search(prior) or prior.endswith('.') or prior.startswith(('Prepare the','Protect the','Produce Well','Respond to')):
                        break
                    parts.insert(0, prior)
                    k -= 1
                practice_names[pid] = clean(' '.join(parts))
    for row in rows:
        row['practice_name'] = practice_names.get(row['practice_id'], '')
    return rows


def write_outputs(rows, output):
    output.mkdir(parents=True, exist_ok=True)
    stem = 'nist_ssdf_v1.1'
    (output / (stem+'.json')).write_text(json.dumps(rows, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    with (output / (stem+'.csv')).open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row,
                'notional_implementation_examples': json.dumps(row['notional_implementation_examples'], ensure_ascii=False),
                'references': json.dumps(row['references'], ensure_ascii=False)})
    with (output / (stem+'.txt')).open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(f"Practice: {row['practice_id']} - {row['practice_name']}\n")
            f.write(f"Task: {row['task_id']} - {row['task_description']}\n")
            f.write('Notional Implementation Examples:\n')
            for example in row['notional_implementation_examples']:
                f.write(f'  - {example}\n')
            f.write('References:\n')
            for key, value in row['references'].items():
                f.write(f'  {key}: {value}\n')
            f.write('\n')



def print_summary(rows, output):
    """Print a concise extraction summary to the terminal."""
    from collections import Counter, defaultdict

    practice_ids = {row["practice_id"] for row in rows}
    group_counts = Counter(row["practice_id"].split(".")[0] for row in rows)
    practice_task_counts = Counter(row["practice_id"] for row in rows)

    total_examples = sum(len(row["notional_implementation_examples"]) for row in rows)
    total_reference_entries = sum(len(row["references"]) for row in rows)
    unique_reference_sources = {
        source
        for row in rows
        for source in row["references"].keys()
    }

    missing_names = sum(not row["practice_name"].strip() for row in rows)
    missing_descriptions = sum(not row["task_description"].strip() for row in rows)
    tasks_without_examples = sum(not row["notional_implementation_examples"] for row in rows)
    tasks_without_references = sum(not row["references"] for row in rows)

    group_names = {
        "PO": "Prepare the Organization",
        "PS": "Protect the Software",
        "PW": "Produce Well-Secured Software",
        "RV": "Respond to Vulnerabilities",
    }

    print()
    print("NIST SSDF PARSING SUMMARY")
    print(f"Total practices:                 {len(practice_ids)}")
    print(f"Total tasks:                     {len(rows)}")
    print(f"Implementation examples:         {total_examples}")
    print(f"Reference entries:               {total_reference_entries}")
    print(f"Unique reference sources:        {len(unique_reference_sources)}")

    print("\nTasks by SSDF group:")
    for group in ("PO", "PS", "PW", "RV"):
        print(f"  {group} - {group_names[group]:31} {group_counts[group]:>3} tasks")

    print("\nTasks by practice:")
    for practice_id in sorted(
        practice_task_counts,
        key=lambda p: ("POPSPWRV".find(p[:2]), int(p.split(".")[1]))
    ):
        name = next(
            (r["practice_name"] for r in rows
             if r["practice_id"] == practice_id and r["practice_name"]),
            ""
        )
        label = f"{practice_id} - {name}" if name else practice_id
        print(f"  {label}: {practice_task_counts[practice_id]}")

    print("\nGenerated files:")
    for suffix in (".json", ".csv", ".txt"):
        print(f"  {output.resolve() / ('nist_ssdf_v1.1' + suffix)}")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('.'))
    args = parser.parse_args()
    rows = extract(args.pdf)
    if not rows:
        raise RuntimeError('No SSDF tasks found; check that the PDF is NIST SP 800-218 v1.1.')
    write_outputs(rows, args.output_dir)
    print_summary(rows, args.output_dir)

if __name__ == '__main__':
    main()
