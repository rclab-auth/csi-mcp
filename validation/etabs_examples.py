# Rebuilds CSI verification examples from scratch through the MCP tools and compares with the published results
# Usage : uv run --no-project --with "mcp<2" python validation\etabs_examples.py

import asyncio
import os
import sys
from verif_client import HERE, compare, save, server

print('\nETABS verification examples (1, 6, 8) through the MCP server')
print('V.K. Papanikolaou, Assoc. Prof. AUTh')
print('Last updated : 31/10/2026\n')

OUT = os.path.join(HERE, 'models')
ROWS = []
FIXED = [True] * 6
FREE = [False] * 6
ZERO = [0] * 6
G = 32.174


async def material(s, name, e, u):

    # weight and mass zero, so that only the masses given in each example exist

    await s.api('PropMaterial.SetMaterial', Name=name, MatType=2)
    await s.api('PropMaterial.SetMPIsotropic', Name=name, E=e, U=u, A=0)
    await s.api('PropMaterial.SetWeightAndMass', Name=name, MyOption=1, Value=0)


async def general(s, name, mat, area, i22, i33, j):

    # user section : shear areas 0 so that shear deformations are ignored

    await s.api('PropFrame.SetGeneral', Name=name, MatProp=mat, T3=1, T2=1, Area=area, As2=0, As3=0, Torsion=j,
                I22=i22, I33=i33, S22=1, S33=1, Z22=1, Z33=1, R22=1, R33=1)


async def frame(s, a, b, prop):

    return (await s.api('FrameObj.AddByCoord', XI=a[0], YI=a[1], ZI=a[2], XJ=b[0], YJ=b[1], ZJ=b[2], PropName=prop))['Name']


async def point_at(s, x, y, z):

    return (await s.api('PointObj.AddCartesian', X=x, Y=y, Z=z))['Name']


async def eigen_case(s, modes):

    await s.api('LoadCases.ModalEigen.SetCase', Name='EIGEN')
    await s.api('LoadCases.ModalEigen.SetNumberModes', Name='EIGEN', MaxModes=modes, MinModes=1)


async def example_1(s):

    # two-bay plane frame, outer beam ends pinned, axial and shear deformations neglected, beam B1 forces at five stations

    print('Example 1', flush=True)
    await s.tool('new_blank_model', units='kip_in_F')
    await s.api('Analyze.SetActiveDOF', DOF=[True, False, True, False, True, False])
    await material(s, 'CONC', 3000, 0.2)
    await s.api('PropFrame.SetRectangle', Name='COL', MatProp='CONC', T3=24, T2=12)
    await s.api('PropFrame.SetRectangle', Name='BEAM', MatProp='CONC', T3=30, T2=12)

    for p in ('COL', 'BEAM'):
        await s.api('PropFrame.SetModifiers', Name=p, Value=[1000, 0, 0, 1, 1, 1, 1, 1])

    xs = [0, 216, 432]
    tops = []

    for x in xs:
        c = await frame(s, (x, 0, 0), (x, 0, 120), 'COL')
        pts = await s.api('FrameObj.GetPoints', Name=c)
        await s.api('PointObj.SetRestraint', Name=pts['Point1'], Value=FIXED)
        tops.append(pts['Point2'])

    b1 = await frame(s, (0, 0, 120), (216, 0, 120), 'BEAM')
    b2 = await frame(s, (216, 0, 120), (432, 0, 120), 'BEAM')
    await s.api('FrameObj.SetReleases', Name=b1, II=[False] * 5 + [True], JJ=FREE, StartValue=ZERO, EndValue=ZERO)
    await s.api('FrameObj.SetReleases', Name=b2, II=FREE, JJ=[False] * 5 + [True], StartValue=ZERO, EndValue=ZERO)
    await s.api('FrameObj.SetOutputStations', Name=b1, MyType=1, MaxSegSize=54, MinSections=1)

    # no rigid joint offsets, as the example states : ETABS adds them automatically from the column and beam depths

    await s.api('FrameObj.SetEndLengthOffset', Name='ALL', AutoOffset=False, Length1=0, Length2=0, RZ=0, ItemType=1)

    # case 1 : 50, 100, 100, 100, 50 k at equal spaces (joints and beam midspans), case 2 : 10 k/ft on both beams

    await s.api('LoadPatterns.Add', Name='CASE1', MyType=8, SelfWTMultiplier=0, AddAnalysisCase=True)
    await s.api('LoadPatterns.Add', Name='CASE2', MyType=8, SelfWTMultiplier=0, AddAnalysisCase=True)

    for pt, p in zip(tops, (50, 100, 50)):
        await s.api('PointObj.SetLoadForce', Name=pt, LoadPat='CASE1', Value=[0, 0, -p, 0, 0, 0])

    for b in (b1, b2):
        await s.api('FrameObj.SetLoadPoint', Name=b, LoadPat='CASE1', MyType=1, Dir=6, Dist=0.5, Val=-100)
        await s.api('FrameObj.SetLoadDistributed', Name=b, LoadPat='CASE2', MyType=1, Dir=6, Dist1=0, Dist2=1, Val1=-10 / 12, Val2=-10 / 12)

    await s.tool('save_model', path=os.path.join(OUT, 'ETABS Example 01.edb'))
    await s.tool('run_analysis', cases=['CASE1', 'CASE2'])
    expected = {'CASE1': ([0, 1687.5, 3375, -337.5, -4050], [-31.25, -31.25, 68.75, 68.75, 68.75]),
                'CASE2': ([0, 2430, 2430, 0, -4860], [-67.5, -22.5, 22.5, 67.5, 112.5])}
    labels = ['End I', '1/4 point', '1/2 point', '3/4 point', 'End J']

    for case, (moments, shears) in expected.items():
        rows = (await s.tool('get_results', function='frame_force', name=b1, item_type='Object', cases=[case]))['rows']

        for k, (lab, m, v) in enumerate(zip(labels, moments, shears)):
            x = 216 * k / 4

            # at the point load there are two rows (left and right of it), the published shear is the one to the right

            at = [r for r in rows if abs(r['ObjSta'] - x) < 0.01]
            compare(ROWS, 'Example 1', f'{case} B1 M3 {lab} [k-in]', at[0]['M3'], m, 0.001 if m else 0.5)
            compare(ROWS, 'Example 1', f'{case} B1 V2 {lab} [k]', at[-1]['V2'], v, 0.001)


