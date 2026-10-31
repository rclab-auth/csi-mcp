# Index of a CSI API help file (CHM) : decompiled once into a local cache, then parsed
# Two layouts exist : the classic SAP2000 OAPI pages (Syntax, VB6 Procedure) and the Sandcastle pages of ETABS
# Shared by the SAP2000 and ETABS servers

import html
import json
import os
import re
import shutil
import subprocess
import csi_com

_INDEX = None

def _paths():

    c = csi_com.cfg()
    cache = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), csi_com.STATE['product'].lower() + '-mcp')

    return {'chm': os.path.join(c['dir'], c['chm']),
            'cache': cache,
            'docs': os.path.join(cache, 'docs'),
            'index': os.path.join(cache, 'index.json')}

def _text(fragment):

    fragment = re.sub(r'(?is)<(script|style).*?</\1>', '', fragment)
    fragment = re.sub(r'(?i)<br\s*/?>|</p>|</tr>|</li>|</h\d>|</dd>', '\n', fragment)
    fragment = html.unescape(re.sub(r'<[^>]+>', '', fragment))
    fragment = fragment.replace(' ', ' ').replace('�', ' ')
    lines = [re.sub(r'[ \t]+', ' ', ln).strip() for ln in fragment.splitlines()]

    return '\n'.join(ln for ln in lines if ln)

def _decompile(p):

    # hh.exe fails on paths with spaces, so decompile a copy of the CHM

    os.makedirs(p['docs'], exist_ok=True)
    copy = os.path.join(p['cache'], 'oapi.chm')
    shutil.copyfile(p['chm'], copy)
    subprocess.run(['hh.exe', '-decompile', p['docs'], copy], check=False)

def _classic_section(page, title):

    m = re.search(r'(?is)<h2>\s*' + re.escape(title) + r'\s*</h2>(.*?)(?=<h2>|</body>)', page)

    return _text(m.group(1)) if m else ''

def _classic_parameters(page):

    m = re.search(r'(?is)<h2>\s*Parameters\s*</h2>(.*?)(?=<h2>|</body>)', page)

    if not m:
        return {}

    params = {}
    current = None

    for cls, body in re.findall(r'(?is)<p class="(\w+)"[^>]*>(.*?)</p>', m.group(1)):
        txt = _text(body)

        if cls == 'ParameterName':
            current = txt
            params[current] = ''

        elif current:
            params[current] = (params[current] + '\n' + txt).strip()

    return params

def _classic(page, topic):

    syntax = _classic_section(page, 'Syntax').split('\n')[0].strip()

    if not syntax:
        return None

    path = re.sub(r'^SapObject\.SapModel\.?', '', syntax)
    path = re.sub(r'^cDatabaseTables', 'DatabaseTables', path)

    return {'key': (path or syntax).lower(),
            'path': path or syntax,
            'topic': topic,
            'signature': _classic_section(page, 'VB6 Procedure'),
            'parameters': _classic_parameters(page),
            'remarks': _classic_section(page, 'Remarks'),
            'example': _classic_section(page, 'VBA Example')[:4000],
            'release_notes': _classic_section(page, 'Release Notes')}

def _sandcastle_region(page, title):

    m = re.search(r'(?is)>' + re.escape(title) + r'</span></div><div id="\w+" class="collapsibleSection">(.*?)(?=<div class="collapsibleAreaRegion"|<div id="pageFooter"|$)', page)

    return m.group(1) if m else ''

