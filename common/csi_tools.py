# MCP tools shared by the CSI servers (SAP2000, ETABS), create() builds the FastMCP app for one product
# Shared by the SAP2000 and ETABS servers

import asyncio
import csv
import json
import os
import sys
import tempfile
import time
from typing import Any, Literal
from mcp.server.fastmcp import FastMCP
import csi_com
import csi_docs
from csi_com import CsiError, checked, invoke, run

ITEM_TYPES = {'Object': 0, 'Element': 1, 'Group': 2, 'Selection': 3}
CASE_STATUS = {1: 'not run', 2: 'could not start',
               3: 'not finished', 4: 'finished'}
COMMON_ALIASES = {'joint_displ': 'JointDispl', 'joint_react': 'JointReact',
                  'frame_force': 'FrameForce', 'base_react': 'BaseReact',
                  'modal_periods': 'ModalPeriod', 'modal_participating_mass': 'ModalParticipatingMassRatios',
                  'area_force_shell': 'AreaForceShell', 'joint_accel': 'JointAcc'}

def _pick(outputs, *needles):

    # find an output by part of its name, the typelib names differ slightly from the help

    for k, v in outputs.items():

        if all(n.lower() in k.lower() for n in needles):
            return v

    return None

def _count_key(outputs):

    return next((k for k, v in outputs.items() if k.lower().startswith('number') and isinstance(v, int)), None)

def _ok(ret):

    return not (isinstance(ret, int) and not isinstance(ret, bool) and ret != 0)

