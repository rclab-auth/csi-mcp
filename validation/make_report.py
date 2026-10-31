# Writes validation/RESULTS.md from the JSON results of sap2000_examples.py and etabs_examples.py
# Usage : python validation\make_report.py

import json
import os

print('\nCSI MCP validation report')
print('V.K. Papanikolaou, Assoc. Prof. AUTh')
print('Last updated : 31/10/2026\n')

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = [('SAP2000 26.2.0', 'results_sap2000.json'),
           ('ETABS 23.2.0', 'results_etabs.json')]


def fmt(v):

    return f'{v:.6g}'


lines = ['# Validation results', '',
         'Each CSI verification example was rebuilt from scratch through the MCP tools (no CSI model file was opened), '
         'analyzed, and its results were compared with the values published in the CSI verification manuals '
         '(`Manuals\\Verification` of each installation). See [examples](../examples) for the prompts.', '']
total = passed = 0

for program, name in SOURCES:
    rows = json.load(open(os.path.join(HERE, name), encoding='utf-8'))
    lines += [f'## {program}', '', '| Example | Quantity | MCP | Published | Difference | |', '|---|---|---:|---:|---:|---|']

    for r in rows:
        diff = f'{100 * r["diff"]:+.2f} %' if r['published'] != 0 else f'abs {r["diff"]:.3g}'
        lines.append(f'| {r["example"]} | {r["quantity"]} | {fmt(r["mcp"])} | {fmt(r["published"])} | {diff} | {"✅" if r["ok"] else "❌"} |')
        total += 1
        passed += r['ok']

    lines.append('')

lines.insert(4, f'**{passed} of {total} comparisons pass.**')
lines.insert(5, '')

with open(os.path.join(HERE, 'RESULTS.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f'{passed} of {total} comparisons pass, written RESULTS.md')
