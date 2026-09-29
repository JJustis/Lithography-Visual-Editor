# Lithography Voxel Lab

`Lithography Voxel Lab` is a playable Python prototype for a voxel-style chip fabrication game. You are an engineer reduced to a particle-scale avatar inside a PCB lab. Build lithography patterns for four chips, route their shared bus, and watch the live monitor respond as the virtual computer runs.

## Run

From this folder:

```bash
python3 lithography_voxel_lab.py
```

The built-in `AURORA FAB // WORKING COMPUTER` boots already connected: all four chips, gates, ports, layered bus traces, lithography fields, and the live screen output are online immediately. Use it as a running reference system, or load a custom JSON to start a fresh fabrication job.

Load a generated system from JSON:

```bash
python3 lithography_voxel_lab.py --system example_system.json
# or: python3 lithography_voxel_lab.py example_system.json
```

A separate quantum reference system is included:

```bash
python3 lithography_voxel_lab.py --system quantum_system.json
```

The third quick-load option is a parallel SIMD computer:

```bash
python3 lithography_voxel_lab.py --system parallel_system.json
```

The File menu also has **Load 8-bit Computer**, or load the complete BYTEFORGE system directly:

```bash
python3 lithography_voxel_lab.py --system 8bit_computer.json
```

It also includes **Load Turing Machine** for the tape-based TAPEWEAVE computer:

```bash
python3 lithography_voxel_lab.py --system turing_machine.json
```

The File menu also includes **Load SOC-32 Workstation**, a larger equation-and-graphics system. Run it with: python3 lithography_voxel_lab.py --system soc_workstation.json

While the simulator is running, use **File → Load System from File…** or `Ctrl+O` to choose any system JSON. The File menu also contains quick loaders for the neural, quantum, and parallel examples, plus an **Experimental Computers** submenu for topological braid, photonic wavefront, and hybrid quantum machines. Save and Save As are also available.

It uses only Python's standard library and Tkinter. On Debian/Ubuntu, install Tkinter if it is missing:

```bash
sudo apt install python3-tk
```

Run the logic check without opening a window:

```bash
python3 lithography_voxel_lab.py --self-test
```

## Controls

- `WASD` or arrow keys: move the engineer particle
- `F`: toggle flight mode; `Space`/`Shift` change altitude while flying
- `1`–`4`: select silicon, copper, resist, or mask on the PCB floor
- Left click: deposit the selected voxel material
- Right click: break the upper voxel and recover its material
- `Z`: enter chip scale for the nearest chip; `Esc`/`Z`: return to the fab floor
- In chip scale, `1`–`4` select SOURCE, AND, OR, or NOT gates
- In chip scale, left click snaps a gate into a grid slot; right click removes it
- In chip scale, click a face connector block to link/unlink a bus slot
- `L`: expose the active chip or the most complete macro pattern
- `Esc`: quit from the macro view

The included [example_system.json](/home/jdaj/Downloads/lithography_voxel_lab/example_system.json) is a complete layered neural computer. It models a sensory cortex, synaptic core, spike-threshold unit, recurrent memory, and motor-output chip connected by a three-layer synapse bus. Run `python3 lithography_voxel_lab.py --system example_system.json` from this folder. The loader reads system metadata, an ordered bus path for every layer, starter traces, vertical `connections`, and any number of chips. Each chip can define a relative lithography `pattern`, per-face `face_slots`, a `gate_target`, and optional `initial_gates` / `connected_ports`; the game builds the board and chip queue automatically on launch.

The macro board is logically infinite. Use `PageUp` / `PageDown` to switch fabric layers; bright dashed vertical lines and labeled endpoint dots show vias and connections passing through layers. The mouse wheel zooms the board in both isometric and top-down modes around the cursor; `+`/`-` zoom around the viewport center, and `Ctrl`+wheel remains available for fast block selection. JSON `lithography.fields` creates massive viewport-rendered mask arrays with field boundaries, repeating patterns, and PCB tap lines. The **SYSTEM OUTPUT // LIVE** HUD reports the active bus, chip paths, port links, and total lithography loci. Flight mode lets you move the particle across the unbounded grid.

