# COM layer of the CSI MCP servers (SAP2000, ETABS) : one STA thread owns every program object
# Shared by the SAP2000 and ETABS servers, setup(product) selects the program

import asyncio
import concurrent.futures
import contextlib
import glob
import importlib
import os
import re
import sys
import comtypes
import comtypes.client
import comtypes.typeinfo

CSI = r'C:\Program Files\Computers and Structures'

# 'folder' is the install folder name without the version, the newest installed version is used unless 'env' is set

PRODUCTS = {'SAP2000': {'prog_id': 'CSI.SAP2000.API.SapObject',
                        'helper': 'SAP2000v1.Helper',
                        'tlb': 'SAP2000v1',
                        'folder': 'SAP2000',
                        'env': 'SAP2000_DIR',
                        'chm': 'CSI_OAPI_Documentation.chm',
                        'ext': '.sdb'},
            'ETABS': {'prog_id': 'CSI.ETABS.API.ETABSObject',
                      'helper': 'ETABSv1.Helper',
                      'tlb': 'ETABSv1',
                      'folder': 'ETABS',
                      'env': 'ETABS_DIR',
                      'chm': 'CSI API ETABS v1.chm',
                      'ext': '.edb'}}

UNITS = {'lb_in_F': 1, 'lb_ft_F': 2,
         'kip_in_F': 3, 'kip_ft_F': 4,
         'kN_mm_C': 5, 'kN_m_C': 6,
         'kgf_mm_C': 7, 'kgf_m_C': 8,
         'N_mm_C': 9, 'N_m_C': 10,
         'Ton_mm_C': 11, 'Ton_m_C': 12,
         'kN_cm_C': 13, 'kgf_cm_C': 14,
         'N_cm_C': 15, 'Ton_cm_C': 16}

UNITS_BY_CODE = {v: k for k, v in UNITS.items()}

# paramflags of the type library : 1 in, 2 out, 16 optional, 8 retval

PARAM_IN = 1
PARAM_OUT = 2
PARAM_RETVAL = 8

class CsiError(Exception):
    pass

def _init_thread():

    comtypes.CoInitialize()

COM_THREAD = concurrent.futures.ThreadPoolExecutor(max_workers=1,
                                                   initializer=_init_thread,
                                                   thread_name_prefix='csi-com')

STATE = {'product': None, 'cfg': None,
         'helper': None, 'tlb': None,
         'program': None, 'model': None,
         'started': False, 'pid': None,
         'class_paths': None}

def _install_dir(c):

    # e.g. 'ETABS 22' and 'ETABS 23' installed side by side : take the highest version number

    # a folder chosen in the Claude install screen arrives as an environment variable, an empty or unresolved one is ignored

    forced = os.environ.get(c['env'], '').strip()

    if forced and os.path.isdir(forced):
        return forced

    found = []

    for d in glob.glob(os.path.join(CSI, c['folder'] + ' *')):
        m = re.search(r' (\d+)$', d)

        if m and os.path.isdir(d):
            found.append((int(m.group(1)), d))

    if not found:
        raise CsiError(f'No {c["folder"]} installation found in {CSI}, set {c["env"]}')

    return max(found)[1]

def setup(product):

    STATE['product'] = product
    STATE['cfg'] = dict(PRODUCTS[product])
    STATE['cfg']['dir'] = _install_dir(STATE['cfg'])

def _fresh_wrapper(module):

    # comtypes keeps the wrapper it generated the first time, keyed by the type library GUID and version
    # CSI keeps GUID and version 1.0 across program versions, so after an upgrade the wrapper is regenerated here

    guid, major, minor = module.Library._reg_typelib_
    registered = comtypes.typeinfo.QueryPathOfRegTypeLib(comtypes.GUID(guid), major, minor).rstrip('\x00')
    current = getattr(module, 'typelib_path', '')

    if os.path.normcase(os.path.abspath(registered)) == os.path.normcase(os.path.abspath(current)):
        return module

    gen_dir = os.path.dirname(module.__file__)
    wrapper = '_' + guid.strip('{}').replace('-', '_') + f'_0_{major}_{minor}'

    for name in (cfg()['tlb'], wrapper):
        sys.modules.pop('comtypes.gen.' + name, None)

        for path in glob.glob(os.path.join(gen_dir, name + '.py')) + glob.glob(os.path.join(gen_dir, '__pycache__', name + '.*')):
            os.remove(path)

    comtypes.client.GetModule(registered)

    return importlib.import_module('comtypes.gen.' + cfg()['tlb'])

def cfg():

    return STATE['cfg']

