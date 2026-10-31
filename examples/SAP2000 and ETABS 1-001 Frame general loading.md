# SAP2000 and ETABS Example 1-001 : Frame, general loading

**Source :** CSI SAP2000 verification manual, Example 1-001 (`Manuals\Verification\Analysis\Frames\Problem 1-001.pdf`). The same problem is the Python example of both API help files.

A three-element concrete frame is subjected to seven load cases with distributed, concentrated, trapezoidal and local-axis loads. The displacements at two joints are compared with independent hand calculations. The example runs the same way in SAP2000 and in ETABS.

## Prompt

Paste in Claude Desktop with the `csi-sap2000` or the `csi-etabs` extension installed :

```text
Using SAP2000 (or ETABS), rebuild CSI verification Example 1-001 (frame, general loading) from scratch and compare with the manual.

- New blank model in kip-in units.
- Concrete material CONC: E = 3600 ksi, nu = 0.2, alpha = 5.5E-06. Rectangular section R1, 12 x 12 in, with modifiers area = 1000, shear areas = 0, all others 1.
- Switch to kip-ft units. Three frames with section R1:
  1: (0,0,0) to (0,0,10)   2: (0,0,10) to (8,0,16)   3: (-4,0,10) to (0,0,10)
- Restraints: base of frame 1 restrained UX, UY, UZ, RX ; end of frame 2 at (8,0,16) restrained UX, UY.
- Load patterns 1 to 7, type Other, self-weight multiplier 1 for pattern 1 and 0 for the others, each with its own analysis case:
  - 2: 10 k down at (-4,0,10) and 1.8 k/ft gravity load on frame 3
  - 3: joint load at (0,0,10): Fz = -17.2 k, My = -54.4 k-ft
  - 4: 2 k/ft on frame 2 in the projected gravity direction (direction 11)
  - 5: 2 k/ft on frame 1 and -2 k/ft on frame 2, local 2 direction
  - 6: trapezoidal local 2 load, 0.9984 to 0.3744 k/ft on frame 1 and -0.3744 to 0 k/ft on frame 2
  - 7: -15 k point load at mid-length of frame 2, local 2 direction
- Switch back to kip-in, save, run cases 1 to 7.
- Report Uz at the end of frame 2 (8,0,16) for cases 1 to 4, and Ux at (0,0,10) for cases 5 to 7.

Expected (manual) [in]: -0.02639, 0.06296, 0.06296, -0.2963, 0.3125, 0.11556, 0.00651.
```

## Results

| Case | Quantity | Manual [in] | SAP2000 26.2.0 [in] | ETABS 23.2.0 [in] |
|---|---|---:|---:|---:|
| 1 | Uz, end of frame 2 | -0.02639 | -0.02639 | -0.026411 (+0.08 %) |
| 2 | Uz, end of frame 2 | 0.06296 | 0.06296 | 0.06296 |
| 3 | Uz, end of frame 2 | 0.06296 | 0.06296 | 0.06296 |
| 4 | Uz, end of frame 2 | -0.2963 | -0.2963 | -0.2963 |
| 5 | Ux at (0,0,10) | 0.3125 | 0.3125 | 0.3125 |
| 6 | Ux at (0,0,10) | 0.11556 | 0.11556 | 0.11556 |
| 7 | Ux at (0,0,10) | 0.00651 | 0.0065114 (+0.02 %) | 0.0065114 (+0.02 %) |

Case 1 (self weight) differs by 0.08 % in ETABS; its cause was not investigated. All other values are identical in both programs.

Script : [`validation/example_1_001.py`](../validation/example_1_001.py), used by both `sap2000_examples.py` and `etabs_examples.py`.