The right-side **BUS MONITOR // LIVE** is the game's input/output screen. It shows bus health, clock, thermal load, pipeline state, chip queue progress, gate counts, face-port counts, exposure results, and a live binary stream. The **COMPUTE SPEED** slider in the world header controls LITHO-ISA instructions per tick (1–512); the same control is available in the program editor. The sidebar has its own scrollbar: scroll over it or drag the bar at the far right. Its lower **GRAPHICAL OUTPUT // LIVE CARRIER PLOT** shows the animated signal waveform, moving particles on each bus layer, and live per-chip output levels. Each chip is a multi-slot item: its north/east/south/west faces expose one visible connector block per bus connection.

The macro fab now has two construction views: press `T` for a square-cell top-down builder, or press `T` again to return to the isometric voxel view. Top-down building is snapped directly to the selected layer and is easier for large lithography layouts. The palette includes silicon, copper, resist, mask, dielectric, gold, N-type, P-type, and via blocks. Use `Q`/`E` to cycle blocks, number keys when available, and `PageUp`/`PageDown` to change layers.

The simulator uses infinite construction stock by default: every material and particle gate can be placed repeatedly, and the HUD shows `∞` instead of a finite inventory. The lower-right framed **SCREEN OUTPUT // LIVE** panel is the in-game simulator output surface; it receives the loaded system's output message, bus bitstream, field/layer totals, chip status, animated signal trace, and any JSON `equations` as rotating live equation examples. Open **File → Open 512×512 Screen Output…** or press `F2` for a separate fixed-resolution graphical display canvas.

Scroll the mouse wheel to cycle block types; in chip scale it cycles particle gates.

The block palette is now paged and scrollable: use its scrollbar, hover over the options area and scroll, or use `Q`/`E`. The quantum set includes Qubit, Photon, Electron, Positron, Muon, Neutrino, Quark, Gluon, Boson, Anyon, Exciton, and Polariton blocks. The chip-scale gate list also includes Hadamard, CNOT, Phase, T, SWAP, Toffoli, Measure, Bell, Controlled Phase, sqrt-SWAP, iSWAP, Fredkin, Parity, Weak Measure, Anyon Braid, Magic State, Teleport, Dephase, and QFT gates. Each new gate shows its particle carriers, fabrication recipe, and equation in the chip HUD.

## Saving

Press `Ctrl+S` during play to save the current system to `savegame.json` beside the Python file. This includes placed voxels, layers, gates, bus ports, chip results, and player UI state. Press `Ctrl+Shift+S` for a Save As dialog. Load the save exactly like an example:

```bash
python3 lithography_voxel_lab.py --system savegame.json
```

The material palette also includes quantum quasiparticles such as **phonon**, magnon, plasmon, hole, Cooper pair, Majorana, fluxon, ion, and dark photon. It also includes dedicated **Noise Source**, **Observer**, **Bayesian**, and **Consensus** materials. The neural example's **BAYESIAN OBSERVATION ENGINE** chip maps to `maze_flask.py`: its physical stages represent `observe`, `upward_pass`, `downward_pass`, `deep_obs`, and `plan_path`, and its screen output reports the posterior/deep-observation stream. The **MATERIAL GATE PRESET** dropdown above the build palette stamps complete multi-block assemblies such as CMOS Inverter, NAND Cell, Quantum H, CNOT Tile, Bell Pair, Ion Trap, Superconducting, and Photonic Mux. Choose `FREE BUILD` to return to single-block placement.

Directional blocks now show restrained route arrows. Press `R` to rotate the placement direction through east, south, west, and north. Active conductive/quantum blocks pulse and glow with the live bus; inactive blocks remain dim with a static direction marker. The live packet is the primary notifier: its arrowhead follows the current bus segment and updates direction on every hop, including corners and diagonal transitions. Presets stamp every block with the selected orientation, and saved JSON preserves those directions. JSON now writes readable voxel records with `direction` plus numeric `rotation` degrees (`0=east`, `90=south`, `180=west`, `270=north`); legacy five-item voxel arrays and direction strings still load. Chip `initial_gates` and saved `chip_logic.gates` accept the same `direction`/`rotation` fields, and gate arrows are visible in chip scale.

## Dual-computer lithography mode

The dual-computer examples are two fabricated virtual servers, not a software-only socket demo. Each server owns an explicit `chip_codes` bank, and the program is synthesized separately against that bank. A missing gate on either fabricated bank blocks execution with `SYNTH WAIT`. Each server has two cores, so the shared program runs across four lanes with separate registers and program counters.

The servers communicate through a physical in-game FireWire lithography route. The route is stored on layer 2 as conductive voxel cells; the synthesized gate carrier travels over that route and `INPUT` reads the delivered carrier. Removing one route voxel immediately changes the machine to `FAB WAIT`.

