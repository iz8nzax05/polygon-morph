# Polygon Morph

Polygons morph from one shape to another through an animated resistance field. Each vertex moves at its own speed — slowed or accelerated by a wave that shifts beneath the shape as it travels.

---

## How it works

An animated field of three overlapping sine waves covers the canvas:

```
wave1 = sin((nx + ny) * freq * π + time * 2.0)   # diagonal
wave2 = sin((nx - ny) * freq * π + time * 1.5)   # counter-diagonal
wave3 = sin(ny * freq * 2π + time * 3.0)          # vertical
```

The average of the three waves becomes a resistance value from 0 to 1. Each vertex samples the field at its current position to get its speed:

```
speed = 0.1 + (1 - resistance) * 0.9
```

High resistance slows a vertex almost to a stop. Low resistance lets it move at full speed. Because every vertex reads the field independently, some race ahead while others lag — the shape stretches and warps before landing.

Wave direction also exerts a small pull on each vertex. The engine samples the gradient at ±5px and applies `force = -gradient * 20` scaled by a `wave_influence` factor of 0.3.

---

## Adaptive vertex system

The polygon vertex count adjusts while morphing:

- **Removal** — vertices with curvature below 0.15 rad are removed after 30% progress
- **Addition** — vertices with curvature above 1.0 rad get a neighbor inserted before 70% progress
- **Cap** — max 64 vertices
- **Deviant kill** — after 20% progress, any vertex more than 15px from the straight line between start and end position is removed

This keeps the mesh clean and avoids pileups at tight corners.

---

## Shapes

9 presets, all initialized with 32 distributed vertices:

| Key | Shape |
|---|---|
| `1` | Square |
| `2` | Triangle |
| `3` | Star (5-point) |
| `4` | Hexagon |
| `5` | Pentagon |
| `Q` | Octagon |
| `W` | Star (8-point) |
| `E` | Star (12-point) |
| `R` | Dodecagon |

Keys `1–5` / `QWER` set the start shape. Keys `6–0` / `ASDF` set the end shape.

---

## Controls

| Input | Action |
|---|---|
| `1–5` / `QWER` | Set start shape |
| `6–0` / `ASDF` | Set end shape |
| `Enter` | Start morph |
| `X` | Enter custom draw mode (click points, Enter to finish) |
| Arrow Up/Down | Wave frequency |
| Arrow Left/Right | Wave amplitude |
| Scroll | Morph speed |
| `G` | Toggle wave force on/off |
| `H` | Toggle wave visualization |
| `T` | Toggle deviant vertex culling |

---

## Running it

```bash
pip install pygame numpy
python main.py
```

**~1,065 lines** across 4 modules (`main.py`, `morph_engine.py`, `wave_field.py`, `polygon.py`).
