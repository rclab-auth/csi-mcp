# SAP2000 Example 2-008 : Cantilever plate eigenvalue problem

**Source :** CSI SAP2000 verification manual, Example 2-008 (`Manuals\Verification\Analysis\Shells\Problem 2-008.pdf`), model C, thin plate.

A 24 × 24 × 1 in steel plate, cantilevered from its base, is meshed 40 × 40. The periods of the first five plate-bending modes are compared with SAP2000's published values and with Harris and Crede (1976).

## Prompt

```text
Using SAP2000, rebuild CSI verification Example 2-008, model C thin plate (cantilever plate eigenvalues), from scratch and compare with the manual.

- New blank model in kip-in units. Active DOFs UY, RX, RZ only (plate bending in the XZ plane).
- Steel material E = 29000 ksi, nu = 0.3, mass per unit volume 7.35E-07 k-s2/in4 (with t = 1 in this gives 7.35E-07 k-s2/in3 per area).
- Shell property: Shell-thin, thickness 1 in (membrane and bending), no drilling DOF.
- One area object with corners (0,0,0), (24,0,0), (24,0,24), (0,0,24).
- Restrain UY and RX at the two base corners (z = 0).
- Auto-mesh the area 40 x 40, with "restraints on edge" enabled so that the whole base is restrained.
- Modal case MODAL with 12 modes. Save, run MODAL, report the first five periods.

Expected (manual, model C thin): 0.01735, 0.00708, 0.00283, 0.00222, 0.00195 s.
Independent (Harris and Crede): 0.01723, 0.00704, 0.00281, 0.00219, 0.00193 s.
```

## Results

| Mode | MCP [s] | Manual SAP2000 [s] | Difference | Independent [s] | Difference |
|---|---:|---:|---:|---:|---:|
| 1 | 0.017352 | 0.01735 | +0.01 % | 0.01723 | +0.71 % |
| 2 | 0.0070841 | 0.00708 | +0.06 % | 0.00704 | +0.63 % |
| 3 | 0.0028323 | 0.00283 | +0.08 % | 0.00281 | +0.79 % |
| 4 | 0.0022181 | 0.00222 | -0.09 % | 0.00219 | +1.28 % |
| 5 | 0.0019483 | 0.00195 | -0.09 % | 0.00193 | +0.95 % |

The differences from the independent solution are the same as in the manual (the independent solution approximates plate modes with beam modes). Script : [`validation/sap2000_examples.py`](../validation/sap2000_examples.py), function `example_2_008`.