A JSON system enables it with:

```json
"cluster": {
  "enabled": true,
  "shared_memory": true,
  "link": {
    "type": "firewire",
    "name": "FIRELINK-A/B",
    "layer": 2,
    "latency_ticks": 2,
    "cells": [[0, 6], [1, 6], [2, 6]]
  },
  "computers": [
    {"name": "FAB-A", "role": "primary", "cores": 2, "chip_codes": ["N-01", "N-03"]},
    {"name": "FAB-B", "role": "replica", "cores": 2, "chip_codes": ["N-02", "N-04"]}
  ]
}
```

The live program strip reports the active fabricated server/chip, carrier values, FireWire hop, direction, latency, and transfer count. This remains an in-game lithography architecture; it does not access physical FireWire hardware on the host computer.

## Equation proposals

Open **File → Propose Equation to Chip…** or press `Ctrl+E`. Choose a chip, enter a name and expression, then select **PROPOSE TO CHIP**. The simulator evaluates ordinary numeric expressions in a restricted sample environment, reports the answer and elapsed milliseconds in a popup, mirrors the report on the 512×512 output, and saves it in the system JSON under `equation_proposals`. Multiple statements are supported with semicolons or newlines, for example `m = 2; x = 0.75; y = m * x`; `let`, `var`, and `const` prefixes are accepted. Quantum/state notation is retained as a clearly labelled symbolic result.

## Programming the computer

Open **File → Edit / Run LITHO-ISA Program…** or press `Ctrl+P`. The editor accepts source directly, with `RUN`, `STEP`, `STOP`, `RESET`, `.litho` load/save, and an **instructions/frame** speed control. The runtime executes many instructions per rendered frame, so increasing speed accelerates the computer without multiplying canvas redraw work.

Execution is physically gated by the fabricated board. The compiler then synthesizes each instruction into a gate-stage netlist. Arithmetic and control instructions lower into AND/OR/NOT stages; quantum instructions require their matching fabricated particle gate, such as CPHASE → CONTROLLED PHASE or QFT → QFT. Each stage records its chip, gate slots, route latency, and carrier value in the live program status and saved JSON.

The default and bundled computer examples boot with commissioned lithography. For a custom or unbuilt system, RUN and STEP remain in FAB WAIT until every chip's layer-one pattern is placed, its particle gates and bus ports are complete, each chip has been exposed with L, and every routed bus cell contains a conductor. Removing a required chip material, gate, port, or trace while the computer is running stops execution on the next tick. The program strip reports FAB READY or FAB WAIT, and active blocks/packet arrows only animate while the fabricated computer is executing.

The core instruction set is: `CONST`, `MOV`, `ADD`, `SUB`, `MUL`, `DIV`, `CLAMP`, `INC`, `DEC`, `NOISE`, `OBSERVE`, `BAYES`, `HADAMARD`, `MEASURE`, `SEND`, `PRINT`, `WAIT`, `JMP`, `JNZ`, `JZ`, and `HALT`. The invented quantum operations are `CPHASE`, `SQRTSWAP`, `ISWAP`, `FREDKIN`, `PARITY`, `WEAKMEASURE`, `BRAID`, `MAGICSTATE`, `TELEPORT`, `DEPHASE`, and `QFT`. Lines beginning with `;` or `#` are comments. Registers are `R0` through `R15`.

### LITHO-8 byte computer

The `8bit_computer.json` system runs a deterministic 8-bit CPU mode. It has sixteen 8-bit registers, 256 bytes of addressable memory, an 8-bit stack pointer, `Z/N/C/V` flags, wrapping arithmetic, subroutine stack flow, and byte ports. Use `IMM8`/`MOV8`, `LOAD8`/`STORE8`, `ADD8`, `SUB8`, `AND8`, `OR8`, `XOR8`, `NOT8`, `INC8`, `DEC8`, `SHL8`, `SHR8`, `CMP8`, `PUSH8`, `POP8`, `IN8`, `OUT8`, `JZ8`, `JNZ8`, `JC8`, `JNC8`, `CALL`, and `RET`. Numeric constants accept decimal, hexadecimal (`0x2A`), binary (`0b101010`), or octal notation. Port `0` is connected to the graphical screen/bus output; `OUT8 0 R0` displays the byte as both hexadecimal and decimal.

### Turing-machine computer

