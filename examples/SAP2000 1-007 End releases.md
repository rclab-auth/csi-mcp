# SAP2000 Example 1-007 : Frame end releases

**Source :** CSI SAP2000 verification manual, Example 1-007 (`Manuals\Verification\Analysis\Frames\Problem 1-007.pdf`).

Three statically determinate frames differ only in one end release : a beam shear release (A), a column axial release (B) and a beam moment release (C). The reactions at the fixed support are compared with hand calculations.

## Prompt

Paste in Claude Desktop with the `csi-sap2000` extension installed :

```text
Using SAP2000, rebuild CSI verification Example 1-007 (frame end releases) from scratch and compare with the manual.

For each of three models A, B and C:
- New blank model in kip-ft units. Make it a 2D XZ frame by setting the active DOFs to UX, UZ, RY only.
- Any material and a 1 ft x 1 ft rectangular section (the frames are statically determinate).
- Column from (0,0,0) to (0,0,10), fully fixed at the base. Beam from (0,0,10) to (10,0,10), roller at (10,0,10) restraining UZ only.
- Load pattern P10 (type Other, self-weight multiplier 0): a 10 k downward point load at mid-span of the beam (relative distance 0.5, gravity direction).
- Releases (order P, V2, V3, T, M2, M3):
  - A: beam start, V2 released
  - B: column end, P (axial) released
  - C: beam start, M3 released
- Save, run P10, and report the reaction Fz and My at the fixed support.

Expected (manual): A Fz=0, My=50 k-ft ; B Fz=0, My=50 k-ft ; C Fz=5 k, My=0.
```

## Results

| Model | Quantity | MCP | Manual |
|---|---|---:|---:|
| A | Fz [k] | 0 | 0 |
| A | My [k-ft] | 50.00 | 50 |
| B | Fz [k] | 0 | 0 |
| B | My [k-ft] | 50.00 | 50 |
| C | Fz [k] | 5.00 | 5 |
| C | My [k-ft] | 0 | 0 |

Exact match. Script : [`validation/sap2000_examples.py`](../validation/sap2000_examples.py), function `example_1_007`.
