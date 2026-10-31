# SAP2000 Example 1-013 : Simply supported beam on elastic foundation

**Source :** CSI SAP2000 verification manual, Example 1-013 (`Manuals\Verification\Analysis\Frames\Problem 1-013.pdf`), model C.

A 36 × 36 in beam, 15 ft long, on an elastic foundation (subgrade modulus 800 k/ft³) carries a 500 k load at midspan. The deflection and moment at midspan are compared with Timoshenko (1956).

## Prompt

```text
Using SAP2000, rebuild CSI verification Example 1-013, model C (simply supported beam on elastic foundation), from scratch and compare with the manual.

- New blank model in kip-in units, 2D XZ frame (active DOFs UX, UZ, RY).
- Concrete material E = 3600 ksi, nu = 0.2. Rectangular section 36 in deep x 36 in wide.
- Only bending deformations: section modifiers area = 1000, shear areas = 0, all others 1.
- Two frames: (0,0,0)-(90,0,0) and (90,0,0)-(180,0,0). Pin at x=0 (UX, UY, UZ), roller at x=180 (UZ).
- Line spring on both frames: simple spring, tension and compression, stiffness 2400/144 = 16.667 k/in per inch of length (3 ft width x 800 k/ft3), along the frame local 2 axis (global Z).
- Auto-mesh each frame into 100 segments.
- Load pattern P500 (Other, self weight 0): 500 k downward joint load at the midspan joint (x = 90).
- Save, run P500, and report Uz and the moment M3 at midspan.

Expected (manual): Uz = -0.08933 in, M = 17,698 k-in.
```

## Results

| Quantity | MCP | Manual | Difference |
|---|---:|---:|---:|
| Uz at midspan [in] | -0.089333 | -0.08933 | 0.00 % |
| M at midspan [k-in] | 17,698 | 17,698 | 0.00 % |

Script : [`validation/sap2000_examples.py`](../validation/sap2000_examples.py), function `example_1_013`.