def _sandcastle(page, topic):

    t = re.search(r'(?is)<title>\s*(\w+)\.(\w+) Method\b', page)

    if not t:
        return None

    cls, method = t.group(1), t.group(2)
    desc = re.search(r'(?is)<meta name="Description" content="([^"]*)"', page)
    pre = re.search(r'(?is)<pre[^>]*>(.*?)</pre>', page)
    syntax = _sandcastle_region(page, 'Syntax')
    params = {}

    for name, body in re.findall(r'(?is)<dt><span class="parameter">(\w+)</span></dt><dd>(.*?)</dd>', syntax):
        params[name] = re.sub(r'^Type:[^\n]*\n?', '', _text(body)).strip()

    ret = re.search(r'(?is)Return Value</h4>(.*?)</div>', syntax)
    example = _sandcastle_region(page, 'Examples')
    ex_pre = re.search(r'(?is)<pre[^>]*>(.*?)</pre>', example)

    return {'key': f'{cls}.{method}'.lower(),
            'path': f'{cls}.{method}',
            'class': cls,
            'method': method,
            'topic': topic,
            'signature': _text(pre.group(1)) if pre else '',
            'parameters': params,
            'returns': _text(ret.group(1)) if ret else '',
            'remarks': '\n'.join(filter(None, [html.unescape(desc.group(1)).strip() if desc else '',
                                               _text(_sandcastle_region(page, 'Remarks'))])),
            'example': (_text(ex_pre.group(1)) if ex_pre else '')[:4000],
            'release_notes': ''}

def _build(p):

    # always decompile again, so that an upgraded program never reuses the pages of the old CHM

    shutil.rmtree(p['docs'], ignore_errors=True)
    _decompile(p)

    entries = {}

    for root, _, files in os.walk(p['docs']):

        for name in files:

            if not name.lower().endswith('.htm'):
                continue

            full = os.path.join(root, name)

            with open(full, encoding='utf-8', errors='replace') as f:
                page = f.read()

            topic = os.path.relpath(full, p['docs'])
            entry = _sandcastle(page, topic) if 'Microsoft.Help.Id' in page else _classic(page, topic)

            if entry:
                entries.setdefault(entry['key'], entry)

    data = {'chm': p['chm'], 'chm_mtime': os.path.getmtime(p['chm']), 'entries': entries}

    with open(p['index'], 'w', encoding='utf-8') as f:
        json.dump(data, f)

    return data

def index():

    global _INDEX

    if _INDEX is not None:
        return _INDEX

    p = _paths()
    data = None

    if not os.path.exists(p['chm']):
        raise FileNotFoundError(f'Help file not found : {p["chm"]}')

    if os.path.exists(p['index']):

        with open(p['index'], encoding='utf-8') as f:
            data = json.load(f)

        # a different CHM (program upgrade) or a newer one makes the index stale

        if data.get('chm') != p['chm'] or data.get('chm_mtime') != os.path.getmtime(p['chm']):
            data = None

    _INDEX = (data or _build(p))['entries']

    return _INDEX

def lookup(path, iface=None):

    # by dotted path (SAP2000 pages), by interface and method (ETABS pages), or by a unique method name

    entries = index()
    key = re.sub(r'^(SapObject\.)?(SapModel\.)?', '', path.strip(), flags=re.I).lower()
    tail = key.split('.')[-1]

    for k in (key, f'{iface}.{tail}'.lower() if iface else None):

        if k and k in entries:
            return entries[k]

    hits = [e for k, e in entries.items() if k.split('.')[-1] == tail]

    return hits[0] if len(hits) == 1 else None

def search(query, limit=20, class_map=None):

    # class_map turns ETABS interface names into dotted paths, e.g. cFrameObj.AddByCoord -> FrameObj.AddByCoord

    words = [w for w in re.split(r'\W+', query.lower()) if w]
    scored = []

    for key, e in index().items():
        body = (e['remarks'] + ' ' + ' '.join(e['parameters'])).lower()
        score = sum(5 * (w in key) + body.count(w) for w in words)

        if all(w in key or w in body for w in words) and score:
            scored.append((score, e))

    scored.sort(key=lambda s: -s[0])
    hits = []

    for _, e in scored[:limit]:
        path = e['path']

        if class_map and e.get('class') in class_map:
            prefix = class_map[e['class']]
            path = (prefix + '.' if prefix else '') + e['method']

        hits.append({'path': path,
                     'signature': e['signature'][:300],
                     'summary': e['remarks'][:300]})

    return hits
