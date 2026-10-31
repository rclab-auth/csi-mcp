# Rebuilds CSI verification examples from scratch through the MCP tools and compares with the published results
# Usage : uv run --no-project --with "mcp<2" python validation\sap2000_examples.py

import asyncio
import os
from verif_client import HERE, compare, save, server
from example_1_001 import example_1_001

print('\nSAP2000 verification examples (1-001, 1-007, 1-013, 2-008) through the MCP server')
print('V.K. Papanikolaou, Assoc. Prof. AUTh')
print('Last updated : 31/10/2026\n')

OUT = os.path.join(HERE, 'models')
ROWS = []
PIN = [True, True, True, False, False, False]
FIXED = [True] * 6
FREE = [False] * 6


async def material(s, name, mtype, e, u):

    await s.api('PropMaterial.SetMaterial', Name=name, MatType=mtype)
    await s.api('PropMaterial.SetMPIsotropic', Name=name, E=e, U=u, A=0)


async def example_1_007(s):

    # three statically determinate frames, identical except for one end release each

    expected = {'A': (0, 50), 'B': (0, 50), 'C': (5, 0)}

    for model, (fz, my) in expected.items():
        print(f'1-007 model {model}', flush=True)
        await s.tool('new_blank_model', units='kip_ft_F')
        await s.api('Analyze.SetActiveDOF', DOF=[True, False, True, False, True, False])
        await material(s, 'MAT', 2, 500000, 0.2)
        await s.api('PropFrame.SetRectangle', Name='R1', MatProp='MAT', T3=1, T2=1)
        col = (await s.api('FrameObj.AddByCoord', XI=0, YI=0, ZI=0, XJ=0, YJ=0, ZJ=10, PropName='R1'))['Name']
        beam = (await s.api('FrameObj.AddByCoord', XI=0, YI=0, ZI=10, XJ=10, YJ=0, ZJ=10, PropName='R1'))['Name']
        base = (await s.api('FrameObj.GetPoints', Name=col))['Point1']
        roller = (await s.api('FrameObj.GetPoints', Name=beam))['Point2']
        await s.api('PointObj.SetRestraint', Name=base, Value=FIXED)
        await s.api('PointObj.SetRestraint', Name=roller, Value=[False, False, True, False, False, False])

        # releases in the order P, V2, V3, T, M2, M3 : A beam shear at its start, B column axial at its top, C beam moment at its start

        if model == 'A':
            await s.api('FrameObj.SetReleases', Name=beam, II=[False, True, False, False, False, False], JJ=FREE, StartValue=[0] * 6, EndValue=[0] * 6)

        elif model == 'B':
            await s.api('FrameObj.SetReleases', Name=col, II=FREE, JJ=[True, False, False, False, False, False], StartValue=[0] * 6, EndValue=[0] * 6)

        else:
            await s.api('FrameObj.SetReleases', Name=beam, II=[False, False, False, False, False, True], JJ=FREE, StartValue=[0] * 6, EndValue=[0] * 6)

        await s.api('LoadPatterns.Add', Name='P10', MyType=8, SelfWTMultiplier=0, AddAnalysisCase=True)
        await s.api('FrameObj.SetLoadPoint', Name=beam, LoadPat='P10', MyType=1, Dir=10, Dist=0.5, Val=10)
        await s.tool('save_model', path=os.path.join(OUT, f'SAP 1-007{model}.sdb'))
        await s.tool('run_analysis', cases=['P10'])
        row = (await s.tool('get_results', function='joint_react', name=base, item_type='Object', cases=['P10']))['rows'][0]
        compare(ROWS, '1-007', f'Model {model} : Fz at fixed support [k]', row['F3'], fz, 1e-6)
        compare(ROWS, '1-007', f'Model {model} : My at fixed support [k-ft]', row['M2'], my, 1e-6)