def create(product, design, aliases, extensions):

    # design maps a design kind to its SapModel object, its start method and the words of its result tables
    # aliases are extra friendly names for Results functions

    out_dir = os.environ.get('CSI_MCP_OUT', os.path.join(tempfile.gettempdir(), product.lower() + '-mcp'))
    result_aliases = {**COMMON_ALIASES, **aliases}
    mcp = FastMCP(f'csi-{product.lower()}')

    def limit_rows(rows, max_rows, csv_path, stem):

        if len(rows) <= max_rows and not csv_path:
            return {'count': len(rows), 'rows': rows}

        path = csv_path or os.path.join(out_dir, f'{stem}_{time.strftime("%Y%m%d_%H%M%S")}.csv')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fields = list(rows[0].keys()) if rows else []

        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

        shown = min(max_rows, 50)

        return {'count': len(rows), 'csv_path': path, 'rows': rows[:shown], 'truncated': len(rows) > shown}

    @mcp.tool(description=f'Connect to {product}. mode "attach" uses the running instance (or the one with process id pid), '
                          f'mode "start" launches a new instance (optionally a specific {product}.exe in program_path). Returns the status.')
    async def connect(mode: Literal['attach', 'start'] = 'attach',
                      pid: int | None = None,
                      program_path: str | None = None,
                      visible: bool = True,
                      units: str = 'kN_m_C') -> dict:

        return await run(csi_com.connect, mode, pid, program_path, visible, units)

    @mcp.tool(description=f'Release the connection. close_app=True also closes {product} without saving, '
                          'allowed only for an instance started by this server.')
    async def disconnect(close_app: bool = False) -> dict:

        return await run(csi_com.disconnect, close_app)

    @mcp.tool(description='Connection state, OAPI and program version, model file, present and database units, lock state.')
    async def status() -> dict:

        return await run(csi_com.status)

    @mcp.tool(description=f'Open an existing model file ({extensions}). Changes the model in {product}.')
    async def open_model(path: str) -> dict:

        await run(checked, 'File.OpenFile', {'FileName': path})

        return await run(csi_com.status)

    @mcp.tool(description='Start a new blank model in the given units (e.g. kN_m_C, kN_mm_C, kip_in_F). '
                          'Discards the unsaved current model.')
    async def new_blank_model(units: str = 'kN_m_C') -> dict:

        def work():

            checked('InitializeNewModel', {'Units': csi_com.UNITS[units]})
            checked('File.NewBlank')

            return csi_com.status()

        return await run(work)

    @mcp.tool(description=f'Save the model to the given full path ({csi_com.cfg()["ext"]}). The path is mandatory.')
    async def save_model(path: str) -> dict:

        await run(checked, 'File.Save', {'FileName': path})

        return {'saved': path}

    @mcp.tool(description='Set the present units: lb_in_F, lb_ft_F, kip_in_F, kip_ft_F, kN_mm_C, kN_m_C, kgf_mm_C, kgf_m_C, '
                          'N_mm_C, N_m_C, Ton_mm_C, Ton_m_C, kN_cm_C, kgf_cm_C, N_cm_C, Ton_cm_C.')
    async def set_units(units: str) -> dict:

        if units not in csi_com.UNITS:
            raise CsiError(f'Unknown units {units}, use one of {list(csi_com.UNITS)}')

        await run(checked, 'SetPresentUnits', {'Units': csi_com.UNITS[units]})

        return {'present_units': units}

    @mcp.tool(description='Run the analysis. With cases, only those load cases are run, otherwise the current run flags are used. '
                          'The model must have been saved to a file first. Returns the status of every case.')
    async def run_analysis(cases: list[str] | None = None) -> dict:

        def work():

            if cases:
                checked('Analyze.SetRunCaseFlag', {'Name': '', 'Run': False, 'All': True})

                for c in cases:
                    checked('Analyze.SetRunCaseFlag', {'Name': c, 'Run': True})

            t0 = time.time()
            checked('Analyze.RunAnalysis')
            elapsed = round(time.time() - t0, 1)
            out = invoke('Analyze.GetCaseStatus')['outputs']
            names = _pick(out, 'name') or []
            codes = _pick(out, 'status') or []

            return {'elapsed_s': elapsed,
                    'cases': {n: CASE_STATUS.get(s, s) for n, s in zip(names, codes)}}

        return await run(work)

    @mcp.tool(description=f'Run a design check ({", ".join(design)}) with the code and preferences already set in the model. '
                          'Needs analysis results. Returns the available table keys with design results.')
    async def run_design(kind: str) -> dict:

        def work():

            if kind not in design:
                raise CsiError(f'Unknown design kind {kind}, use one of {list(design)}')

            obj, start, word = design[kind]
            checked(f'{obj}.{start}')
            out = invoke('DatabaseTables.GetAvailableTables')['outputs']
            keys = _pick(out, 'key') or []

            return {'design': kind, 'result_tables': [k for k in keys if word.lower() in k.lower()]}

        return await run(work)

    @mcp.tool(description='List the database tables. available_only=True lists only tables with data in the current model. '
                          'contains filters the table keys (case insensitive).')
    async def list_tables(available_only: bool = True, contains: str | None = None) -> dict:

        def work():

            fn = 'DatabaseTables.GetAvailableTables' if available_only else 'DatabaseTables.GetAllTables'
            out = invoke(fn)['outputs']
            rows = csi_com.rows_from_columns(out, _count_key(out))

            if contains:
                rows = [r for r in rows if contains.lower() in str(_pick(r, 'key')).lower()]

            return {'count': len(rows), 'tables': rows}

        return await run(work)

    @mcp.tool(description='Fields (columns) of a database table, with units and whether each is importable (editable).')
    async def table_fields(table_key: str) -> dict:

        def work():

            out = invoke('DatabaseTables.GetAllFieldsInTable', {'TableKey': table_key})['outputs']

            return {'table': table_key, 'fields': csi_com.rows_from_columns(out, _count_key(out))}

        return await run(work)

    @mcp.tool(description='Read a database table as rows. fields limits the columns, group limits the objects (All by default), '
                          'load_cases and combos select the results shown in result tables. '
                          'Above max_rows (or when csv_path is given) the full table is written to a CSV and only the first rows are returned.')
    async def get_table(table_key: str,
                        fields: list[str] | None = None,
                        group: str = 'All',
                        load_cases: list[str] | None = None,
                        combos: list[str] | None = None,
                        max_rows: int = 500,
                        csv_path: str | None = None) -> dict:

        def work():

            if load_cases is not None:
                checked('DatabaseTables.SetLoadCasesSelectedForDisplay', [load_cases])

            if combos is not None:
                checked('DatabaseTables.SetLoadCombinationsSelectedForDisplay', [combos])

            out = checked('DatabaseTables.GetTableForDisplayArray',
                          {'TableKey': table_key, 'FieldKeyList': fields or [''], 'GroupName': group})['outputs']
            cols = _pick(out, 'included') or []
            rows = csi_com.rows_from_flat(cols, _pick(out, 'tabledata') or [], _pick(out, 'number') or 0)
            stem = ''.join(ch if ch.isalnum() else '_' for ch in table_key)[:60]

            return {'table': table_key, **limit_rows(rows, max_rows, csv_path, stem)}

        return await run(work)

    @mcp.tool(description='Edit an importable database table and apply it to the model (changes the model). '
                          'rows is a list of {field: value}. mode "merge" updates rows that match on key_fields '
                          '(default: the first field) and appends the others; mode "replace" makes rows the whole table. '
                          'apply=False only stages the table. Returns the import counts and log. Unlock the model first if it is locked.')
    async def edit_table(table_key: str,
                         rows: list[dict[str, Any]],
                         mode: Literal['merge', 'replace'] = 'merge',
                         key_fields: list[str] | None = None,
                         apply: bool = True) -> dict:

        def work():

            out = checked('DatabaseTables.GetTableForEditingArray', {'TableKey': table_key, 'GroupName': 'All'})['outputs']
            version = _pick(out, 'version')
            fields = list(_pick(out, 'included') or [])
            current = csi_com.rows_from_flat(fields, _pick(out, 'tabledata') or [], _pick(out, 'number') or 0)
            unknown = sorted({k for r in rows for k in r} - set(fields))

            if unknown:
                raise CsiError(f'Unknown fields {unknown} for {table_key}, fields are {fields}')

            if mode == 'replace':
                merged = [{f: str(r.get(f, '')) for f in fields} for r in rows]

            else:
                keys = key_fields or fields[:1]
                merged = [dict(r) for r in current]
                where = {tuple(r.get(k, '') for k in keys): r for r in merged}

                for r in rows:
                    hit = where.get(tuple(str(r.get(k, '')) for k in keys))

                    if hit is not None:
                        hit.update({k: str(v) for k, v in r.items()})

                    else:
                        merged.append({f: str(r.get(f, '')) for f in fields})

            flat = [str(r.get(f, '')) for r in merged for f in fields]

            try:
                checked('DatabaseTables.SetTableForEditingArray', [table_key, version, fields, len(merged), flat])

            except Exception:
                invoke('DatabaseTables.CancelTableEditing')
                raise

            if not apply:
                return {'staged': table_key, 'records': len(merged)}

            log = invoke('DatabaseTables.ApplyEditedTables', {'FillImportLog': True})

            return {'table': table_key, 'records': len(merged), 'ret': log['ret'], **log['outputs']}

        return await run(work)

    @mcp.tool(description='Analysis results through the Results API, one row per result. function is any Results function '
                          f'or an alias ({", ".join(result_aliases)}). '
                          'name and item_type (Object, Element, Group, Selection) select the objects where the function needs them.')
    async def get_results(function: str,
                          name: str = 'All',
                          item_type: Literal['Object', 'Element', 'Group', 'Selection'] = 'Group',
                          cases: list[str] | None = None,
                          combos: list[str] | None = None,
                          max_rows: int = 500,
                          csv_path: str | None = None) -> dict:

        def work():

            fn = result_aliases.get(function, function)
            checked('Results.Setup.DeselectAllCasesAndCombosForOutput')

            for c in cases or []:
                checked('Results.Setup.SetCaseSelectedForOutput', {'Name': c})

            for c in combos or []:
                checked('Results.Setup.SetComboSelectedForOutput', {'Name': c})

            params = {p['name'].lower() for p in csi_com.describe(csi_com.find_method(f'Results.{fn}')[1])}
            args = {}

            if 'name' in params:
                args['Name'] = name

            if 'itemtypeelm' in params:
                args['ItemTypeElm'] = ITEM_TYPES[item_type]

            out = checked(f'Results.{fn}', args)['outputs']
            rows = csi_com.rows_from_columns(out, _count_key(out))

            return {'function': fn, **limit_rows(rows, max_rows, csv_path, fn)}

        return await run(work)

    @mcp.tool(description='Call any SapModel API function by dotted path, e.g. "FrameObj.AddByCoord", "PropMaterial.SetMPIsotropic", '
                          '"LoadPatterns.AutoSeismic.SetEurocode82004". args is a dict by parameter name (output parameters may be omitted, '
                          'optional ones take their defaults) or a full positional list. Returns ret (0 = success) and the named outputs. '
                          'Read api_doc first for the parameters. Can change the model.')
    async def call_api(path: str, args: dict[str, Any] | list[Any] | None = None) -> dict:

        result = await run(invoke, path, args)
        result['ok'] = _ok(result['ret'])

        return result

    @mcp.tool(description=f'Search the {product} API documentation for functions, by words in their path, parameters and remarks.')
    async def search_api(query: str, limit: int = 20) -> dict:

        class_map = await run(csi_com.class_paths)
        hits = await asyncio.to_thread(csi_docs.search, query, limit, class_map)

        return {'query': query, 'count': len(hits), 'results': hits}

    @mcp.tool(description='Documentation of one API function (dotted path like "FrameObj.AddByCoord"): signature, parameter '
                          'descriptions, remarks, example, plus the parameter list with directions and defaults from the type library.')
    async def api_doc(path: str, include_example: bool = False) -> dict:

        try:
            canon, spec, iface = await run(csi_com.find_method, path)
            typelib = csi_com.describe(spec)
            path = '.'.join(canon)

        except Exception as e:
            iface, typelib = None, f'not resolved: {e}'

        entry = await asyncio.to_thread(csi_docs.lookup, path, iface)
        doc = dict(entry) if entry else {'note': 'No help topic found'}
        doc['path'] = path
        doc['typelib_parameters'] = typelib

        if not include_example:
            doc.pop('example', None)

        return doc

    return mcp

def selftest(paths):

    # checks the type library and the docs index without starting the program

    def com_part():

        info = {'product': csi_com.STATE['product'],
                'oapi_version': csi_com.helper().GetOAPIVersionNumber(),
                'interfaces reachable': len(csi_com.class_paths())}

        for p in paths:
            info[p] = [(d['name'], d['direction']) for d in csi_com.describe(csi_com.find_method(p)[1])]

        return info

    print(json.dumps(csi_com.COM_THREAD.submit(com_part).result(), indent=1))
    t0 = time.time()
    idx = csi_docs.index()
    print(f'docs index : {len(idx)} functions in {time.time() - t0:.1f} s')
    entry = csi_docs.lookup('FrameObj.AddByCoord', 'cFrameObj')
    print(json.dumps({k: entry[k] for k in ('path', 'signature', 'parameters')}, indent=1)[:900])
    class_map = csi_com.COM_THREAD.submit(csi_com.class_paths).result()
    print(json.dumps(csi_docs.search('eurocode 8 seismic', 5, class_map), indent=1)[:1200])