async def run(fn, *args, **kwargs):

    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(COM_THREAD, lambda: fn(*args, **kwargs))

def helper():

    if STATE['helper'] is None:

        # comtypes prints '# Generating ...' on first use, keep stdout clean for the protocol

        with contextlib.redirect_stdout(sys.stderr):
            obj = comtypes.client.CreateObject(cfg()['helper'])
            module = _fresh_wrapper(importlib.import_module('comtypes.gen.' + cfg()['tlb']))

        STATE['tlb'] = module
        STATE['helper'] = obj.QueryInterface(module.cHelper)

    return STATE['helper']

def tlb():

    helper()

    return STATE['tlb']

def model():

    if STATE['model'] is None:
        raise CsiError(f'Not connected to {STATE["product"]} : call connect first')

    return STATE['model']

def _plain(value):

    # COM arrays come back as tuples, turn them into JSON friendly lists

    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]

    if isinstance(value, (int, float, str, bool)) or value is None:
        return value

    return str(value)

def _iface_of(restype_ptr):

    # a property getter returns LP_POINTER(cX), unwrap it to the next interface cX

    m = re.search(r'POINTER\((\w+)\)', getattr(restype_ptr, '__name__', ''))

    return getattr(tlb(), m.group(1), None) if m else None

def find_method(path):

    # walk a dotted path such as 'LoadPatterns.AutoSeismic.SetEurocode8' from cSapModel
    # returns the canonical path parts, the method spec and the interface name that owns it

    parts = [p for p in path.split('.') if p]

    if parts and parts[0] in ('SapObject', 'EtabsObject', 'ETABSObject'):
        parts = parts[1:]

    if parts and parts[0] == 'SapModel':
        parts = parts[1:]

    if not parts:
        raise CsiError('Empty API path')

    iface = tlb().cSapModel
    canon = []

    for i, part in enumerate(parts):
        wanted = (part.lower(), '_get_' + part.lower())
        spec = next((m for m in iface._methods_ if m.name.lower() in wanted), None)

        if spec is None:
            raise CsiError(f'{iface.__name__} has no member {part}')

        canon.append(spec.name.removeprefix('_get_'))

        if i == len(parts) - 1:
            return canon, spec, iface.__name__

        nxt = _iface_of(spec.argtypes[-1]) if spec.argtypes else None

        if nxt is None or not hasattr(nxt, '_methods_'):
            raise CsiError(f'{part} is not an object, cannot go deeper')

        iface = nxt

    raise CsiError('Unreachable')

def class_paths():

    # map every interface reachable from cSapModel to its dotted path, e.g. cAutoSeismic -> LoadPatterns.AutoSeismic

    if STATE['class_paths'] is None:
        found = {'cSapModel': ''}
        queue = [(tlb().cSapModel, '')]

        while queue:
            iface, prefix = queue.pop(0)

            for m in iface._methods_:

                if not m.name.startswith('_get_') or not m.argtypes:
                    continue

                nxt = _iface_of(m.argtypes[-1])

                if nxt is None or nxt.__name__ in found or not hasattr(nxt, '_methods_'):
                    continue

                path = (prefix + '.' if prefix else '') + m.name.removeprefix('_get_')
                found[nxt.__name__] = path
                queue.append((nxt, path))

        STATE['class_paths'] = found

    return STATE['class_paths']

def _placeholder(argtype):

    name = getattr(argtype, '__name__', str(argtype))

    if 'SAFEARRAY' in name:
        return []

    if 'BSTR' in name:
        return ''

    if 'VARIANT_BOOL' in name:
        return False

    if 'double' in name:
        return 0.0

    return 0

def describe(spec):

    # list of (name, direction, optional default) for every non retval parameter

    params = []

    for argtype, pf in zip(spec.argtypes, spec.paramflags):
        flags, name = pf[0], pf[1]

        if flags & PARAM_RETVAL:
            continue

        direction = 'in/out' if flags & PARAM_OUT else 'in'
        entry = {'name': name, 'direction': direction,
                 'type': getattr(argtype, '__name__', str(argtype)).replace('LP_', '')}

        if len(pf) > 2:
            entry['default'] = _plain(pf[2])

        params.append(entry)

    return params

