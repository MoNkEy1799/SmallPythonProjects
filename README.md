# Collection of some small/ random Python projects

## Circuit Visualizer
Qiskit/ Perceval (Quandela) like visualizer for integrated photonic circuits.

## Lorenz System
3D animation of a Lorenz Attractor with PyQtGraph.

- `Start`, `Stop`, `Reset` control the animation.
- `Speed` slider changes the amount of points drawn per update cycle.
- `Plot Type` changes between scatter and line plot.
- `Truncate` truncates the data point array to the given size (the plot will begin to lag after some time without truncation).
- Move the mouse around/ scroll for camera controll.

## IBMQ Spring Challange 2023

Quick implementation of the IBMQ Sherbrooke (Eagle r3 Chip) Qubit map and calculations to optimally solve Lab 5 in the IBM Quantum Spring Challenge 2023.
Resulting transpiled circuit depth is 59 which I guess is the best hardware optimized solution.

## PXL2ASCII

Implementation of an image downsampler and pixel to ascii converter. Ascii conversion modes:
- ***brightness***: depending on pixel brightness (mean(r, g, b)) the ascii image will have different characters in it (depending on the given ascii mask)
- ***color/rgb***: fully converts the image to rgb ascii characters (default is 'full block' char: \u2588) using ANSI escape codes: https://en.wikipedia.org/wiki/ANSI_escape_code

Main usage for this is to animate the measurement of integrated photonic chips: `integratedChip.py`.
