# CSI verification Example 1-001 (frame, general loading), the same problem in SAP2000 and in ETABS
# Used by sap2000_examples.py and etabs_examples.py

import os
from verif_client import compare

# independent hand-calculated displacements of the manual, cases 1 to 4 vertical (U3), cases 5 to 7 horizontal (U1) [in]

EXPECTED = [-0.02639, 0.06296, 0.06296, -0.2963, 0.3125, 0.11556, 0.00651]


async def example_1_001(s, rows, out, ext):

    # three-element concrete frame under seven load cases, axial and shear deformations neglected (area modifier 1000)

    print('1-001', flush=True)
    await s.tool('new_blank_model', units='kip_in_F')
    await s.api('PropMaterial.SetMaterial', Name='CONC', MatType=2)
    await s.api('PropMaterial.SetMPIsotropic', Name='CONC', E=3600, U=0.2, A=0.0000055)
    await s.api('PropFrame.SetRectangle', Name='R1', MatProp='CONC', T3=12, T2=12)
    await s.api('PropFrame.SetModifiers', Name='R1', Value=[1000, 0, 0, 1, 1, 1, 1, 1])
    await s.tool('set_units', units='kip_ft_F')
    f1 = (await s.api('FrameObj.AddByCoord', XI=0, YI=0, ZI=0, XJ=0, YJ=0, ZJ=10, PropName='R1', UserName='1'))['Name']
    f2 = (await s.api('FrameObj.AddByCoord', XI=0, YI=0, ZI=10, XJ=8, YJ=0, ZJ=16, PropName='R1', UserName='2'))['Name']
    f3 = (await s.api('FrameObj.AddByCoord', XI=-4, YI=0, ZI=10, XJ=0, YJ=0, ZJ=10, PropName='R1', UserName='3'))['Name']
    p1 = await s.api('FrameObj.GetPoints', Name=f1)
    await s.api('PointObj.SetRestraint', Name=p1['Point1'], Value=[True, True, True, True, False, False])
    p2 = await s.api('FrameObj.GetPoints', Name=f2)
    await s.api('PointObj.SetRestraint', Name=p2['Point2'], Value=[True, True, False, False, False, False])

    for i in range(1, 8):
        await s.api('LoadPatterns.Add', Name=str(i), MyType=8, SelfWTMultiplier=1 if i == 1 else 0, AddAnalysisCase=True)

    p3 = await s.api('FrameObj.GetPoints', Name=f3)
    await s.api('PointObj.SetLoadForce', Name=p3['Point1'], LoadPat='2', Value=[0, 0, -10, 0, 0, 0])
    await s.api('FrameObj.SetLoadDistributed', Name=f3, LoadPat='2', MyType=1, Dir=10, Dist1=0, Dist2=1, Val1=1.8, Val2=1.8)
    await s.api('PointObj.SetLoadForce', Name=p3['Point2'], LoadPat='3', Value=[0, 0, -17.2, 0, -54.4, 0])
    await s.api('FrameObj.SetLoadDistributed', Name=f2, LoadPat='4', MyType=1, Dir=11, Dist1=0, Dist2=1, Val1=2, Val2=2)
    await s.api('FrameObj.SetLoadDistributed', Name=f1, LoadPat='5', MyType=1, Dir=2, Dist1=0, Dist2=1, Val1=2, Val2=2, CSys='Local')
    await s.api('FrameObj.SetLoadDistributed', Name=f2, LoadPat='5', MyType=1, Dir=2, Dist1=0, Dist2=1, Val1=-2, Val2=-2, CSys='Local')
    await s.api('FrameObj.SetLoadDistributed', Name=f1, LoadPat='6', MyType=1, Dir=2, Dist1=0, Dist2=1, Val1=0.9984, Val2=0.3744, CSys='Local')
    await s.api('FrameObj.SetLoadDistributed', Name=f2, LoadPat='6', MyType=1, Dir=2, Dist1=0, Dist2=1, Val1=-0.3744, Val2=0, CSys='Local')
    await s.api('FrameObj.SetLoadPoint', Name=f2, LoadPat='7', MyType=1, Dir=2, Dist=0.5, Val=-15, CSys='Local')
    await s.tool('set_units', units='kip_in_F')
    await s.tool('save_model', path=os.path.join(out, 'Example 1-001' + ext))
    await s.tool('run_analysis', cases=[str(i) for i in range(1, 8)])

    for i in range(1, 8):
        pt = p2['Point2'] if i <= 4 else p2['Point1']
        row = (await s.tool('get_results', function='joint_displ', name=pt, item_type='Object', cases=[str(i)]))['rows'][0]
        got = row['U3'] if i <= 4 else row['U1']
        quantity = f'Case {i} : ' + ('Uz at the end of the inclined member [in]' if i <= 4 else 'Ux at the knee joint (0, 0, 10 ft) [in]')
        compare(rows, '1-001', quantity, got, EXPECTED[i - 1], 0.01)