The `turing_machine.json` system runs a deterministic single-tape Turing machine. Its JSON `program.turing` section defines the blank symbol, tape, head position, start/accept/reject states, and transition table. Each transition reads one symbol, writes one symbol, moves `L`, `R`, or `N`, and selects the next state. `Ctrl+P` opens the same RUN/STEP/STOP/RESET console; the 512×512 output shows the current tape window, head, state, step count, and accept/reject result.

### SOC-32 equation and graphics workstation

The soc_workstation.json example provides 32 registers, 64K of addressable memory, safe in-program EVAL equations, and a 512x512 drawing surface. Use LOAD32 and STORE32 for wide memory addresses, then CLEAR, PIXEL/PLOT, LINE, RECT, and SHOW to generate graphics from code. The program console's ARCHITECTURE dropdown lets you switch directly between LITHO-ISA, LITHO-8, SOC-32, and TURING examples.

A transition has this shape:

```json
{"state": "q0", "read": "1", "write": "1", "move": "R", "next": "q0"}
```

Example:

```text
CONST R0 250
CONST R1 10
ADD8 R2 R0 R1    ; R2 = 0x04, C flag set
STORE8 0x20 R2
OUT8 0 R2
```

A JSON system can provide the program directly:

```json
"program": {
  "language": "LITHO-ISA",
  "auto_start": true,
  "speed": 32,
  "source": "CONST R0 0\nHADAMARD R1 R0\nSEND R1\nPRINT \"Q\" R1"
}
```

`SEND` drives the program value into the live bus/screen telemetry, and `PRINT` appears in the program strip above the graphical output panel. The quantum example includes a running program using `HADAMARD`, `CPHASE`, `WEAKMEASURE`, and noise before sending its result to `Q-BUS`. The parallel example adds `LANE R0`: the same source runs on all four workers, but `R0` becomes lane `0`, `1`, `2`, or `3`, allowing each worker to calculate a separate slice before using `SEND`/`INPUT` across the shared link.

## Quantum fabrication

The new quantum gates are invented process recipes rather than claims about a physical manufacturing flow. Each recipe combines the particle materials already in the palette with a lithographic structure: waveguides, phase rails, resonators, topological braid tracks, zero-mode islands, or feed-forward vias. In chip scale, scroll the **PARTICLE GATES** bar to select a gate; the `Q-FAB` line shows its particles, process idea, and equation. The **MATERIAL GATE PRESET** dropdown stamps the corresponding material assembly on the infinite board.

Examples include `CONTROLLED PHASE` (photon + fluxon junction), `SQRT SWAP` (exciton + phonon bridge), `iSWAP` (electron + hole phase rail), `ANYON BRAID` (anyon + Majorana tracks), `WEAK MEASURE` (photon + phonon resonator), `MAGIC STATE` (Majorana zero-mode island), `TELEPORT` (Bell source plus feed-forward via), and `QFT` (polariton/plasmon phase stack).

## Parallel SIMD example

[parallel_system.json](/home/jdaj/Downloads/lithography_voxel_lab/parallel_system.json) is a third default system option. It has four SIMD lithography fields, a three-layer crossbar, a reduction chip, and a screen-output chip. `PARA-SERVER-A` and `PARA-SERVER-B` each contribute two cores. The shared program calculates a lane-specific value, exchanges it through `PARA-FIRELINK-A/B`, and displays the lane result in the live monitor.

## Performance

The renderer uses a separate fast input/simulation tick and a throttled canvas composition pass. The world redraws every other tick, while the sidebar graph refreshes less often. Movement is elapsed-time based and key auto-repeat is ignored, so slow frames no longer build a movement queue.

## Experimental quantum computers

Three additional systems use the invented quantum gates as complete computer designs:

- [experimental_topological.json](/home/jdaj/Downloads/lithography_voxel_lab/experimental_topological.json) — Majorana zero-mode islands, anyon braid tracks, parity readout, and magic-state output.
- [experimental_photonic.json](/home/jdaj/Downloads/lithography_voxel_lab/experimental_photonic.json) — photon/polariton waveguides, controlled phase, iSWAP, QFT, and teleportation.
- [experimental_hybrid.json](/home/jdaj/Downloads/lithography_voxel_lab/experimental_hybrid.json) — superconducting Cooper-pair cells, anyon control, dephasing/noise lab, and hybrid output.

Load them from **File → Experimental Computers**. Each system has its own lithography fields, chip queue, equations, four-core shared program, and FireWire-style link.