async def example_1_013(s):

    # simply supported 36x36 in beam on elastic foundation, 15 ft, 500 k at midspan, model C (2 x 100 elements)

    print('1-013 model C', flush=True)
    await s.tool('new_blank_model', units='kip_in_F')
    await s.api('Analyze.SetActiveDOF', DOF=[True, False, True, False, True, False])
    await material(s, 'CONC', 2, 3600, 0.2)
    await s.api('PropFrame.SetRectangle', Name='B36', MatProp='CONC', T3=36, T2=36)

    # only bending deformations : area modifier 1000, shear area modifiers 0

    await s.api('PropFrame.SetModifiers', Name='B36', Value=[1000, 0, 0, 1, 1, 1, 1, 1])
    left = (await s.api('FrameObj.AddByCoord', XI=0, YI=0, ZI=0, XJ=90, YJ=0, ZJ=0, PropName='B36'))['Name']
    right = (await s.api('FrameObj.AddByCoord', XI=90, YI=0, ZI=0, XJ=180, YJ=0, ZJ=0, PropName='B36'))['Name']
    p1 = await s.api('FrameObj.GetPoints', Name=left)
    p3 = (await s.api('FrameObj.GetPoints', Name=right))['Point2']
    mid = p1['Point2']
    await s.api('PointObj.SetRestraint', Name=p1['Point1'], Value=PIN)
    await s.api('PointObj.SetRestraint', Name=p3, Value=[False, False, True, False, False, False])

    # subgrade modulus 800 k/ft3 x 3 ft width = 2400 k/ft2 = 16.667 k/in per inch of length, along the frame local 2 axis (global Z)

    for f in (left, right):
        await s.api('FrameObj.SetSpring', Name=f, MyType=1, S=2400 / 144, SimpleSpringType=1, LinkProp='', SpringLocalOneType=1,
                    Dir=2, Plane23Angle=0, Vec=[0, 0, 0], Ang=0, Replace=True)
        await s.api('FrameObj.SetAutoMesh', Name=f, AutoMesh=True, AutoMeshAtPoints=False, AutoMeshAtLines=False, NumSegs=100, AutoMeshMaxLength=0)

    await s.api('LoadPatterns.Add', Name='P500', MyType=8, SelfWTMultiplier=0, AddAnalysisCase=True)
    await s.api('PointObj.SetLoadForce', Name=mid, LoadPat='P500', Value=[0, 0, -500, 0, 0, 0])
    await s.tool('save_model', path=os.path.join(OUT, 'SAP 1-013C.sdb'))
    await s.tool('run_analysis', cases=['P500'])
    d = (await s.tool('get_results', function='joint_displ', name=mid, item_type='Object', cases=['P500']))['rows'][0]
    compare(ROWS, '1-013', 'Uz at midspan [in]', d['U3'], -0.08933, 0.005)
    forces = (await s.tool('get_results', function='frame_force', name=left, item_type='Object', cases=['P500'], max_rows=1000))['rows']
    m_mid = max(forces, key=lambda r: r['ObjSta'])['M3']
    compare(ROWS, '1-013', 'My at midspan [k-in]', m_mid, 17698, 0.005)


async def example_2_008(s):

    # 24 x 24 x 1 in cantilever plate in the XZ plane, thin plate, 40 x 40 mesh, plate bending modes only

    print('2-008 model C thin', flush=True)
    await s.tool('new_blank_model', units='kip_in_F')
    await s.api('Analyze.SetActiveDOF', DOF=[False, True, False, True, False, True])
    await material(s, 'STEEL', 1, 29000, 0.3)
    await s.api('PropMaterial.SetWeightAndMass', Name='STEEL', MyOption=2, Value=7.35e-07)
    await s.api('PropArea.SetShell_1', Name='PLATE', ShellType=1, IncludeDrillingDOF=False, MatProp='STEEL', MatAng=0, Thickness=1, Bending=1)
    area = (await s.api('AreaObj.AddByCoord', NumberPoints=4, X=[0, 24, 24, 0], Y=[0, 0, 0, 0], Z=[0, 0, 24, 24], PropName='PLATE'))['Name']
    pts = (await s.api('AreaObj.GetPoints', Name=area))['Point']

    for p in pts[:2]:
        await s.api('PointObj.SetRestraint', Name=p, Value=[False, True, False, True, False, False])

    await s.api('AreaObj.SetAutoMesh', Name=area, MeshType=1, N1=40, N2=40, RestraintsOnEdge=True)
    await s.api('LoadCases.ModalEigen.SetNumberModes', Name='MODAL', MaxModes=12, MinModes=1)
    await s.tool('save_model', path=os.path.join(OUT, 'SAP 2-008C-thin.sdb'))
    await s.tool('run_analysis', cases=['MODAL'])
    periods = (await s.tool('get_results', function='modal_periods', cases=['MODAL']))['rows']
    published = [0.01735, 0.00708, 0.00283, 0.00222, 0.00195]
    independent = [0.01723, 0.00704, 0.00281, 0.00219, 0.00193]

    for i, (p, ind) in enumerate(zip(published, independent)):
        compare(ROWS, '2-008', f'Period mode {i + 1} [s] vs SAP2000 published', periods[i]['Period'], p, 0.01)
        compare(ROWS, '2-008', f'Period mode {i + 1} [s] vs independent', periods[i]['Period'], ind, 0.025)


async def main():

    os.makedirs(OUT, exist_ok=True)

    async with server('SAP2000') as s:
        print('connect :', (await s.tool('connect', mode='start', visible=False))['program_version'], flush=True)

        try:
            await example_1_001(s, ROWS, OUT, '.sdb')
            await example_1_007(s)
            await example_1_013(s)
            await example_2_008(s)

        finally:
            await s.tool('disconnect', close_app=True)
            save(ROWS, os.path.join(HERE, 'results_sap2000.json'))
            print(f'tool calls : {s.calls}', flush=True)


asyncio.run(main())
