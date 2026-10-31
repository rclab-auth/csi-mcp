# ETABS Example 1 : Plane frame with beam span loads, static gravity analysis

**Source :** CSI ETABS verification manual, Example 1 (`Manuals\Verification\Analysis\Example 01.pdf`).

A one-story, two-bay frame with pinned outer beam ends, under point loads (case 1) and a uniform load (case 2). The moments and shears of beam B1 at five stations are compared with propped-cantilever theory.

## Prompt

Paste in Claude Desktop with the `csi-etabs` extension installed :

```text
Using ETABS, rebuild CSI verification Example 1 (plane frame with beam span loads) from scratch and compare with the manual.

- New blank model in kip-in units, 2D XZ frame (active DOFs UX, UZ, RY).
- Concrete E = 3000 ksi. Columns 12 x 24 in (24 in in the frame plane), beams 12 x 30 in.
- Axial and shear deformations neglected: modifiers area = 1000, shear areas = 0 on both sections.
- No rigid joint offsets: set the end length offsets of all frames to 0 (AutoOffset off).
- Columns C1, C2, C3 at x = 0, 216, 432 in, from z = 0 to 120, fixed bases.
- Beams B1 (0 to 216) and B2 (216 to 432) at z = 120. Pinned outer ends: release M3 at the start of B1 and at the end of B2.
- B1 output stations every 54 in (quarter points).
- Case 1: joint loads 50, 100, 50 k down at the tops of C1, C2, C3, and 100 k down at mid-span of each beam.
- Case 2: 10 k/ft (10/12 k/in) uniform downward load on both beams.
- Save, run both cases, and report M3 and V2 of B1 at 0, 54, 108, 162 and 216 in (at 108 take the shear just right of the point load).

Expected (manual), case 1: M = 0, 1687.5, 3375, -337.5, -4050 k-in ; V = -31.25, -31.25, 68.75, 68.75, 68.75 k.
Case 2: M = 0, 2430, 2430, 0, -4860 k-in ; V = -67.5, -22.5, 22.5, 67.5, 112.5 k.
```

## Results

| Case | Station | M3 MCP [k-in] | M3 manual | V2 MCP [k] | V2 manual |
|---|---|---:|---:|---:|---:|
| 1 | End I | 0 | 0 | -31.25 | -31.25 |
| 1 | 1/4 | 1687.5 | 1687.5 | -31.25 | -31.25 |
| 1 | 1/2 | 3375.1 | 3375 | 68.75 | 68.75 |
| 1 | 3/4 | -337.4 | -337.5 | 68.75 | 68.75 |
| 1 | End J | -4049.9 | -4050 | 68.75 | 68.75 |
| 2 | End I | 0 | 0 | -67.50 | -67.5 |
| 2 | 1/4 | 2430.0 | 2430 | -22.50 | -22.5 |
| 2 | 1/2 | 2430.1 | 2430 | 22.50 | 22.5 |
| 2 | 3/4 | 0.09 | 0 | 67.50 | 67.5 |
| 2 | End J | -4859.9 | -4860 | 112.50 | 112.5 |

All within 0.03 %. Note : ETABS adds rigid end offsets automatically from the member depths; the example requires them off, otherwise the results differ by about 10 %. Script : [`validation/etabs_examples.py`](../validation/etabs_examples.py), function `example_1`.