async def example_6(s):

    # nine-story, ten-bay plane frame in the YZ plane, one horizontal mass per floor through a rigid diaphragm

    print('Example 6', flush=True)

    # stories at the floor levels, so that the default mass source lumps the lateral masses at them

    await s.api('InitializeNewModel', Units=4)
    await s.api('File.NewGridOnly', NumberStorys=9, TypicalStoryHeight=10, BottomStoryHeight=10, NumberLinesX=2, NumberLinesY=11, SpacingX=20, SpacingY=20)
    await material(s, 'MAT', 432000, 0.2)
    await general(s, 'SEC', 'MAT', 3, 1, 1, 1)

    for f in range(1, 10):
        await s.api('Diaphragm.SetDiaphragm', Name=f'RD{f}', SemiRigid=False)

    joints = {}

    for f in range(9):

        for c in range(11):
            name = await frame(s, (0, 20 * c, 10 * f), (0, 20 * c, 10 * (f + 1)), 'SEC')
            pts = await s.api('FrameObj.GetPoints', Name=name)
            joints[(c, f)] = pts['Point1']
            joints[(c, f + 1)] = pts['Point2']

        for c in range(10):
            await frame(s, (0, 20 * c, 10 * (f + 1)), (0, 20 * (c + 1), 10 * (f + 1)), 'SEC')

    for c in range(11):
        await s.api('PointObj.SetRestraint', Name=joints[(c, 0)], Value=FIXED)

    # 3 kip-s2/ft per ft of member, tributary : 10 bays x 20 ft of beam plus 11 columns x 10 ft (half at the roof)

    for f in range(1, 10):
        mass = 3 * (200 + (110 if f < 9 else 55))

        for c in range(11):
            await s.api('PointObj.SetDiaphragm', Name=joints[(c, f)], DiaphragmOption=3, DiaphragmName=f'RD{f}')

        await s.api('PointObj.SetMass', Name=joints[(0, f)], M=[0, mass, 0, 0, 0, 0], Replace=True)

    await eigen_case(s, 9)
    await s.tool('save_model', path=os.path.join(OUT, 'ETABS Example 06.edb'))
    await s.tool('run_analysis', cases=['EIGEN'])
    modes = (await s.tool('get_results', function='modal_periods', cases=['EIGEN']))['rows']
    etabs = [0.58964, 5.53195, 16.5962]
    wilson = [0.58954, 5.52696, 16.5879]

    for i in range(3):
        compare(ROWS, 'Example 6', f'Eigenvalue mode {i + 1} [rad2/s2] vs ETABS published', modes[i]['EigenValue'], etabs[i], 0.005)
        compare(ROWS, 'Example 6', f'Eigenvalue mode {i + 1} [rad2/s2] vs Wilson and Habibullah', modes[i]['EigenValue'], wilson[i], 0.005)


async def response_function(s):

    # ETABS has no API function for a user response spectrum, it is defined through the database tables

    tables = (await s.tool('list_tables', available_only=False, contains='Response Spectrum'))['tables']
    key = next(t['TableKey'] for t in tables if 'User' in t['TableKey'] and 'Functions' in t['TableKey'])
    fields = [f['FieldKey'] for f in (await s.tool('table_fields', table_key=key))['fields']]
    print('  table :', key, fields, flush=True)
    period = next(f for f in fields if f.lower().startswith('period'))
    value = next(f for f in fields if f.lower() in ('value', 'accel', 'acceleration'))
    damping = next((f for f in fields if 'damp' in f.lower()), None)
    rows = []

    for t in (0, 10):
        r = {'Name': 'CONST', period: str(t), value: '0.4'}

        if damping:
            r[damping] = '0.05'

        rows.append(r)

    log = await s.tool('edit_table', table_key=key, rows=rows, mode='replace')
    print('  edit_table :', {k: log[k] for k in ('ret', 'NumFatalErrors', 'NumErrorMsgs', 'NumWarnMsgs')}, flush=True)

    if log['NumFatalErrors'] or log['NumErrorMsgs']:
        raise RuntimeError(log.get('ImportLog', '')[:2000])


