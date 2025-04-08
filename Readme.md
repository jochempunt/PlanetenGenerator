# 🌍 Planet Generator (Blender Addon)

This is a Blender plugin written in Python using `bpy`. It adds an operator that lets you generate customizable planets directly in the 3D Viewport. The tool was created for a university project and supports two main types of planets: **Gas Giants** and **Terrestrial Planets**.

---

## Overview

After installing the addon, a new entry appears under `Add > Planet-Generator`. You can tweak a variety of settings before generating a planet, including surface details, rings, atmosphere, and cloud layers. All geometry and materials are created procedurally.

### Supported Planet Types

- **Gas Planet**: Smooth surface with optional rings and an atmospheric glow at the edges.
![gasPlanet](https://github.com/jochempunt/PlanetenGenerator/blob/main/gas_planet.jpg?raw=true)

- **Rocky Planet** (Gesteinsplanet): Procedural continents, oceans, and optionally clouds and atmosphere.
![terrestrialPlanet](https://github.com/jochempunt/PlanetenGenerator/blob/main/terrestrial_planet.jpg?raw=true)
---

## Parameters

Each planet type comes with its own set of customizable options:

### Gas Planet
- Subdivision level
- Surface pattern scale and detail
- Surface color gradient (1–2 colors)
- Optional rings (size, thickness, pattern)
- Edge transparency to simulate atmosphere

### Terrestrial Planet
- Terrain bumpiness and noise
- Three land colors
- Oceans with wave simulation and shorelines
- Optional clouds and atmosphere with adjustable opacity and size

---

## How to Install

1. Open Blender 3.1.1 or newer  
2. Go to `Edit > Preferences > Add-ons > Install`  
3. Select `operator_planet.py`  
4. Enable the addon  
5. Use it from the `Add > Planet-Generator` menu in the 3D View

---

## Files

- `operator_planet.py` – main addon script  
---

## Notes

Created for educational use. Works with Blender 3.1.1 and probably newer versions too. All materials are generated procedurally with node trees.
