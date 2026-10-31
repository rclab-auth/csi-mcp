# ETABS Example 6 : Nine-story, ten-bay plane frame, eigenvalue analysis

**Source :** CSI ETABS verification manual, Example 6 (`Manuals\Verification\Analysis\Example 06.pdf`).

A nine-story, ten-bay plane frame with one horizontal mass per floor. The first three eigenvalues are compared with ETABS's published values and with Wilson and Habibullah (1992) and Bathe and Wilson (1972).

## Prompt

```text
Using ETABS, rebuild CSI verification Example 6 (nine-story, ten-bay plane frame, eigenvalues) from scratch and compare with the manual.

- Initialize a new model in kip-ft units and create it with File.NewGridOnly: 9 stories, typical and bottom story height 10 ft (stories must exist at the floor levels so that the default mass source lumps lateral masses there).
- Material E = 432000 ksf, weight and mass 0.
- General section for all members: A = 3 ft2, I22 = I33 = 1 ft4, J = 1 ft4, shear areas 0.
- Frame in the YZ plane: 11 column lines at y = 0, 20, ..., 200 ft, 9 stories at 10 ft. Columns between floors, beams between column lines at each floor. Fixed bases.
- One rigid diaphragm per floor (use new names, not D1), assigned to all joints of that floor.
- Mass 3 kip-s2/ft per ft of member, lumped as one horizontal mass per floor at the joint of the first column line: 930 kip-s2/ft at floors 1 to 8 (200 ft of beams + 11 x 10 ft of columns), 765 at the roof (columns count half).
- Eigen modal case with 9 modes. Save, run it, and report the first three eigenvalues.

Expected: ETABS 0.58964, 5.53195, 16.5962 ; Wilson and Habibullah 0.58954, 5.52696, 16.5879 (rad2/s2).
```

## Results

| Mode | MCP [rad²/s²] | Manual ETABS | Difference | Wilson and Habibullah | Difference |
|---|---:|---:|---:|---:|---:|
| 1 | 0.58964 | 0.58964 | 0.00 % | 0.58954 | +0.02 % |
| 2 | 5.5320 | 5.53195 | 0.00 % | 5.52696 | +0.09 % |
| 3 | 16.596 | 16.5962 | 0.00 % | 16.5879 | +0.05 % |

Identical to the published ETABS values; the small difference from the references comes from their extra vertical masses, as the manual explains. Script : [`validation/etabs_examples.py`](../validation/etabs_examples.py), function `example_6`.