async def example_8(s):

    # two-story 3D frame, 3 x 3 column lines, story mass at the center of mass, constant 0.4 g response spectrum in X

    print('Example 8', flush=True)
    await s.api('InitializeNewModel', Units=4)
    await s.api('File.NewGridOnly', NumberStorys=2, TypicalStoryHeight=13, BottomStoryHeight=13, NumberLinesX=3, NumberLinesY=3, SpacingX=35, SpacingY=25)
    await material(s, 'MCOL', 350000, 0.2)
    await material(s, 'MBEAM', 500000, 0.2)
    await general(s, 'COL', 'MCOL', 4, 1.25, 1.25, 2.5)
    await general(s, 'BEAM', 'MBEAM', 5, 1.67, 2.61, 4.28)
    xs, ys = [0, 35, 70], [0, 25, 50]

    for f in (1, 2):
        await s.api('Diaphragm.SetDiaphragm', Name=f'RD{f}', SemiRigid=False)

    for f in (1, 2):
        z0, z1 = 13 * (f - 1), 13 * f

        for x in xs:

            for y in ys:
                c = await frame(s, (x, y, z0), (x, y, z1), 'COL')
                pts = await s.api('FrameObj.GetPoints', Name=c)

                if f == 1:
                    await s.api('PointObj.SetRestraint', Name=pts['Point1'], Value=FIXED)

                await s.api('PointObj.SetDiaphragm', Name=pts['Point2'], DiaphragmOption=3, DiaphragmName=f'RD{f}')

        for y in ys:

            for i in range(2):
                await frame(s, (xs[i], y, z1), (xs[i + 1], y, z1), 'BEAM')

        for x in xs:

            for i in range(2):
                await frame(s, (x, ys[i], z1), (x, ys[i + 1], z1), 'BEAM')

    com = {}

    for f in (1, 2):
        com[f] = await point_at(s, 38, 27, 13 * f)
        await s.api('PointObj.SetDiaphragm', Name=com[f], DiaphragmOption=3, DiaphragmName=f'RD{f}')
        await s.api('PointObj.SetMass', Name=com[f], M=[6.212, 6.212, 0, 0, 0, 0], Replace=True)

    await eigen_case(s, 6)
    await response_function(s)
    await s.api('LoadCases.ResponseSpectrum.SetCase', Name='RSX')
    await s.api('LoadCases.ResponseSpectrum.SetModalCase', Name='RSX', ModalCase='EIGEN')
    await s.api('LoadCases.ResponseSpectrum.SetLoads', Name='RSX', NumberLoads=1, LoadName=['U1'], Func=['CONST'], SF=[G], CSys=['Global'], Ang=[0])
    await s.tool('save_model', path=os.path.join(OUT, 'ETABS Example 08.edb'))
    await s.tool('run_analysis', cases=['EIGEN', 'RSX'])
    modes = (await s.tool('get_results', function='modal_periods', cases=['EIGEN']))['rows']
    etabs = [0.22708, 0.21565, 0.07335, 0.07201]
    refs = [0.22706, 0.21563, 0.07335, 0.07201]

    for i in range(4):
        compare(ROWS, 'Example 8', f'Period mode {i + 1} [s] vs ETABS published', modes[i]['Period'], etabs[i], 0.005)
        compare(ROWS, 'Example 8', f'Period mode {i + 1} [s] vs Wilson and Habibullah', modes[i]['Period'], refs[i], 0.005)

    d = (await s.tool('get_results', function='joint_displ', name=com[2], item_type='Object', cases=['RSX']))['rows']
    compare(ROWS, 'Example 8', 'RS X displacement, center of mass story 2 [ft]', max(abs(r['U1']) for r in d), 0.0201, 0.01)


async def main():

    os.makedirs(OUT, exist_ok=True)

    async with server('ETABS') as s:
        print('connect :', (await s.tool('connect', mode='start', visible=False))['program_version'], flush=True)

        try:

            todo = {'1': example_1, '6': example_6, '8': example_8}

            for ex in [todo[k] for k in (sys.argv[1:] or todo)]:

                try:
                    await ex(s)

                except Exception as e:
                    print(f'  ERROR in {ex.__name__} : {e}', flush=True)

        finally:
            await s.tool('disconnect', close_app=True)
            save(ROWS, os.path.join(HERE, 'results_etabs.json'))
            print(f'tool calls : {s.calls}', flush=True)


asyncio.run(main())