def invoke(path, args=None):

    # call any SapModel function, args is a dict by parameter name or a positional list

    parts, spec, _ = find_method(path)

    if parts[-1] == 'ApplicationExit':
        raise CsiError('ApplicationExit is refused, use disconnect instead')

    obj = model()

    for part in parts[:-1]:
        obj = getattr(obj, part)

    params = [(t, pf) for t, pf in zip(spec.argtypes, spec.paramflags) if not pf[0] & PARAM_RETVAL]

    if isinstance(args, list):
        values = list(args)

    else:
        given = {k.lower(): v for k, v in (args or {}).items()}
        known = {pf[1].lower() for _, pf in params}
        unknown = [k for k in given if k not in known]

        if unknown:
            raise CsiError(f'{path} has no parameter(s) {unknown}, expected {[pf[1] for _, pf in params]}')

        values = []

        for argtype, pf in params:
            key = pf[1].lower()

            if key in given:
                values.append(given[key])

            elif pf[0] & PARAM_OUT:
                values.append(_placeholder(argtype))

            elif len(pf) > 2:
                values.append(pf[2])

            else:
                raise CsiError(f'{path} needs parameter {pf[1]}')

    raw = getattr(obj, parts[-1])(*values)
    out_names = [pf[1] for _, pf in params if pf[0] & PARAM_OUT]
    has_retval = any(pf[0] & PARAM_RETVAL for pf in spec.paramflags)

    if out_names:
        raw = list(raw) if isinstance(raw, (list, tuple)) else [raw]
        outputs = dict(zip(out_names, [_plain(v) for v in raw[:len(out_names)]]))
        ret = _plain(raw[len(out_names)]) if len(raw) > len(out_names) else None

    else:
        outputs = {}
        ret = _plain(raw) if has_retval else None

    return {'function': '.'.join(parts), 'ret': ret, 'outputs': outputs}

def checked(path, args=None):

    # like invoke, but a nonzero integer return value raises

    result = invoke(path, args)
    ret = result['ret']

    if isinstance(ret, int) and not isinstance(ret, bool) and ret != 0:
        raise CsiError(f'{result["function"]} returned {ret} (nonzero means failure)')

    return result

def connect(mode, pid=None, program_path=None, visible=True, units='kN_m_C'):

    h = helper()
    prog_id = cfg()['prog_id']

    if STATE['model'] is not None:
        disconnect(False)

    if mode == 'attach':
        obj = h.GetObjectProcess(prog_id, pid) if pid else h.GetObject(prog_id)

        if not obj:
            raise CsiError(f'No running {STATE["product"]} instance found to attach to')

        started = False

    elif mode == 'start':
        obj = h.CreateObject(program_path) if program_path else h.CreateObjectProgID(prog_id)
        spec = next(m for m in tlb().cOAPI._methods_ if m.name == 'ApplicationStart')

        # SAP2000 takes units, visibility and a file name at start, ETABS takes nothing

        if any(pf[1] == 'Units' for pf in spec.paramflags):
            ret = obj.ApplicationStart(UNITS[units], visible, '')

        else:
            ret = obj.ApplicationStart()

            if not visible and hasattr(obj, 'Hide'):
                obj.Hide()

        if ret != 0:
            raise CsiError(f'ApplicationStart returned {ret} (license or startup problem ?)')

        started = True

    else:
        raise CsiError('mode must be attach or start')

    STATE.update(program=obj, model=obj.SapModel, started=started, pid=pid)

    return status()

def disconnect(close_app=False):

    obj = STATE['program']
    closed = False

    if obj is not None and close_app:

        if not STATE['started']:
            raise CsiError('This instance was attached, not started here : close it from the GUI')

        obj.ApplicationExit(False)
        closed = True

    STATE.update(program=None, model=None, started=False, pid=None)

    return {'disconnected': True, 'application_closed': closed}

def status():

    h = helper()
    info = {'product': STATE['product'],
            'connected': STATE['model'] is not None,
            'oapi_version': h.GetOAPIVersionNumber()}

    if not info['connected']:
        return info

    m = STATE['model']
    version = invoke('GetVersion')['outputs']
    info.update(started_here=STATE['started'],
                program_version=version.get('Version'),
                model_file=invoke('GetModelFilename')['ret'],
                present_units=UNITS_BY_CODE.get(m.GetPresentUnits()),
                database_units=UNITS_BY_CODE.get(m.GetDatabaseUnits()),
                model_locked=bool(m.GetModelIsLocked()))

    return info

def rows_from_flat(fields, data, count):

    width = len(fields)

    return [dict(zip(fields, data[i * width:(i + 1) * width])) for i in range(count)]

def rows_from_columns(outputs, count_key):

    # result functions return parallel arrays, zip the ones that have one value per result

    n = outputs.get(count_key) or 0
    cols = {k: v for k, v in outputs.items() if isinstance(v, list) and len(v) == n}

    return [{k: cols[k][i] for k in cols} for i in range(n)]
