"""Lithography Voxel Lab.

A small, dependency-free prototype for a voxel lithography game.  The player
is an engineer represented as a particle inside a chip fabrication lab.  Move
around the isometric board, place and remove process materials, finish the
stencil patterns, and watch the bus monitor react in real time.

Run with:
    python3 lithography_voxel_lab.py

The --self-test flag exercises the board/circuit model without opening a UI.
"""

from __future__ import annotations

import json
import math
import random
import shlex
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


GridCell = Tuple[int, int]
Voxel = Tuple[int, int, int]


@dataclass(frozen=True)
class Material:
    key: str
    label: str
    short: str
    top: str
    left: str
    right: str
    glow: str
    help_text: str


MATERIALS: Dict[str, Material] = {
    "silicon": Material(
        "silicon", "SILICON", "SI", "#768c99", "#465763", "#536a77", "#a8e9f3", "wafer / active layer"
    ),
    "copper": Material(
        "copper", "COPPER", "CU", "#e6a044", "#8f512d", "#b76d32", "#ffd185", "bus trace / conductor"
    ),
    "resist": Material(
        "resist", "RESIST", "PR", "#9b407f", "#5b225d", "#742e70", "#eb72bd", "photoresist / mask bed"
    ),
    "mask": Material(
        "mask", "MASK", "MK", "#34b9bf", "#176c7a", "#258d99", "#76eff4", "exposure stencil"
    ),
    "dielectric": Material(
        "dielectric", "DIELECTRIC", "DX", "#4e6bd1", "#293878", "#384a9c", "#94a9ff", "insulating oxide"
    ),
    "gold": Material(
        "gold", "GOLD", "AU", "#f4d35e", "#9a7223", "#c19a2d", "#fff0a2", "bond / contact metal"
    ),
    "n_type": Material(
        "n_type", "N-TYPE", "N+", "#d26a54", "#71352f", "#98483c", "#ffad97", "electron dopant"
    ),
    "p_type": Material(
        "p_type", "P-TYPE", "P+", "#b15be0", "#5e2c82", "#7e3da7", "#e3a8ff", "hole dopant"
    ),
    "via": Material(
        "via", "VIA", "V", "#71eef0", "#1d6978", "#2d9ba5", "#a6ffff", "vertical interconnect"
    ),
    "pcb": Material(
        "pcb", "PCB", "PCB", "#1d5548", "#12382f", "#164238", "#3ad9b9", "board substrate"
    ),
    "power": Material(
        "power", "POWER", "PWR", "#ed5663", "#7b2937", "#a63847", "#ff9da6", "power rail"
    ),
    "ground": Material(
        "ground", "GROUND", "GND", "#65727a", "#343d42", "#465158", "#b8c8ce", "ground return"
    ),
    "clock": Material(
        "clock", "CLOCK", "CLK", "#ef8c4f", "#783c2a", "#a65535", "#ffc39b", "timing rail"
    ),
    "signal": Material(
        "signal", "SIGNAL", "SIG", "#4de0a2", "#1b6a54", "#2c9672", "#a0ffd3", "data lane"
    ),
    "noise_source": Material(
        "noise_source", "NOISE SOURCE", "Nσ", "#ff5f91", "#7d294d", "#a63c66", "#ffc1d5", "programmatic Gaussian noise injector"
    ),
    "observer": Material(
        "observer", "OBSERVER", "OBS", "#5ddcff", "#236b87", "#3591ad", "#b8f4ff", "deep observation sampler"
    ),
    "bayes": Material(
        "bayes", "BAYESIAN", "BY", "#b58cff", "#5a3c90", "#7954b8", "#e2d3ff", "posterior belief fusion"
    ),
    "consensus": Material(
        "consensus", "CONSENSUS", "CS", "#72e0a0", "#2b7952", "#3c9b6b", "#c6ffdb", "downward observer consensus"
    ),
    "transistor": Material(
        "transistor", "TRANSISTOR", "TR", "#e28bdf", "#71366f", "#984a94", "#ffd4f8", "active device"
    ),
    "quantum": Material(
        "quantum", "QUANTUM", "Q", "#82a7ff", "#3b4e90", "#536bb9", "#c8d7ff", "particle channel"
    ),
    "qubit": Material(
        "qubit", "QUBIT", "QB", "#a678ff", "#4e3284", "#6c43ad", "#d8c2ff", "quantum bit"
    ),
    "photon": Material(
        "photon", "PHOTON", "PH", "#ffe76b", "#9c8126", "#c0a234", "#fff5b4", "light particle"
    ),
    "electron": Material(
        "electron", "ELECTRON", "E-", "#63d9ff", "#246b8b", "#388eaf", "#b2efff", "matter particle"
    ),
    "positron": Material(
        "positron", "POSITRON", "E+", "#ff8bba", "#843e61", "#ad527e", "#ffc4dd", "antimatter particle"
    ),
    "muon": Material(
        "muon", "MUON", "MU", "#7cf0c5", "#28755e", "#3a9a7b", "#bbffe7", "lepton carrier"
    ),
    "neutrino": Material(
        "neutrino", "NEUTRINO", "NU", "#b7f58c", "#5d813e", "#7aa953", "#dcffc1", "weak particle"
    ),
    "quark": Material(
        "quark", "QUARK", "QR", "#ff9c67", "#8e4b2f", "#b9623d", "#ffd0af", "color charge"
    ),
    "gluon": Material(
        "gluon", "GLUON", "GL", "#f15b9f", "#7e2d51", "#a73e6d", "#ffc0dc", "force carrier"
    ),
    "boson": Material(
        "boson", "BOSON", "BO", "#b98cff", "#5d3b91", "#7b52b5", "#e0ccff", "field excitation"
    ),
    "anyon": Material(
        "anyon", "ANYON", "AN", "#56e6dc", "#206b6b", "#328f8a", "#b7fffa", "topological carrier"
    ),
    "exciton": Material(
        "exciton", "EXCITON", "EX", "#f2a1ff", "#7d4a8b", "#a565b0", "#ffd0ff", "bound pair"
    ),
    "polariton": Material(
        "polariton", "POLARITON", "PO", "#84baff", "#3d6095", "#557dbb", "#c1dcff", "light-matter mode"
    ),
    "phonon": Material(
        "phonon", "PHONON", "PN", "#ffbf69", "#8e5b2b", "#b87738", "#ffe0a6", "lattice vibration"
    ),
    "magnon": Material(
        "magnon", "MAGNON", "MG", "#7af2e8", "#27736f", "#3a9b94", "#c3fffa", "spin wave"
    ),
    "plasmon": Material(
        "plasmon", "PLASMON", "PL", "#ff6f91", "#843146", "#ac405c", "#ffc0cc", "charge oscillation"
    ),
    "hole": Material(
        "hole", "HOLE", "HO", "#d89aff", "#6c3b86", "#9253ad", "#f0c8ff", "positive carrier"
    ),
    "cooper_pair": Material(
        "cooper_pair", "COOPER PAIR", "CP", "#70c7ff", "#315f93", "#457eb9", "#c5e7ff", "paired electrons"
    ),
    "majorana": Material(
        "majorana", "MAJORANA", "MZ", "#b6ff8d", "#5b853e", "#7dab54", "#e1ffc7", "zero mode"
    ),
    "fluxon": Material(
        "fluxon", "FLUXON", "FX", "#f98dff", "#7b3d83", "#a953ad", "#ffd0ff", "flux quantum"
    ),
    "ion": Material(
        "ion", "ION", "IO", "#ffdb67", "#967b27", "#b99932", "#fff2b0", "trapped particle"
    ),
    "dark_photon": Material(
        "dark_photon", "DARK PHOTON", "DP", "#667cff", "#303e8e", "#475ab5", "#bec7ff", "hidden-sector carrier"
    ),
}

MATERIAL_ORDER = [
    "silicon", "copper", "resist", "mask", "dielectric", "gold", "n_type", "p_type", "via",
    "pcb", "power", "ground", "clock", "signal", "noise_source", "observer", "bayes", "consensus", "transistor", "quantum",
    "qubit", "photon", "electron", "positron", "muon", "neutrino", "quark", "gluon",
    "boson", "anyon", "exciton", "polariton",
    "phonon", "magnon", "plasmon", "hole", "cooper_pair", "majorana", "fluxon", "ion", "dark_photon",
]

DIRECTIONS = ["east", "south", "west", "north"]
DIRECTIONAL_BLOCKS = set(MATERIAL_ORDER) - {"pcb", "dielectric", "resist", "mask", "ground"}
ACTIVE_BLOCKS = DIRECTIONAL_BLOCKS - {"gold", "silicon", "n_type", "p_type"}


@dataclass(frozen=True)
class GateSpec:
    key: str
    label: str
    symbol: str
    color: str
    help_text: str
    particle: str = "mixed particle"
    fabrication: str = "pattern, etch, and connect the active layer"
    equation: str = ""


GATE_TYPES: Dict[str, GateSpec] = {
    "source": GateSpec("source", "SOURCE", "IN", "#f6b85f", "particle input"),
    "and": GateSpec("and", "AND", "&", "#69d7e6", "coincidence"),
    "or": GateSpec("or", "OR", "≥1", "#c88bff", "merge"),
    "not": GateSpec("not", "NOT", "!", "#72f0ad", "invert"),
    "hadamard": GateSpec("hadamard", "HADAMARD", "H", "#b98cff", "superposition"),
    "cnot": GateSpec("cnot", "CNOT", "CX", "#56e6dc", "controlled flip"),
    "phase": GateSpec("phase", "PHASE", "S", "#ff9c67", "phase shift"),
    "t_gate": GateSpec("t_gate", "T GATE", "T", "#f2a1ff", "pi/8 rotation"),
    "swap": GateSpec("swap", "SWAP", "SW", "#84baff", "exchange states"),
    "toffoli": GateSpec("toffoli", "TOFFOLI", "CCX", "#ffe76b", "double control"),
    "measure": GateSpec("measure", "MEASURE", "M", "#ff8bba", "read qubit"),
    "bell": GateSpec("bell", "BELL", "B", "#7cf0c5", "entangle pair", "photon + cooper pair", "cross-couple two qubit wells, then expose a shared photon rail", "|Φ+⟩ = (|00⟩ + |11⟩)/√2"),
    "controlled_phase": GateSpec("controlled_phase", "CONTROLLED PHASE", "CP", "#ff6f91", "conditional phase", "photon + fluxon", "pattern a photon waveguide over a flux-biased Josephson junction", "|11⟩ → e^(iφ)|11⟩"),
    "sqrt_swap": GateSpec("sqrt_swap", "SQRT SWAP", "√SW", "#84baff", "half exchange", "exciton + phonon", "etch two exciton wells and join them with a phonon-coupled bridge", "(√SWAP)^2 = SWAP"),
    "iswap": GateSpec("iswap", "iSWAP", "iSW", "#63d9ff", "phase exchange", "electron + hole", "cross electron and hole channels under a phase-shift metal mask", "|01⟩ → i|10⟩"),
    "fredkin": GateSpec("fredkin", "FREDKIN", "CSW", "#ffe76b", "controlled swap", "photon + anyon", "lithograph one control interferometer beside two braided data lanes", "|c,a,b⟩ → |c,b,a⟩ when c=1"),
    "parity": GateSpec("parity", "PARITY", "P", "#b7f58c", "parity check", "electron + positron", "split opposite-carrier contacts into a coincidence detector", "P = (-1)^(n₁+n₂)"),
    "weak_measure": GateSpec("weak_measure", "WEAK MEASURE", "WM", "#ffbf69", "low-disturbance read", "photon + phonon", "use a resonator tap and phonon probe instead of a full absorber", "p(m|ψ) ∝ 1 + ε⟨M⟩"),
    "braid": GateSpec("braid", "ANYON BRAID", "BR", "#56e6dc", "topological exchange", "anyon + Majorana", "write crossed topological tracks with vias at the braid endpoints", "UᵢUⱼUᵢ = UⱼUᵢUⱼ"),
    "magic_state": GateSpec("magic_state", "MAGIC STATE", "MS", "#d89aff", "non-Clifford seed", "Majorana + dark photon", "pattern a protected zero-mode island beside a hidden-sector bias line", "|A⟩ = T|+⟩"),
    "teleport": GateSpec("teleport", "TELEPORT", "TP", "#f2a1ff", "state transfer", "Bell photon + Cooper pair", "fabricate a Bell source, two readout taps, and a feed-forward via", "|ψ⟩₃ = XᵐZⁿ|ψ⟩"),
    "dephase": GateSpec("dephase", "DEPHASE", "DΦ", "#7af2e8", "noise channel", "phonon + plasmon", "couple a phonon bath to a plasmon rail through dielectric", "ρ → (1-p)ρ + pZρZ"),
    "qft": GateSpec("qft", "QFT", "QF", "#b98cff", "phase spectrum", "polariton + plasmon", "stack phase masks over a polariton waveguide and clock vias", "|x⟩ → 1/√N Σᵧ e^(2πixy/N)|y⟩"),
}

GATE_ORDER = [
    "source", "and", "or", "not", "hadamard", "cnot", "phase", "t_gate", "swap", "toffoli", "measure", "bell",
    "controlled_phase", "sqrt_swap", "iswap", "fredkin", "parity", "weak_measure", "braid", "magic_state", "teleport", "dephase", "qft",
]


@dataclass(frozen=True)
class GatePreset:
    key: str
    label: str
    tint: str
    help_text: str
    blocks: Tuple[Tuple[int, int, str], ...]


GATE_PRESETS: Dict[str, GatePreset] = {
    "cmos_inverter": GatePreset("cmos_inverter", "CMOS INVERTER", "#ffb85c", "N/P transistor gate", ((0, 0, "p_type"), (1, 0, "dielectric"), (2, 0, "n_type"), (0, 1, "gold"), (1, 1, "signal"), (2, 1, "gold"))),
    "nand_cell": GatePreset("nand_cell", "NAND CELL", "#69d7e6", "two-input material gate", ((0, 0, "p_type"), (1, 0, "p_type"), (2, 0, "dielectric"), (0, 1, "n_type"), (1, 1, "n_type"), (2, 1, "copper"))),
    "quantum_h": GatePreset("quantum_h", "QUANTUM H", "#b98cff", "Hadamard superposition", ((0, 0, "qubit"), (1, 0, "hadamard"), (2, 0, "qubit"), (1, 1, "photon"), (1, 2, "phonon"), (2, 1, "via"))),
    "cnot_tile": GatePreset("cnot_tile", "CNOT TILE", "#56e6dc", "controlled quantum flip", ((0, 0, "qubit"), (1, 0, "cnot"), (2, 0, "qubit"), (0, 1, "electron"), (1, 1, "signal"), (2, 1, "photon"), (1, 2, "via"))),
    "bell_pair": GatePreset("bell_pair", "BELL PAIR", "#7cf0c5", "entangled pair source", ((0, 0, "qubit"), (1, 0, "bell"), (2, 0, "qubit"), (0, 1, "photon"), (2, 1, "photon"), (1, 2, "cooper_pair"))),
    "ion_trap": GatePreset("ion_trap", "ION TRAP", "#ffe76b", "trapped-ion cell", ((0, 0, "ion"), (1, 0, "magnon"), (2, 0, "ion"), (0, 1, "gold"), (1, 1, "dielectric"), (2, 1, "gold"))),
    "superconducting": GatePreset("superconducting", "SUPERCONDUCTING", "#84baff", "flux / paired-electron cell", ((0, 0, "cooper_pair"), (1, 0, "fluxon"), (2, 0, "cooper_pair"), (0, 1, "phonon"), (1, 1, "majorana"), (2, 1, "via"))),
    "photonic_mux": GatePreset("photonic_mux", "PHOTONIC MUX", "#ff6f91", "photon-plasmon route", ((0, 0, "photon"), (1, 0, "plasmon"), (2, 0, "photon"), (1, 1, "polariton"), (0, 2, "gold"), (2, 2, "signal"))),
    "controlled_phase": GatePreset("controlled_phase", "CONTROLLED PHASE", "#ff6f91", "photon / fluxon junction", ((0, 0, "photon"), (1, 0, "fluxon"), (2, 0, "photon"), (1, 1, "dielectric"), (1, 2, "via"), (2, 2, "signal"))),
    "sqrt_swap": GatePreset("sqrt_swap", "SQRT SWAP CELL", "#84baff", "exciton / phonon bridge", ((0, 0, "exciton"), (1, 0, "phonon"), (2, 0, "exciton"), (0, 1, "qubit"), (2, 1, "qubit"), (1, 2, "dielectric"))),
    "iswap_bridge": GatePreset("iswap_bridge", "iSWAP BRIDGE", "#63d9ff", "electron / hole phase rail", ((0, 0, "electron"), (1, 0, "hole"), (2, 0, "electron"), (1, 1, "plasmon"), (0, 2, "gold"), (2, 2, "gold"))),
    "anyon_braid": GatePreset("anyon_braid", "ANYON BRAID", "#56e6dc", "crossed topological tracks", ((0, 0, "anyon"), (1, 0, "majorana"), (2, 0, "anyon"), (0, 1, "fluxon"), (2, 1, "fluxon"), (1, 2, "via"))),
    "weak_readout": GatePreset("weak_readout", "WEAK READOUT", "#ffbf69", "resonator probe", ((0, 0, "photon"), (1, 0, "phonon"), (2, 0, "photon"), (1, 1, "observer"), (0, 2, "dielectric"), (2, 2, "signal"))),
    "magic_island": GatePreset("magic_island", "MAGIC ISLAND", "#d89aff", "protected zero-mode seed", ((0, 0, "majorana"), (1, 0, "qubit"), (2, 0, "majorana"), (0, 1, "dark_photon"), (1, 1, "dielectric"), (2, 1, "via"))),
    "teleport_link": GatePreset("teleport_link", "TELEPORT LINK", "#f2a1ff", "Bell source and feed-forward", ((0, 0, "bell"), (1, 0, "photon"), (2, 0, "bell"), (0, 1, "cooper_pair"), (2, 1, "cooper_pair"), (1, 2, "via"))),
    "qft_stack": GatePreset("qft_stack", "QFT STACK", "#b98cff", "polariton phase spectrum", ((0, 0, "polariton"), (1, 0, "plasmon"), (2, 0, "polariton"), (1, 1, "clock"), (0, 2, "gold"), (2, 2, "gold"))),
}


@dataclass
class ChipSpec:
    name: str
    code: str
    anchor: GridCell
    pattern: Dict[GridCell, str]
    tint: str
    output: str
    face_slots: Dict[str, int]
    gate_target: int

    @property
    def cells(self) -> Iterable[GridCell]:
        return self.pattern.keys()

    @property
    def port_total(self) -> int:
        return sum(self.face_slots.values())


@dataclass
class ChipLogic:
    gates: Dict[GridCell, str]
    ports: Dict[str, List[bool]]

    @property
    def connected_ports(self) -> int:
        return sum(sum(side) for side in self.ports.values())


@dataclass
class ChipResult:
    matched: int = 0
    total: int = 0
    exposed: bool = False
    passed: bool = False

    @property
    def ratio(self) -> float:
        return self.matched / self.total if self.total else 0.0


CHIPS: List[ChipSpec] = [
    ChipSpec(
        "CPU CORE",
        "C-01",
        (3, 2),
        {(3, 2): "silicon", (4, 2): "copper", (3, 3): "copper", (4, 3): "silicon"},
        "#ffb85c",
        "instruction stream stable",
        {"north": 2, "east": 2, "south": 1, "west": 1},
        5,
    ),
    ChipSpec(
        "IO BRIDGE",
        "I-02",
        (7, 2),
        {(7, 2): "silicon", (8, 2): "resist", (7, 3): "copper", (8, 3): "silicon"},
        "#69d7e6",
        "peripheral lanes online",
        {"north": 1, "east": 3, "south": 1, "west": 1},
        5,
    ),
    ChipSpec(
        "MEM BANK",
        "M-03",
        (11, 2),
        {(11, 2): "silicon", (12, 2): "copper", (11, 3): "resist", (12, 3): "silicon"},
        "#c88bff",
        "address space mapped",
        {"north": 2, "east": 1, "south": 2, "west": 1},
        5,
    ),
    ChipSpec(
        "VECTOR DSP",
        "V-04",
        (6, 7),
        {(6, 7): "silicon", (7, 7): "copper", (6, 8): "copper", (7, 8): "resist"},
        "#72f0ad",
        "parallel lanes synchronized",
        {"north": 1, "east": 2, "south": 2, "west": 1},
        5,
    ),
]


DEFAULT_BUS_CELLS: List[GridCell] = [(x, 5) for x in range(2, 14)] + [(8, 6), (8, 7), (8, 8)]
DEFAULT_PROGRAM_SOURCE = """; LITHO-ISA live computer demo
; Registers are floating point values.  The loop performs a noisy Bayesian
; observation, publishes it to the bus, and prints the current result.
CONST R0 0.50
CONST R1 0.80
LOOP:
NOISE R2 0.08
BAYES R3 R0 R1
ADD R3 R2
CLAMP R3 0 1
SEND R3
PRINT \"POSTERIOR\" R3
WAIT 2
JMP LOOP
"""
SYSTEM_CONFIG: Dict[str, Any] = {
    "system": {
        "name": "AURORA FAB // WORKING COMPUTER",
        "bus_name": "AURORA-BUS",
        "clock_ghz": 2.4,
    },
    "board": {"width": 20, "height": 14},
    "bus": {
        "layers": {
            "1": {
                "path": [[x, 5] for x in range(1, 16)] + [[8, 6], [8, 7], [8, 8]],
                "starting_traces": [[x, 5] for x in range(1, 16)],
            },
            "2": {
                "path": [[8, 2], [8, 3], [8, 4], [8, 5], [8, 6], [8, 7], [8, 8]],
                "starting_traces": [[8, 4], [8, 5], [8, 6]],
            },
            "3": {
                "path": [[3, 3], [4, 3], [5, 3], [6, 3], [7, 3], [8, 3], [9, 3], [10, 3], [11, 3]],
                "starting_traces": [[6, 3], [7, 3], [8, 3]],
            },
        },
        "connections": [
            {"cell": [8, 5], "layers": [1, 2, 3], "material": "via"},
            {"cell": [3, 5], "layers": [1, 3], "material": "copper"},
            {"cell": [11, 3], "layers": [2, 3], "material": "copper"},
        ],
    },
    "lithography": {
        "fields": [
            {"name": "CPU MASK ARRAY", "origin": [1, 0], "size": [7, 4], "layer": 1, "pattern": "grid", "pitch": 2, "tint": "#55dce0", "bus_taps": [[3, 5]]},
            {"name": "MEMORY MASK ARRAY", "origin": [10, 0], "size": [8, 5], "layer": 1, "pattern": "crosshatch", "pitch": 2, "tint": "#c88bff", "bus_taps": [[11, 5]]},
            {"name": "QUANTUM CONTROL PLANE", "origin": [4, 7], "size": [8, 7], "layer": 2, "pattern": "checker", "pitch": 2, "tint": "#b98cff", "bus_taps": [[8, 6]]},
        ]
    },
    "output": {
        "screen_name": "SCREEN OUTPUT // AURORA COMPUTER",
        "idle_message": "AURORA COMPUTER RUNNING",
    },
    "infinite_supply": True,
    "boot_working": True,
    "cluster": {
        "enabled": True,
        "shared_memory": True,
        "link": {"type": "firewire", "name": "FIRELINK-A/B", "latency_ticks": 2, "bandwidth": "shared-bus"},
        "computers": [
            {"name": "FAB-A", "role": "primary", "cores": 2},
            {"name": "FAB-B", "role": "replica", "cores": 2},
        ],
    },
    "program": {
        "language": "LITHO-ISA",
        "auto_start": True,
        "speed": 24,
        "source": DEFAULT_PROGRAM_SOURCE,
    },
}


def _cell(value: Any, label: str) -> GridCell:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{label} must be [x, y]")
    return int(value[0]), int(value[1])


def _face_slots(value: Any) -> Dict[str, int]:
    defaults = {"north": 1, "east": 1, "south": 1, "west": 1}
    if value is None:
        return defaults
    if not isinstance(value, dict):
        raise ValueError("face_slots must be an object")
    for face, count in value.items():
        if face not in defaults:
            raise ValueError(f"unknown chip face: {face}")
        defaults[face] = max(0, int(count))
    return defaults


def _pattern(raw: Any, anchor: GridCell, chip_label: str) -> Dict[GridCell, str]:
    """Read a pattern as relative JSON offsets or explicit cells."""
    result: Dict[GridCell, str] = {}
    if isinstance(raw, dict):
        for key, material in raw.items():
            try:
                dx, dy = (int(part.strip()) for part in str(key).split(",", 1))
            except (ValueError, TypeError):
                raise ValueError(f"{chip_label}.pattern keys must look like '0,1'") from None
            result[(anchor[0] + dx, anchor[1] + dy)] = str(material)
    elif isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                raise ValueError(f"{chip_label}.pattern list entries must be objects")
            material = str(item.get("material", ""))
            if "cell" in item:
                target = _cell(item["cell"], f"{chip_label}.pattern.cell")
            elif "offset" in item:
                offset = _cell(item["offset"], f"{chip_label}.pattern.offset")
                target = anchor[0] + offset[0], anchor[1] + offset[1]
            else:
                raise ValueError(f"{chip_label}.pattern entries need cell or offset")
            result[target] = material
    else:
        raise ValueError(f"{chip_label}.pattern must be an object or list")
    if not result:
        raise ValueError(f"{chip_label}.pattern cannot be empty")
    unknown = sorted(set(result.values()) - set(MATERIALS))
    if unknown:
        raise ValueError(f"{chip_label}.pattern has unknown materials: {', '.join(unknown)}")
    return result


def load_system_file(filename: str) -> Dict[str, Any]:
    """Load a system JSON and replace the built-in chip/bus definition."""
    global CHIPS, SYSTEM_CONFIG
    source = Path(filename)
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("system JSON must contain an object")
    raw_chips = data.get("chips")
    if not isinstance(raw_chips, list) or not raw_chips:
        raise ValueError("system JSON needs a non-empty chips array")
    parsed: List[ChipSpec] = []
    for index, raw in enumerate(raw_chips, 1):
        if not isinstance(raw, dict):
            raise ValueError(f"chips[{index}] must be an object")
        name = str(raw.get("name", f"CHIP {index}"))
        code = str(raw.get("code", f"C-{index:02d}"))
        anchor = _cell(raw.get("anchor", [2 + index * 2, 2]), f"{code}.anchor")
        parsed.append(ChipSpec(
            name=name,
            code=code,
            anchor=anchor,
            pattern=_pattern(raw.get("pattern"), anchor, code),
            tint=str(raw.get("tint", "#69d7e6")),
            output=str(raw.get("output", "output lane online")),
            face_slots=_face_slots(raw.get("face_slots", raw.get("connections"))),
            gate_target=max(1, int(raw.get("gate_target", 5))),
        ))
    duplicate_codes = {chip.code for chip in parsed if [item.code for item in parsed].count(chip.code) > 1}
    if duplicate_codes:
        raise ValueError(f"duplicate chip codes: {', '.join(sorted(duplicate_codes))}")
    SYSTEM_CONFIG = data
    CHIPS = parsed
    return data



class LabModel:
    """State and rules that can run independently of Tkinter."""

    width = 16
    height = 11

    def __init__(self, system_config: Optional[Dict[str, Any]] = None) -> None:
        self.config = system_config or SYSTEM_CONFIG
        system_meta = self.config.get("system", {})
        board_meta = self.config.get("board", system_meta.get("board", {}))
        bus_meta = self.config.get("bus", {})
        self.system_name = str(system_meta.get("name", "LITHOGRAPHY SYSTEM"))
        self.bus_name = str(bus_meta.get("name", system_meta.get("bus_name", "BUS-0")))
        self.base_clock_ghz = float(system_meta.get("clock_ghz", 1.0))
        self.width = max(8, int(board_meta.get("width", 16)))
        self.height = max(8, int(board_meta.get("height", 11)))
        self.layer_bus_cells: Dict[int, List[GridCell]] = {}
        self.layer_starting_traces: Dict[int, List[GridCell]] = {}
        raw_layers = bus_meta.get("layers", {})
        if isinstance(raw_layers, dict):
            for raw_layer, raw_layer_config in raw_layers.items():
                layer = max(1, int(raw_layer))
                layer_config = raw_layer_config if isinstance(raw_layer_config, dict) else {"path": raw_layer_config}
                self.layer_bus_cells[layer] = [_cell(item, f"bus.layers.{layer}.path") for item in layer_config.get("path", [])]
                self.layer_starting_traces[layer] = [_cell(item, f"bus.layers.{layer}.starting_traces") for item in layer_config.get("starting_traces", [])]
        legacy_path = [_cell(item, "bus.path") for item in bus_meta.get("path", DEFAULT_BUS_CELLS)]
        if not self.layer_bus_cells:
            self.layer_bus_cells[1] = legacy_path
            self.layer_starting_traces[1] = [_cell(item, "bus.starting_traces") for item in bus_meta.get("starting_traces", [])]
        self.bus_cells = self.layer_bus_cells.get(1, legacy_path)
        self.starting_traces = self.layer_starting_traces.get(1, [])
        connection_layers = [int(layer) for item in bus_meta.get("connections", []) if isinstance(item, dict) for layer in item.get("layers", [1])]
        self.max_layer = max([1, *self.layer_bus_cells.keys(), *connection_layers])
        self.output_config = self.config.get("output", {}) if isinstance(self.config.get("output", {}), dict) else {}
        self.equations = self.config.get("equations", []) if isinstance(self.config.get("equations", []), list) else []
        cluster_config = self.config.get("cluster", {}) if isinstance(self.config.get("cluster", {}), dict) else {}
        link_config = cluster_config.get("link", {}) if isinstance(cluster_config.get("link", {}), dict) else {}
        self.cluster_enabled = bool(cluster_config.get("enabled", False))
        self.cluster_link_type = str(link_config.get("type", "firewire"))
        self.cluster_link_name = str(link_config.get("name", "FIRELINK-0"))
        self.cluster_latency_ticks = min(32, max(0, int(link_config.get("latency_ticks", 2))))
        self.cluster_shared_memory = bool(cluster_config.get("shared_memory", True))
        self.cluster_worker_specs: List[Tuple[str, str, int]] = []
        raw_computers = cluster_config.get("computers", [])
        if self.cluster_enabled and isinstance(raw_computers, list):
            for computer_index, raw_computer in enumerate(raw_computers[:2], 1):
                if not isinstance(raw_computer, dict):
                    continue
                computer_name = str(raw_computer.get("name", f"COMPUTER-{computer_index}"))
                core_count = min(8, max(1, int(raw_computer.get("cores", 2))))
                for core_index in range(core_count):
                    self.cluster_worker_specs.append((computer_name, computer_name, core_index))
        if not self.cluster_worker_specs:
            self.cluster_enabled = False
            self.cluster_worker_specs = [("LOCAL", "LOCAL", 0)]
        self.cluster_tick = 0
        self.cluster_transfers = 0
        self.cluster_link_queue: List[Dict[str, Any]] = []
        self.cluster_shared_bus_value = 0.0
        self.cluster_last_transfer = "IDLE"
        self.infinite_supply = bool(self.config.get("infinite_supply", True))
        self.lithography_regions = self._load_lithography_regions(self.config.get("lithography", {}))
        self.lithography_cells_total = sum(int(region["size"][0]) * int(region["size"][1]) for region in self.lithography_regions)
        self.voxels: Dict[Voxel, str] = {}
        self.voxel_directions: Dict[Voxel, str] = {}
        self._top_cache: Dict[GridCell, Optional[int]] = {}
        default_inventory = {material: 999999 for material in MATERIAL_ORDER}
        configured_inventory = self.config.get("inventory", {})
        if isinstance(configured_inventory, dict):
            for material, amount in configured_inventory.items():
                if material in default_inventory:
                    default_inventory[material] = max(0, int(amount))
        self.inventory: Dict[str, int] = default_inventory
        self.gate_inventory: Dict[str, int] = {gate: 999999 for gate in GATE_ORDER}
        self.results: Dict[str, ChipResult] = {chip.code: ChipResult(total=len(chip.pattern)) for chip in CHIPS}
        self.chip_logic: Dict[str, ChipLogic] = {
            chip.code: ChipLogic(
                gates={},
                ports={face: [False] * count for face, count in chip.face_slots.items()},
            )
            for chip in CHIPS
        }
        self._seed_configured_logic()
        self.operations = 0
        self.completed_runs = 0
        self.last_event = "FAB READY // load a pattern"
        self.program_source = ""
        self.program_instructions: List[Tuple[str, List[str], int, str]] = []
        self.program_labels: Dict[str, int] = {}
        self.program_pc = 0
        self.program_registers: Dict[str, float] = {f"R{index}": 0.0 for index in range(16)}
        self.program_running = False
        self.program_halted = False
        self.program_wait = 0
        self.program_speed = 24
        self.program_clock = 0
        self.program_bus_value = 0.0
        self.program_output: List[str] = []
        self.program_error = ""
        self.program_input_value = 0.0
        self.program_workers: List[Dict[str, Any]] = []
        self.program_active_worker = 0
        self._build_lab()
        if bool(self.config.get("boot_working", False)):
            self._boot_working_computer()
        self._restore_state(self.config.get("state", {}))
        program_config = self.config.get("program", {})
        if not isinstance(program_config, dict):
            program_config = {}
        self.program_speed = min(512, max(1, int(program_config.get("speed", 24))))
        source = str(program_config.get("source", DEFAULT_PROGRAM_SOURCE))
        self.load_program(source, announce=False)
        if bool(program_config.get("auto_start", bool(self.config.get("boot_working", False)))):
            self.start_program(announce=False)

    def _load_lithography_regions(self, raw_config: Any) -> List[Dict[str, Any]]:
        raw_fields = raw_config.get("fields", []) if isinstance(raw_config, dict) else []
        regions: List[Dict[str, Any]] = []
        for index, raw in enumerate(raw_fields, 1):
            if not isinstance(raw, dict):
                continue
            origin = _cell(raw.get("origin", [0, 0]), f"lithography.fields[{index}].origin")
            size = raw.get("size", [8, 8])
            if not isinstance(size, list) or len(size) != 2:
                raise ValueError(f"lithography.fields[{index}].size must be [width, height]")
            regions.append({
                "name": str(raw.get("name", f"LITHO FIELD {index}")),
                "origin": origin,
                "size": (max(1, int(size[0])), max(1, int(size[1]))),
                "layer": max(1, int(raw.get("layer", 1))),
                "pattern": str(raw.get("pattern", "crosshatch")),
                "pitch": max(1, int(raw.get("pitch", 2))),
                "tint": str(raw.get("tint", "#55dce0")),
                "bus_taps": [_cell(item, "lithography.bus_taps") for item in raw.get("bus_taps", [])],
            })
        return regions

    def _seed_configured_logic(self) -> None:
        for raw_chip in self.config.get("chips", []):
            if not isinstance(raw_chip, dict):
                continue
            code = str(raw_chip.get("code", ""))
            logic = self.chip_logic.get(code)
            if logic is None:
                continue
            for raw_gate in raw_chip.get("initial_gates", []):
                if not isinstance(raw_gate, dict):
                    continue
                slot = raw_gate.get("slot", raw_gate.get("cell"))
                gate = str(raw_gate.get("gate", ""))
                if isinstance(slot, list) and len(slot) == 2 and gate in GATE_TYPES:
                    cell = int(slot[0]), int(slot[1])
                    if 0 <= cell[0] < 9 and 0 <= cell[1] < 6:
                        logic.gates[cell] = gate
                        if not self.infinite_supply:
                            self.gate_inventory[gate] = max(0, self.gate_inventory[gate] - 1)
            for raw_port in raw_chip.get("connected_ports", []):
                if isinstance(raw_port, list) and len(raw_port) == 2:
                    face, index = str(raw_port[0]), int(raw_port[1])
                    if face in logic.ports and 0 <= index < len(logic.ports[face]):
                        logic.ports[face][index] = True

    def _build_lab(self) -> None:
        # The configured board is a starting area only. The playable space is
        # infinite; the renderer generates the visible tiles around the player.
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                self.voxels[(x, y, 0)] = "pcb"

        for layer, path_cells in self.layer_bus_cells.items():
            starters = self.layer_starting_traces.get(layer, [])
            if layer == 1 and not starters:
                starters = self.bus_cells[: min(6, len(self.bus_cells))]
            for index, (x, y) in enumerate(starters):
                voxel = (x, y, layer)
                self.voxels[voxel] = "copper"
                self.voxel_directions[voxel] = "east"

        # Explicit vertical connections are materialized at every listed layer.
        for raw_connection in self.config.get("bus", {}).get("connections", []):
            if not isinstance(raw_connection, dict):
                continue
            x, y = _cell(raw_connection.get("cell", [0, 0]), "bus.connections.cell")
            material = str(raw_connection.get("material", "copper"))
            if material not in MATERIALS:
                continue
            for layer in raw_connection.get("layers", [1]):
                z = max(1, int(layer))
                voxel = (x, y, z)
                self.voxels[voxel] = material
                self.voxel_directions[voxel] = "up" if material == "via" else "east"
                self.max_layer = max(self.max_layer, z)

        # Keep a readable perimeter around the generated starting area without
        # treating it as a hard boundary.
        max_x, max_y = self.width - 2, self.height - 2
        for x in range(1, self.width - 1):
            self.voxels[(x, 1, 1)] = "copper"
            self.voxels[(x, max_y, 1)] = "copper"
        for y in range(1, self.height - 1):
            self.voxels[(1, y, 1)] = "copper"
            self.voxels[(max_x, y, 1)] = "copper"
        scanner_cells = [(max_x, max_y - 2), (max_x, max_y - 1), (max_x - 1, max_y - 1)]
        for cell in scanner_cells:
            if self.valid_cell(cell):
                self.voxels[(cell[0], cell[1], 1)] = "mask"

    def _boot_working_computer(self) -> None:
        """Populate the built-in demo as a live computer on first launch."""
        for chip in CHIPS:
            for (x, y), material in chip.pattern.items():
                voxel = (x, y, 1)
                self.voxels[voxel] = material
                self.voxel_directions[voxel] = "east"
                self._top_cache.pop((x, y), None)
            self.auto_complete_logic(chip)
            result = self.results[chip.code]
            result.matched = result.total
            result.exposed = True
            result.passed = True
        self.operations += sum(len(chip.pattern) + chip.gate_target + chip.port_total for chip in CHIPS)
        self.completed_runs = len(CHIPS)
        self.last_event = "BOOT PASS // default computer online // screen output streaming"

    def _new_program_worker(self, computer: str, name: str, core: int) -> Dict[str, Any]:
        return {
            "computer": computer,
            "name": name,
            "core": core,
            "pc": 0,
            "registers": {f"R{index}": 0.0 for index in range(16)},
            "running": False,
            "halted": False,
            "wait": 0,
            "clock": 0,
            "bus_value": 0.0,
            "input_value": 0.0,
            "output": [],
            "error": "",
        }

    def _save_active_program_worker(self) -> None:
        if not self.program_workers or not 0 <= self.program_active_worker < len(self.program_workers):
            return
        worker = self.program_workers[self.program_active_worker]
        worker.update({
            "pc": self.program_pc,
            "registers": dict(self.program_registers),
            "running": self.program_running,
            "halted": self.program_halted,
            "wait": self.program_wait,
            "clock": self.program_clock,
            "bus_value": self.program_bus_value,
            "input_value": self.program_input_value,
            "output": list(self.program_output),
            "error": self.program_error,
        })

    def _load_program_worker(self, index: int, save_current: bool = True) -> None:
        if not self.program_workers:
            return
        if save_current:
            self._save_active_program_worker()
        index = min(len(self.program_workers) - 1, max(0, index))
        worker = self.program_workers[index]
        self.program_active_worker = index
        self.program_pc = int(worker["pc"])
        self.program_registers = dict(worker["registers"])
        self.program_running = bool(worker["running"])
        self.program_halted = bool(worker["halted"])
        self.program_wait = int(worker["wait"])
        self.program_clock = int(worker["clock"])
        self.program_bus_value = float(worker["bus_value"])
        self.program_input_value = float(worker["input_value"])
        self.program_output = list(worker["output"])
        self.program_error = str(worker["error"])

    def _reset_program_workers(self) -> None:
        self.program_workers = [
            self._new_program_worker(computer, name, core)
            for computer, name, core in self.cluster_worker_specs
        ]
        self.program_active_worker = -1
        self.cluster_link_queue.clear()
        self.cluster_tick = 0
        self.cluster_transfers = 0
        self.cluster_shared_bus_value = 0.0
        self.cluster_last_transfer = "IDLE"
        self._load_program_worker(0, save_current=False)

    def _deliver_cluster_packets(self) -> None:
        if not self.cluster_enabled:
            return
        due = [packet for packet in self.cluster_link_queue if packet["due"] <= self.cluster_tick]
        self.cluster_link_queue = [packet for packet in self.cluster_link_queue if packet["due"] > self.cluster_tick]
        for packet in due:
            target = self.program_workers[packet["target"]]
            target["input_value"] = float(packet["value"])
            self.cluster_last_transfer = f"{packet['source_name']} → {target['name']} {packet['value']:0.4f}"

    def _transmit_cluster_packets(self) -> None:
        if not self.cluster_enabled or len(self.cluster_worker_specs) < 2:
            return
        computers: List[str] = []
        for computer, _, _ in self.cluster_worker_specs:
            if computer not in computers:
                computers.append(computer)
        if len(computers) < 2:
            return
        values: Dict[str, List[float]] = {computer: [] for computer in computers}
        for worker in self.program_workers:
            values[worker["computer"]].append(float(worker["bus_value"]))
        computer_values = {
            computer: sum(samples) / len(samples) if samples else 0.0
            for computer, samples in values.items()
        }
        self.cluster_shared_bus_value = sum(computer_values.values()) / max(1, len(computer_values))
        for source_computer, source_value in computer_values.items():
            for target_computer in computers:
                if target_computer == source_computer:
                    continue
                targets = [index for index, worker in enumerate(self.program_workers) if worker["computer"] == target_computer]
                for target in targets:
                    self.cluster_link_queue.append({
                        "due": self.cluster_tick + self.cluster_latency_ticks,
                        "target": target,
                        "value": source_value,
                        "source_name": source_computer,
                    })
                self.cluster_transfers += 1

    def _program_register(self, token: str) -> str:
        register = str(token).upper().lstrip("$")
        if register not in self.program_registers:
            raise ValueError(f"unknown register {token}; use R0-R15")
        return register

    def _program_value(self, token: str) -> float:
        text = str(token).strip()
        if text.upper().lstrip("$") in self.program_registers:
            return self.program_registers[text.upper().lstrip("$")]
        try:
            return float(text)
        except ValueError:
            raise ValueError(f"expected a number or register, got {token}") from None

    def _compile_program(self, source: str) -> Tuple[List[Tuple[str, List[str], int, str]], Dict[str, int]]:
        instructions: List[Tuple[str, List[str], int, str]] = []
        labels: Dict[str, int] = {}
        known = {
            "NOP", "CONST", "SET", "MOV", "ADD", "SUB", "MUL", "DIV", "INC", "DEC",
            "CLAMP", "NOT", "NOISE", "RANDOM", "OBSERVE", "BAYES", "HADAMARD",
            "CPHASE", "SQRTSWAP", "ISWAP", "FREDKIN", "PARITY", "WEAKMEASURE", "BRAID",
            "MAGICSTATE", "TELEPORT", "DEPHASE", "QFT", "LANE", "CORE", "MEASURE",
            "INPUT", "SEND", "OUTPUT", "PRINT", "WAIT", "JMP", "JNZ", "JZ", "HALT",
        }
        for line_number, original in enumerate(str(source).splitlines(), 1):
            line = original.strip()
            if not line:
                continue
            lexer = shlex.shlex(line, posix=True)
            lexer.whitespace_split = True
            lexer.commenters = ";#"
            try:
                tokens = list(lexer)
            except ValueError as exc:
                raise ValueError(f"LITHO-ISA line {line_number}: {exc}") from None
            if not tokens:
                continue
            while tokens and tokens[0].endswith(":"):
                label = tokens.pop(0)[:-1].upper()
                if not label or not label.replace("_", "A").isalnum() or label[0].isdigit():
                    raise ValueError(f"LITHO-ISA line {line_number}: invalid label")
                if label in labels:
                    raise ValueError(f"LITHO-ISA line {line_number}: duplicate label {label}")
                labels[label] = len(instructions)
            if not tokens:
                continue
            opcode = tokens[0].upper()
            if opcode not in known:
                raise ValueError(f"LITHO-ISA line {line_number}: unknown opcode {opcode}")
            instructions.append((opcode, tokens[1:], line_number, original.strip()))
        for opcode, args, line_number, _ in instructions:
            if opcode in {"JMP", "JNZ", "JZ"}:
                label = args[-1].upper() if args else ""
                if label not in labels:
                    raise ValueError(f"LITHO-ISA line {line_number}: unknown label {label or '<missing>'}")
        return instructions, labels

    def load_program(self, source: str, announce: bool = True) -> None:
        instructions, labels = self._compile_program(source)
        self.program_source = str(source)
        self.program_instructions = instructions
        self.program_labels = labels
        self.reset_program(announce=False)
        if announce:
            self.last_event = f"PROGRAM LOAD // {len(instructions)} instructions // LITHO-ISA"

    def reset_program(self, announce: bool = True) -> None:
        self.program_pc = 0
        self.program_registers = {f"R{index}": 0.0 for index in range(16)}
        self.program_running = False
        self.program_halted = False
        self.program_wait = 0
        self.program_clock = 0
        self.program_bus_value = 0.0
        self.program_input_value = 0.0
        self.program_output = []
        self.program_error = ""
        self._reset_program_workers()
        if announce:
            self.last_event = "PROGRAM RESET // all cluster cores cleared" if self.cluster_enabled else "PROGRAM RESET // registers cleared"

    def start_program(self, announce: bool = True) -> None:
        if not self.program_instructions:
            self.program_error = "program has no instructions"
            self.last_event = "PROGRAM ERROR // no instructions"
            return
        self._save_active_program_worker()
        if any(bool(worker["halted"]) for worker in self.program_workers):
            self.reset_program(announce=False)
        for worker in self.program_workers:
            worker["running"] = True
            worker["halted"] = False
            worker["error"] = ""
        self._load_program_worker(0, save_current=False)
        self.program_running = True
        self.program_halted = False
        self.program_error = ""
        if announce:
            scope = f" // {len(self.program_workers)} shared cores" if self.cluster_enabled else ""
            self.last_event = f"PROGRAM RUN // {self.program_speed} instructions per frame{scope}"

    def stop_program(self, announce: bool = True) -> None:
        self._save_active_program_worker()
        for worker in self.program_workers:
            worker["running"] = False
        self._load_program_worker(0, save_current=False)
        self.program_running = False
        if announce:
            self.last_event = "PROGRAM STOP // cluster execution paused" if self.cluster_enabled else "PROGRAM STOP // execution paused"

    def _program_jump(self, label: str) -> None:
        target = self.program_labels.get(str(label).upper())
        if target is None:
            raise ValueError(f"unknown label {label}")
        self.program_pc = target

    def _program_print(self, args: List[str]) -> None:
        if not args:
            raise ValueError("PRINT needs text, a register, or both")
        values: List[str] = []
        for token in args:
            register = token.upper().lstrip("$")
            if register in self.program_registers:
                values.append(f"{register}={self.program_registers[register]:0.4f}")
            else:
                values.append(token)
        self.program_output.append(" ".join(values)[:160])
        self.program_output = self.program_output[-12:]

    def step_program(self) -> bool:
        if self.program_halted or not self.program_instructions:
            return False
        if self.program_wait:
            self.program_wait -= 1
            self.program_clock += 1
            self._save_active_program_worker()
            return True
        if self.program_pc >= len(self.program_instructions):
            self.program_halted = True
            self.program_running = False
            self.last_event = "PROGRAM HALT // end of instruction stream"
            self._save_active_program_worker()
            return False
        opcode, args, line_number, _ = self.program_instructions[self.program_pc]
        self.program_pc += 1
        try:
            if opcode == "NOP":
                pass
            elif opcode in {"CONST", "SET"}:
                if len(args) != 2:
                    raise ValueError(f"{opcode} needs DEST VALUE")
                self.program_registers[self._program_register(args[0])] = self._program_value(args[1])
            elif opcode == "MOV":
                if len(args) != 2:
                    raise ValueError("MOV needs DEST SOURCE")
                self.program_registers[self._program_register(args[0])] = self._program_value(args[1])
            elif opcode in {"LANE", "CORE"}:
                if len(args) != 1:
                    raise ValueError(f"{opcode} needs DEST")
                self.program_registers[self._program_register(args[0])] = float(self.program_active_worker)
            elif opcode in {"ADD", "SUB", "MUL", "DIV"}:
                if len(args) not in {2, 3}:
                    raise ValueError(f"{opcode} needs DEST SOURCE [SOURCE]")
                destination = self._program_register(args[0])
                left = self.program_registers[destination] if len(args) == 2 else self._program_value(args[1])
                right = self._program_value(args[1] if len(args) == 2 else args[2])
                if opcode == "ADD":
                    value = left + right
                elif opcode == "SUB":
                    value = left - right
                elif opcode == "MUL":
                    value = left * right
                else:
                    value = left / right if abs(right) > 1e-12 else 0.0
                self.program_registers[destination] = value
            elif opcode in {"INC", "DEC"}:
                if len(args) != 1:
                    raise ValueError(f"{opcode} needs DEST")
                register = self._program_register(args[0])
                self.program_registers[register] += 1.0 if opcode == "INC" else -1.0
            elif opcode == "CLAMP":
                if len(args) != 3:
                    raise ValueError("CLAMP needs DEST LOW HIGH")
                destination = self._program_register(args[0])
                low, high = self._program_value(args[1]), self._program_value(args[2])
                self.program_registers[destination] = min(high, max(low, self.program_registers[destination]))
            elif opcode == "NOT":
                if len(args) != 2:
                    raise ValueError("NOT needs DEST SOURCE")
                self.program_registers[self._program_register(args[0])] = 1.0 - self._program_value(args[1])
            elif opcode in {"NOISE", "RANDOM"}:
                if len(args) not in {2, 3}:
                    raise ValueError(f"{opcode} needs DEST AMPLITUDE [CENTER]")
                destination = self._program_register(args[0])
                amplitude = abs(self._program_value(args[1]))
                center = self._program_value(args[2]) if len(args) == 3 else 0.0
                signal = math.sin(self.program_clock * 0.731 + self.program_pc * 1.113) * amplitude
                self.program_registers[destination] = center + signal
            elif opcode in {"OBSERVE", "INPUT"}:
                if len(args) != 1:
                    raise ValueError(f"{opcode} needs DEST")
                destination = self._program_register(args[0])
                self.program_registers[destination] = self.program_input_value if opcode == "INPUT" else self.bus_health()
            elif opcode == "BAYES":
                if len(args) != 3:
                    raise ValueError("BAYES needs DEST PRIOR LIKELIHOOD")
                destination = self._program_register(args[0])
                prior = min(1.0, max(0.0, self._program_value(args[1])))
                likelihood = min(1.0, max(0.0, self._program_value(args[2])))
                false_positive = 1.0 - likelihood
                denominator = prior * likelihood + (1.0 - prior) * false_positive
                self.program_registers[destination] = prior if denominator <= 1e-12 else prior * likelihood / denominator
            elif opcode == "HADAMARD":
                if len(args) != 2:
                    raise ValueError("HADAMARD needs DEST SOURCE")
                self.program_registers[self._program_register(args[0])] = (self._program_value(args[1]) + 1.0) / math.sqrt(2.0)
            elif opcode == "CPHASE":
                if len(args) != 3:
                    raise ValueError("CPHASE needs DEST CONTROL PHASE")
                control, phase = self._program_value(args[1]), self._program_value(args[2])
                self.program_registers[self._program_register(args[0])] = control * math.cos(phase)
            elif opcode in {"SQRTSWAP", "ISWAP"}:
                if len(args) != 3:
                    raise ValueError(f"{opcode} needs DEST A B")
                first, second = self._program_value(args[1]), self._program_value(args[2])
                if opcode == "SQRTSWAP":
                    value = (first + second) / math.sqrt(2.0)
                else:
                    value = math.hypot(first, second) / math.sqrt(2.0)
                self.program_registers[self._program_register(args[0])] = value
            elif opcode == "FREDKIN":
                if len(args) != 4:
                    raise ValueError("FREDKIN needs DEST CONTROL A B")
                control = self._program_value(args[1])
                self.program_registers[self._program_register(args[0])] = self._program_value(args[3] if control >= 0.5 else args[2])
            elif opcode == "PARITY":
                if len(args) != 3:
                    raise ValueError("PARITY needs DEST A B")
                first, second = self._program_value(args[1]), self._program_value(args[2])
                self.program_registers[self._program_register(args[0])] = float((round(first) + round(second)) % 2)
            elif opcode == "WEAKMEASURE":
                if len(args) != 3:
                    raise ValueError("WEAKMEASURE needs DEST SOURCE STRENGTH")
                source = self._program_value(args[1])
                strength = min(1.0, max(0.0, self._program_value(args[2])))
                self.program_registers[self._program_register(args[0])] = 0.5 * (1.0 - strength) + source * strength
            elif opcode == "BRAID":
                if len(args) != 3:
                    raise ValueError("BRAID needs DEST A B")
                first, second = self._program_value(args[1]), self._program_value(args[2])
                self.program_registers[self._program_register(args[0])] = (first + second) * math.cos(math.pi / 4.0)
            elif opcode == "MAGICSTATE":
                if len(args) != 2:
                    raise ValueError("MAGICSTATE needs DEST SOURCE")
                source = self._program_value(args[1])
                self.program_registers[self._program_register(args[0])] = source * math.cos(math.pi / 8.0) + (1.0 - source) * math.sin(math.pi / 8.0)
            elif opcode == "TELEPORT":
                if len(args) != 3:
                    raise ValueError("TELEPORT needs DEST STATE CORRECTION")
                state, correction = self._program_value(args[1]), self._program_value(args[2])
                self.program_registers[self._program_register(args[0])] = 1.0 - state if correction >= 0.5 else state
            elif opcode == "DEPHASE":
                if len(args) != 3:
                    raise ValueError("DEPHASE needs DEST SOURCE PROBABILITY")
                source = self._program_value(args[1])
                probability = min(1.0, max(0.0, self._program_value(args[2])))
                self.program_registers[self._program_register(args[0])] = source * (1.0 - probability) + (1.0 - source) * probability
            elif opcode == "QFT":
                if len(args) != 2:
                    raise ValueError("QFT needs DEST SOURCE")
                source = self._program_value(args[1])
                self.program_registers[self._program_register(args[0])] = 0.5 + 0.5 * math.cos(2.0 * math.pi * source)
            elif opcode == "MEASURE":
                if len(args) != 2:
                    raise ValueError("MEASURE needs DEST SOURCE")
                self.program_registers[self._program_register(args[0])] = 1.0 if self._program_value(args[1]) >= 0.5 else 0.0
            elif opcode in {"SEND", "OUTPUT"}:
                if len(args) != 1:
                    raise ValueError(f"{opcode} needs SOURCE")
                self.program_bus_value = min(1.0, max(0.0, self._program_value(args[0])))
                self.last_event = f"PROGRAM BUS // value {self.program_bus_value:0.4f} // pc {self.program_pc:03d}"
            elif opcode == "PRINT":
                self._program_print(args)
            elif opcode == "WAIT":
                if len(args) != 1:
                    raise ValueError("WAIT needs TICKS")
                self.program_wait = max(0, int(self._program_value(args[0])))
            elif opcode == "JMP":
                if len(args) != 1:
                    raise ValueError("JMP needs LABEL")
                self._program_jump(args[0])
            elif opcode in {"JNZ", "JZ"}:
                if len(args) != 2:
                    raise ValueError(f"{opcode} needs SOURCE LABEL")
                value = self._program_value(args[0])
                should_jump = abs(value) > 1e-9 if opcode == "JNZ" else abs(value) <= 1e-9
                if should_jump:
                    self._program_jump(args[1])
            elif opcode == "HALT":
                self.program_halted = True
                self.program_running = False
                self.last_event = "PROGRAM HALT // instruction requested"
            else:
                raise ValueError(f"unsupported opcode {opcode}")
        except (ValueError, ZeroDivisionError) as exc:
            self.program_error = f"line {line_number}: {exc}"
            self.program_halted = True
            self.program_running = False
            self.last_event = f"PROGRAM ERROR // {self.program_error}"
            self._save_active_program_worker()
            return False
        self.program_clock += 1
        self._save_active_program_worker()
        return True

    def run_program(self, steps: Optional[int] = None) -> int:
        budget = min(4096, max(1, int(steps if steps is not None else self.program_speed)))
        if self.cluster_enabled:
            self._save_active_program_worker()
            if not any(bool(worker["running"]) for worker in self.program_workers):
                return 0
            self.cluster_tick += 1
            self._deliver_cluster_packets()
            total = 0
            for index in range(len(self.program_workers)):
                self._load_program_worker(index)
                local_steps = 0
                while self.program_running and not self.program_halted and local_steps < budget:
                    if not self.step_program():
                        break
                    local_steps += 1
                total += local_steps
                self._save_active_program_worker()
            self._transmit_cluster_packets()
            self._load_program_worker(0)
            return total
        if not self.program_running:
            return 0
        executed = 0
        while self.program_running and not self.program_halted and executed < budget:
            if not self.step_program():
                break
            executed += 1
        return executed

    def program_status(self) -> str:
        if self.cluster_enabled:
            self._save_active_program_worker()
            running_count = sum(bool(worker["running"]) for worker in self.program_workers)
            error_count = sum(bool(worker["error"]) for worker in self.program_workers)
            halted_count = sum(bool(worker["halted"]) for worker in self.program_workers)
        else:
            running_count = int(self.program_running)
            error_count = int(bool(self.program_error))
            halted_count = int(self.program_halted)
        if error_count:
            state = "ERROR"
        elif running_count:
            state = "RUNNING"
        elif halted_count == len(self.program_workers):
            state = "HALTED"
        else:
            state = "PAUSED"
        output = self.program_output[-1] if self.program_output else "-"
        cluster = ""
        if self.cluster_enabled:
            lanes = "/".join(f"{worker['bus_value']:0.2f}" for worker in self.program_workers)
            cluster = f"  DUAL-SERVER {running_count}/{len(self.program_workers)}  {self.cluster_link_type.upper()} {self.cluster_latency_ticks}T TX{self.cluster_transfers}  LANES {lanes}"
        return f"{state} PC {self.program_pc:03d}/{len(self.program_instructions):03d}  SPEED {self.program_speed:03d}{cluster}  OUT {output[:20]}"

    def valid_cell(self, cell: GridCell) -> bool:
        # Grid coordinates are intentionally unbounded. This method remains as
        # a semantic hook for future chunk streaming/collision rules.
        return all(isinstance(value, int) for value in cell)

    def top_z(self, cell: GridCell) -> Optional[int]:
        if cell in self._top_cache:
            return self._top_cache[cell]
        x, y = cell
        heights = [z for (vx, vy, z) in self.voxels if vx == x and vy == y]
        top = max(heights) if heights else None
        self._top_cache[cell] = top
        return top

    def top_material(self, cell: GridCell) -> Optional[str]:
        z = self.top_z(cell)
        return self.voxels.get((cell[0], cell[1], z)) if z is not None else None

    def place_preset(self, origin: GridCell, preset_key: str, layer: int = 1, direction: str = "east") -> bool:
        preset = GATE_PRESETS.get(preset_key)
        if preset is None:
            return False
        target_layer = max(1, int(layer))
        direction = direction if direction in DIRECTIONS else "east"
        targets = [(origin[0] + dx, origin[1] + dy, target_layer, material) for dx, dy, material in preset.blocks]
        if any(material not in MATERIALS and material not in GATE_TYPES for _, _, _, material in targets):
            self.last_event = f"PRESET INVALID // {preset.label} contains an unknown tile"
            return False
        if any((x, y, z) in self.voxels for x, y, z, _ in targets):
            self.last_event = f"PRESET BLOCKED // clear {preset.label} footprint first"
            return False
        for x, y, z, material in targets:
            voxel = (x, y, z)
            self.voxels[voxel] = material
            self.voxel_directions[voxel] = direction
            self._top_cache.pop((x, y), None)
        self.max_layer = max(self.max_layer, target_layer)
        self.operations += len(targets)
        self.last_event = f"PRESET PLACE // {preset.label} / {len(targets)} blocks / {direction.upper()} / L{target_layer}"
        return True

    def place(self, cell: GridCell, material: str, layer: Optional[int] = None, direction: str = "east") -> bool:
        if material not in MATERIALS or not self.valid_cell(cell):
            return False
        if not self.infinite_supply and self.inventory.get(material, 0) <= 0:
            self.last_event = f"STOCK EMPTY // {MATERIALS[material].label}"
            return False
        top = self.top_z(cell)
        if top is None:
            top = -1
        target_layer = top + 1 if layer is None else max(1, int(layer))
        direction = direction if direction in DIRECTIONS else "east"
        if (cell[0], cell[1], target_layer) in self.voxels:
            self.last_event = f"LAYER OCCUPIED // remove [{cell[0]:02d},{cell[1]:02d}] on L{target_layer}"
            return False
        voxel = (cell[0], cell[1], target_layer)
        self.voxels[voxel] = material
        self.voxel_directions[voxel] = "up" if material == "via" else direction
        self._top_cache.pop(cell, None)
        if not self.infinite_supply:
            self.inventory[material] -= 1
        self.operations += 1
        self.max_layer = max(self.max_layer, target_layer)
        self.last_event = f"DEPOSIT // {MATERIALS[material].label} at [{cell[0]:02d},{cell[1]:02d}] L{target_layer}"
        return True

    def break_top(self, cell: GridCell, layer: Optional[int] = None) -> bool:
        if not self.valid_cell(cell):
            return False
        top = self.top_z(cell)
        target_layer = top if layer is None else max(1, int(layer))
        if target_layer is None or target_layer == 0 or (cell[0], cell[1], target_layer) not in self.voxels:
            self.last_event = "LAYER EMPTY // select a visible voxel connection first"
            return False
        voxel = (cell[0], cell[1], target_layer)
        material = self.voxels.pop(voxel)
        self.voxel_directions.pop(voxel, None)
        self._top_cache.pop(cell, None)
        if material in self.inventory and not self.infinite_supply:
            self.inventory[material] += 1
        self.operations += 1
        self.last_event = f"ETCH // removed {MATERIALS.get(material, Material('', material, '', '', '', '', '', '')).label} at [{cell[0]:02d},{cell[1]:02d}] L{target_layer}"
        return True

    def logic_place(self, chip_code: str, cell: GridCell, gate: str) -> bool:
        logic = self.chip_logic.get(chip_code)
        if logic is None or gate not in GATE_TYPES or not (0 <= cell[0] < 9 and 0 <= cell[1] < 6):
            return False
        if cell in logic.gates:
            self.last_event = "GATE LOCKED // right-click to remove the existing gate"
            return False
        if not self.infinite_supply and self.gate_inventory.get(gate, 0) <= 0:
            self.last_event = f"GATE STOCK EMPTY // {GATE_TYPES[gate].label}"
            return False
        logic.gates[cell] = gate
        if not self.infinite_supply:
            self.gate_inventory[gate] -= 1
        self.operations += 1
        self.last_event = f"GATE PLACE // {GATE_TYPES[gate].label} at slot [{cell[0] + 1},{cell[1] + 1}]"
        return True

    def logic_break(self, chip_code: str, cell: GridCell) -> bool:
        logic = self.chip_logic.get(chip_code)
        if logic is None or cell not in logic.gates:
            return False
        gate = logic.gates.pop(cell)
        if not self.infinite_supply:
            self.gate_inventory[gate] += 1
        self.operations += 1
        self.last_event = f"GATE REMOVE // {GATE_TYPES[gate].label} from slot [{cell[0] + 1},{cell[1] + 1}]"
        return True

    def toggle_port(self, chip_code: str, face: str, index: int, connected: Optional[bool] = None) -> bool:
        logic = self.chip_logic.get(chip_code)
        if logic is None or face not in logic.ports or not 0 <= index < len(logic.ports[face]):
            return False
        logic.ports[face][index] = (not logic.ports[face][index]) if connected is None else connected
        self.operations += 1
        state = "LINK" if logic.ports[face][index] else "UNLINK"
        self.last_event = f"BUS {state} // {face.upper()}-{index + 1} on {chip_code}"
        return True

    def logic_complete(self, chip_code: str) -> bool:
        chip = next((item for item in CHIPS if item.code == chip_code), None)
        logic = self.chip_logic.get(chip_code)
        if chip is None or logic is None:
            return False
        return len(logic.gates) >= chip.gate_target and logic.connected_ports == chip.port_total

    def auto_complete_logic(self, chip: ChipSpec) -> None:
        logic = self.chip_logic[chip.code]
        for index in range(chip.gate_target):
            gate = GATE_ORDER[index % len(GATE_ORDER)]
            logic.gates[(index % 9, 2 + ((index // 9) % 4))] = gate
        for face in logic.ports:
            logic.ports[face] = [True] * len(logic.ports[face])

    def _restore_state(self, raw_state: Any) -> None:
        if not isinstance(raw_state, dict):
            return
        raw_voxels = raw_state.get("voxels")
        if isinstance(raw_voxels, list):
            restored: Dict[Voxel, str] = {}
            for item in raw_voxels:
                if isinstance(item, list) and len(item) >= 4 and (str(item[3]) in MATERIALS or str(item[3]) in GATE_TYPES):
                    x, y, z = int(item[0]), int(item[1]), max(0, int(item[2]))
                    voxel = (x, y, z)
                    restored[voxel] = str(item[3])
                    if len(item) >= 5 and str(item[4]) in DIRECTIONS + ["up"]:
                        self.voxel_directions[voxel] = str(item[4])
            if restored:
                self.voxels = restored
                self._top_cache.clear()
                self.max_layer = max(self.max_layer, max((coord[2] for coord in restored), default=1))
        if not self.infinite_supply and isinstance(raw_state.get("inventory"), dict):
            for material, amount in raw_state["inventory"].items():
                if material in self.inventory:
                    self.inventory[material] = max(0, int(amount))
        raw_logic = raw_state.get("chip_logic", {})
        if isinstance(raw_logic, dict):
            for code, raw_chip_logic in raw_logic.items():
                logic = self.chip_logic.get(code)
                if logic is None or not isinstance(raw_chip_logic, dict):
                    continue
                logic.gates.clear()
                logic.ports = {face: [False] * len(values) for face, values in logic.ports.items()}
                for raw_gate in raw_chip_logic.get("gates", []):
                    if isinstance(raw_gate, dict) and isinstance(raw_gate.get("slot"), list) and len(raw_gate["slot"]) == 2:
                        gate = str(raw_gate.get("gate", ""))
                        if gate in GATE_TYPES:
                            logic.gates[(int(raw_gate["slot"][0]), int(raw_gate["slot"][1]))] = gate
                for raw_port in raw_chip_logic.get("ports", []):
                    if isinstance(raw_port, list) and len(raw_port) == 2:
                        face, index = str(raw_port[0]), int(raw_port[1])
                        if face in logic.ports and 0 <= index < len(logic.ports[face]):
                            logic.ports[face][index] = True
        raw_results = raw_state.get("results", {})
        if isinstance(raw_results, dict):
            for code, raw_result in raw_results.items():
                result = self.results.get(code)
                if result is not None and isinstance(raw_result, dict):
                    result.matched = int(raw_result.get("matched", result.matched))
                    result.exposed = bool(raw_result.get("exposed", result.exposed))
                    result.passed = bool(raw_result.get("passed", result.passed))
        self.operations = int(raw_state.get("operations", self.operations))
        self.completed_runs = int(raw_state.get("completed_runs", self.completed_runs))
        self.last_event = str(raw_state.get("last_event", self.last_event))

    def _chip_json(self) -> List[Dict[str, Any]]:
        saved_chips: List[Dict[str, Any]] = []
        for chip in CHIPS:
            logic = self.chip_logic[chip.code]
            pattern = {
                f"{cell[0] - chip.anchor[0]},{cell[1] - chip.anchor[1]}": material
                for cell, material in chip.pattern.items()
            }
            saved_chips.append({
                "name": chip.name,
                "code": chip.code,
                "anchor": list(chip.anchor),
                "pattern": pattern,
                "face_slots": chip.face_slots,
                "gate_target": chip.gate_target,
                "tint": chip.tint,
                "output": chip.output,
                "initial_gates": [
                    {"slot": list(slot), "gate": gate}
                    for slot, gate in logic.gates.items()
                ],
                "connected_ports": [
                    [face, index]
                    for face, values in logic.ports.items()
                    for index, connected in enumerate(values)
                    if connected
                ],
            })
        return saved_chips

    def save_json(self, filename: str, ui_state: Optional[Dict[str, Any]] = None) -> Path:
        output_path = Path(filename).expanduser()
        data = json.loads(json.dumps(self.config))
        data["infinite_supply"] = self.infinite_supply
        data["chips"] = self._chip_json()
        data["inventory"] = dict(self.inventory)
        data["program"] = {
            "language": "LITHO-ISA",
            "auto_start": bool(self.program_running),
            "speed": self.program_speed,
            "source": self.program_source,
        }
        data["state"] = {
            "voxels": [[x, y, z, material, self.voxel_directions.get((x, y, z), "east")] for (x, y, z), material in sorted(self.voxels.items())],
            "chip_logic": {
                code: {
                    "gates": [{"slot": list(slot), "gate": gate} for slot, gate in logic.gates.items()],
                    "ports": [[face, index] for face, values in logic.ports.items() for index, connected in enumerate(values) if connected],
                }
                for code, logic in self.chip_logic.items()
            },
            "results": {
                code: {"matched": result.matched, "exposed": result.exposed, "passed": result.passed}
                for code, result in self.results.items()
            },
            "operations": self.operations,
            "completed_runs": self.completed_runs,
            "last_event": self.last_event,
        }
        if ui_state:
            data["state"]["ui"] = ui_state
        output_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return output_path

    def scan(self, chip_code: Optional[str] = None) -> Optional[ChipSpec]:
        """Expose a selected pattern, or the most complete unexposed pattern."""
        candidates = [chip for chip in CHIPS if chip_code is None or chip.code == chip_code]
        candidates = [chip for chip in candidates if not self.results[chip.code].exposed]
        if not candidates:
            self.last_event = "QUEUE EMPTY // all masks already exposed"
            return None
        ranked: List[Tuple[float, ChipSpec]] = []
        for chip in candidates:
            result = self.results[chip.code]
            result.matched = sum(self.top_material(cell) == required for cell, required in chip.pattern.items())
            ranked.append((result.ratio, chip))
        chip = max(ranked, key=lambda item: item[0])[1]
        result = self.results[chip.code]
        logic_ok = self.logic_complete(chip.code)
        pattern_ok = result.matched == result.total
        if not pattern_ok or not logic_ok:
            result.exposed = False
            result.passed = False
            logic = self.chip_logic[chip.code]
            self.last_event = f"EXPOSE WAIT // {chip.name} pattern {result.matched}/{result.total}, gates {len(logic.gates)}/{chip.gate_target}, links {logic.connected_ports}/{chip.port_total}"
            return chip
        result.exposed = True
        result.passed = True
        self.completed_runs += 1
        self.last_event = f"EXPOSE PASS // {chip.name} {chip.output}"
        return chip

    def refresh_results(self) -> None:
        for chip in CHIPS:
            result = self.results[chip.code]
            if not result.exposed:
                result.matched = sum(self.top_material(cell) == required for cell, required in chip.pattern.items())

    def system_output(self) -> str:
        passed = sum(result.passed for result in self.results.values())
        connected = sum(logic.connected_ports for logic in self.chip_logic.values())
        ports = sum(chip.port_total for chip in CHIPS)
        idle = str(self.output_config.get("idle_message", "fabrication bus streaming"))
        supply = "INFINITE FAB STOCK" if self.infinite_supply else "STOCKED FAB"
        if passed == len(CHIPS):
            return f"{idle} // ALL CHIP PATHS NOMINAL // {supply}"
        return f"{idle} // {passed:02d}/{len(CHIPS):02d} CHIP PATHS / {connected:02d}/{ports:02d} PORTS // {supply}"

    def equation_text(self, index: int = 0) -> str:
        if not self.equations:
            return ""
        item = self.equations[index % len(self.equations)]
        if isinstance(item, dict):
            name = str(item.get("name", "EQUATION"))
            expression = str(item.get("expression", item.get("equation", "")))
            return f"{name}: {expression}" if expression else name
        return str(item)

    def bus_health(self) -> float:
        passed = sum(result.passed for result in self.results.values())
        exposed = sum(result.exposed for result in self.results.values())
        # Four routed traces are intentionally required for a perfect bus.
        routes = [(layer, cell) for layer, cells in self.layer_bus_cells.items() for cell in cells]
        routed = sum(self.voxels.get((cell[0], cell[1], layer)) == "copper" for layer, cell in routes)
        return min(1.0, 0.16 + passed * 0.16 + exposed * 0.04 + routed / max(1, len(routes)) * 0.48)

    def full_pattern_for(self, chip: ChipSpec) -> None:
        """Deterministic helper used only by --self-test."""
        for cell, material in chip.pattern.items():
            if self.top_material(cell) != material:
                # Remove any upper material until the base substrate is exposed.
                while self.top_z(cell) is not None and self.top_z(cell) > 0:
                    self.break_top(cell)
                self.place(cell, material)
        self.auto_complete_logic(chip)


class LithoLab:
    """Tkinter renderer and input loop."""

    W = 1280
    H = 760
    WORLD_W = 900
    TILE_W = 44
    TILE_H = 23
    BLOCK_H = 18
    EDITOR_CELL = 66
    EDITOR_COLS = 9
    EDITOR_ROWS = 6
    ORIGIN_X = 438
    ORIGIN_Y = 350

    BG = "#070d14"
    PANEL = "#0b151f"
    PANEL_ALT = "#0e1c28"
    TEXT = "#d8e7ef"
    MUTED = "#708692"
    TEAL = "#42d6d1"
    CYAN = "#76eff4"
    AMBER = "#f6b85f"
    RED = "#f07076"
    GREEN = "#6ceda5"

    def __init__(self) -> None:
        self.model = LabModel()
        self.root = tk.Tk()
        self.root.title(self.model.system_name)
        self.root.geometry(f"{self.W}x{self.H}")
        self.root.minsize(1080, 680)
        self.root.configure(bg=self.BG)
        self.file_menu = tk.Menu(self.root, tearoff=False, bg="#0d1c26", fg=self.TEXT, activebackground="#2d5c68", activeforeground="#ffffff")
        self.file_menu.add_command(label="Load System from File…", command=self.load_system_dialog)
        self.file_menu.add_command(label="Load Neural Example", command=lambda: self.load_system_path(Path(__file__).with_name("example_system.json")))
        self.file_menu.add_command(label="Load Quantum Example", command=lambda: self.load_system_path(Path(__file__).with_name("quantum_system.json")))
        self.file_menu.add_command(label="Load Parallel Example", command=lambda: self.load_system_path(Path(__file__).with_name("parallel_system.json")))
        self.file_menu.add_command(label="Edit / Run LITHO-ISA Program…", command=self.open_program_editor)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save System", command=self.save_game)
        self.file_menu.add_command(label="Save System As…", command=lambda: self.save_game(save_as=True))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.destroy)
        self.root.config(menu=self.file_menu)
        self.program_editor_window: Optional[tk.Toplevel] = None
        self.program_text_widget: Optional[tk.Text] = None
        self.program_editor_status: Optional[tk.Label] = None
        self.program_speed_var = tk.IntVar(self.root, value=self.model.program_speed)
        self.compute_speed_frame = tk.Frame(self.root, bg="#0b1922", highlightbackground="#244653", highlightthickness=1)
        self.compute_speed_title = tk.Label(self.compute_speed_frame, text="COMPUTE SPEED", bg="#0b1922", fg=self.CYAN, font=("TkFixedFont", 7, "bold"))
        self.compute_speed_title.pack(side="left", padx=(7, 3), pady=2)
        self.compute_speed_value = tk.Label(self.compute_speed_frame, text=f"{self.model.program_speed:03d} INST/TICK", bg="#0b1922", fg=self.GREEN, font=("TkFixedFont", 7, "bold"))
        self.compute_speed_value.pack(side="right", padx=(2, 7), pady=2)
        self.compute_speed_scale = tk.Scale(
            self.compute_speed_frame, from_=1, to=512, orient="horizontal", showvalue=False,
            variable=self.program_speed_var, command=self.on_compute_speed, length=168,
            bg="#0b1922", fg=self.CYAN, troughcolor="#102a34", highlightthickness=0,
            activebackground=self.CYAN, relief="flat", sliderlength=16, width=10,
        )
        self.compute_speed_scale.pack(side="left", fill="x", expand=True, padx=2, pady=0)
        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H, bg=self.BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        # The monitor is a real independent canvas so its long telemetry and
        # graphical output can scroll without moving the build viewport.
        self.sidebar_scroll = 0.0
        self.sidebar_content_height = 1120
        self.sidebar_canvas = tk.Canvas(self.root, bg=self.PANEL, highlightthickness=0, bd=0)
        self.sidebar_scrollbar = tk.Scrollbar(
            self.root, orient="vertical", command=self.on_sidebar_scrollbar,
            bg="#132834", troughcolor="#07141c", activebackground="#42d6d1",
            highlightthickness=0, bd=0, width=14, relief="flat",
        )
        self.preset_var = tk.StringVar(self.root, value="FREE BUILD")
        self.preset_caption = tk.Label(self.root, text="MATERIAL GATE PRESET", bg=self.PANEL, fg=self.MUTED, font=("TkFixedFont", 8, "bold"))
        self.preset_menu = tk.OptionMenu(self.root, self.preset_var, "FREE BUILD", *[preset.label for preset in GATE_PRESETS.values()], command=self.on_preset_select)
        self.preset_menu.configure(bg="#152834", fg=self.TEXT, activebackground="#244955", activeforeground="#ffffff", highlightthickness=0, relief="flat", font=("TkFixedFont", 8, "bold"))
        self.preset_menu["menu"].configure(bg="#0d1c26", fg=self.TEXT, activebackground="#2d5c68", activeforeground="#ffffff", font=("TkFixedFont", 8))
        self.place_preset_widgets()

        self.selected = "copper"
        self.target: Optional[GridCell] = None
        self.player_x = 6.4
        self.player_y = 5.9
        self.keys: set[str] = set()
        self.frame = 0
        self.cycles = 0
        self.started_at = time.time()
        self.last_tick_time = time.perf_counter()
        self.render_stride = 2
        self.monitor_stride = 6
        self.message_flash = 0
        self.view = "macro"
        self.active_chip_code = CHIPS[0].code
        self.selected_gate = "and"
        self.flight_mode = False
        self.flight_altitude = 2.25
        self.topdown = False
        self.TOP_CELL = 32
        self.active_layer = 1
        self.camera_x = self.player_x
        self.camera_y = self.player_y
        self.camera_offset_x = 0.0
        self.camera_offset_y = 0.0
        self.zoom = 1.0
        self.rng = random.Random(11)
        self.material_page = 0
        self.gate_page = 0
        self.palette_dragging = False
        self.gate_palette_dragging = False
        self.selected_preset: Optional[str] = None
        self.build_direction = "east"
        self.save_path = Path(__file__).with_name("savegame.json")
        self.place_compute_speed_widget()

        self.canvas.bind("<Motion>", self.on_mouse_motion)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)
        self.canvas.bind("<B1-Motion>", self.on_palette_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_palette_release)
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.sidebar_canvas.bind("<MouseWheel>", self.on_sidebar_wheel)
        self.sidebar_canvas.bind("<Button-4>", self.on_sidebar_wheel)
        self.sidebar_canvas.bind("<Button-5>", self.on_sidebar_wheel)
        self.root.bind("<KeyPress>", self.on_key_down)
        self.root.bind("<KeyRelease>", self.on_key_up)
        self.root.bind("<FocusOut>", lambda event: self.keys.clear())
        self.root.bind("<Configure>", self.on_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.place_sidebar_widgets()
        self.animate()

    def on_resize(self, event: tk.Event) -> None:
        if event.widget is self.root:
            self.W = max(1080, event.width)
            self.H = max(680, event.height)
            self.place_preset_widgets()
            self.place_compute_speed_widget()
            self.place_sidebar_widgets()

    def place_sidebar_widgets(self) -> None:
        if not hasattr(self, "sidebar_canvas"):
            return
        sidebar_x = self.WORLD_W
        sidebar_width = max(160, self.W - sidebar_x - 16)
        sidebar_height = max(1, self.H - 70)
        self.sidebar_canvas.place(x=sidebar_x, y=70, width=sidebar_width, height=sidebar_height)
        self.sidebar_scrollbar.place(x=self.W - 16, y=70, width=16, height=sidebar_height)

    def place_compute_speed_widget(self) -> None:
        if not hasattr(self, "compute_speed_frame"):
            return
        # Keep the control in the world header, clear of the right monitor.
        self.compute_speed_frame.place(x=max(430, self.WORLD_W - 340), y=8, width=320, height=58)

    def on_compute_speed(self, value: str) -> None:
        self.model.program_speed = min(512, max(1, int(float(value))))
        self.compute_speed_value.configure(text=f"{self.model.program_speed:03d} INST/TICK")
        self.model.last_event = f"COMPUTE SPEED // {self.model.program_speed} instructions per tick"
        self.update_program_editor_status()

    def place_preset_widgets(self) -> None:
        if not hasattr(self, "preset_menu"):
            return
        if getattr(self, "view", "macro") == "chip":
            self.preset_caption.place_forget()
            self.preset_menu.place_forget()
            return
        x = 510
        y = max(88, self.H - 143)
        self.preset_caption.place(x=x, y=y - 17, width=250, height=16)
        self.preset_menu.place(x=x, y=y, width=250, height=28)

    def on_preset_select(self, label: str) -> None:
        if label == "FREE BUILD":
            self.selected_preset = None
            self.model.last_event = "TOOL SELECT // free material placement"
            return
        self.selected_preset = next((key for key, preset in GATE_PRESETS.items() if preset.label == label), None)
        if self.selected_preset:
            self.model.last_event = f"PRESET SELECT // {label} // click the board to stamp"

    def visual_material(self, key: str) -> Optional[Material]:
        mat = MATERIALS.get(key)
        if mat is not None:
            return mat
        gate = GATE_TYPES.get(key)
        if gate is None:
            return None
        return Material(key, gate.label, gate.symbol, gate.color, "#432b55", "#5b3970", gate.color, gate.help_text)

    def draw_preset_preview(self) -> None:
        if self.selected_preset is None or self.target is None or not self.topdown:
            return
        preset = GATE_PRESETS[self.selected_preset]
        for dx, dy, material in preset.blocks:
            x1, y1, x2, y2 = self.topdown_rect(self.target[0] + dx, self.target[1] + dy, 5)
            mat = self.visual_material(material)
            if mat is None:
                continue
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=mat.top, outline=preset.tint, width=2, stipple="gray50")
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=mat.short, fill="#ffffff", font=("TkFixedFont", 7, "bold"))

    def grid_to_screen(self, x: float, y: float, z: float = 0.0) -> Tuple[float, float]:
        scale = self.zoom
        return (
            self.ORIGIN_X + ((x - self.camera_x) - (y - self.camera_y)) * self.TILE_W * scale / 2,
            self.ORIGIN_Y + ((x - self.camera_x) + (y - self.camera_y)) * self.TILE_H * scale / 2 - z * self.BLOCK_H * scale,
        )

    def grid_diamond(self, x: float, y: float, z: float = 0.0, lift: float = 0.0) -> List[Tuple[float, float]]:
        sx, sy = self.grid_to_screen(x, y, z)
        half_w = self.TILE_W * self.zoom / 2
        half_h = self.TILE_H * self.zoom / 2
        sy -= lift * self.zoom
        return [(sx, sy - half_h), (sx + half_w, sy), (sx, sy + half_h), (sx - half_w, sy)]

    def block_is_active(self, x: int, y: int, z: int, material: str) -> bool:
        if material not in ACTIVE_BLOCKS and material not in GATE_TYPES:
            return False
        health = self.model.bus_health()
        if health <= 0.24:
            return False
        phase = (self.frame + x * 5 + y * 7 + z * 11) % 36
        return phase < int(16 + health * 12)

    def direction_vector(self, direction: str) -> Tuple[float, float]:
        return {
            "east": (1.0, 0.0),
            "south": (0.0, 1.0),
            "west": (-1.0, 0.0),
            "north": (0.0, -1.0),
        }.get(direction, (1.0, 0.0))

    def route_direction(self, first: GridCell, second: GridCell) -> str:
        """Return the packet's current hop direction, including diagonal hops."""
        dx = second[0] - first[0]
        dy = second[1] - first[1]
        horizontal = "east" if dx > 0 else "west" if dx < 0 else ""
        vertical = "south" if dy > 0 else "north" if dy < 0 else ""
        if horizontal and vertical:
            return vertical + horizontal
        return horizontal or vertical or "hold"

    def bus_packet_state(self, cells: List[GridCell]) -> Optional[Tuple[GridCell, GridCell, float, str, int, int]]:
        """Return the packet's current segment and hop-local direction."""
        if len(cells) < 2:
            return None
        hop_count = len(cells) - 1
        progress = (self.frame * 0.035) % hop_count
        hop = min(hop_count - 1, int(progress))
        return cells[hop], cells[hop + 1], progress - hop, self.route_direction(cells[hop], cells[hop + 1]), hop, hop_count

    def draw_packet_marker(self, point: Tuple[float, float], target: Tuple[float, float], color: str, label: str = "") -> None:
        """Draw a clean arrow-shaped packet aligned to its current hop."""
        dx = target[0] - point[0]
        dy = target[1] - point[1]
        length = math.hypot(dx, dy) or 1.0
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        size = 6.0
        tip = (point[0] + ux * size * 1.8, point[1] + uy * size * 1.8)
        back = (point[0] - ux * size, point[1] - uy * size)
        left = (back[0] + px * size * 0.82, back[1] + py * size * 0.82)
        right = (back[0] - px * size * 0.82, back[1] - py * size * 0.82)
        self.canvas.create_line(point[0] - ux * 13, point[1] - uy * 13, point[0] - ux * 5, point[1] - uy * 5, fill="#fff3a8", width=2)
        self.canvas.create_polygon(tip, left, right, fill=color, outline="#ffffff", width=1)
        self.canvas.create_oval(point[0] - 2, point[1] - 2, point[0] + 2, point[1] + 2, fill="#ffffff", outline="")
        if label:
            self.canvas.create_text(point[0] + px * 12, point[1] + py * 12, text=label, fill="#ffe76b", font=("TkFixedFont", 7, "bold"))

    def draw_iso_packet(self) -> None:
        cells = self.model.layer_bus_cells.get(self.active_layer, self.model.bus_cells)
        state = self.bus_packet_state(cells)
        if state is None or self.model.bus_health() <= 0.24:
            return
        first, second, fraction, direction, hop, hop_count = state
        a = self.grid_to_screen(first[0] + 0.5, first[1] + 0.5, self.active_layer + 0.18)
        b = self.grid_to_screen(second[0] + 0.5, second[1] + 0.5, self.active_layer + 0.18)
        point = (a[0] + (b[0] - a[0]) * fraction, a[1] + (b[1] - a[1]) * fraction)
        self.draw_packet_marker(point, b, "#ffe76b", f"PKT {direction.upper()}")

    def draw_iso_direction(self, x: int, y: int, z: int, direction: str, active: bool, material: str = "via") -> None:
        if direction not in DIRECTIONS:
            return
        sx, sy = self.grid_to_screen(x, y, z + 0.08)
        vx, vy = self.direction_vector(direction)
        length = 10 + (3 if active else 0)
        ex, ey = self.grid_to_screen(x + vx * length / self.TILE_W, y + vy * length / self.TILE_H, z + 0.08)
        visual = self.visual_material(material) or MATERIALS["via"]
        color = visual.glow if active else "#38515a"
        self.canvas.create_line(sx, sy, ex, ey, fill=color, width=2, arrow=tk.LAST)

    def iso_block(self, x: int, y: int, z: int, material: str) -> None:
        mat = self.visual_material(material)
        if material == "pcb":
            mat = Material("pcb", "PCB", "", "#1d5548", "#12382f", "#164238", "#3ad9b9", "substrate")
        if mat is None:
            return
        active = self.block_is_active(x, y, z, material)
        top = self.grid_diamond(x, y, z)
        top_l = top[0]
        top_r = top[1]
        top_b = top[2]
        top_lft = top[3]
        block_h = self.BLOCK_H * self.zoom
        low_l = (top_lft[0], top_lft[1] + block_h)
        low_b = (top_b[0], top_b[1] + block_h)
        low_r = (top_r[0], top_r[1] + block_h)
        edge = mat.glow if active else "#0b2028"
        edge_width = 2 if active else 1
        self.canvas.create_polygon(top_lft, top_l, top_r, top_b, fill=mat.top, outline=edge, width=edge_width)
        self.canvas.create_polygon(top_lft, top_b, low_b, low_l, fill=mat.left, outline=edge, width=edge_width)
        self.canvas.create_polygon(top_b, top_r, low_r, low_b, fill=mat.right, outline=edge, width=edge_width)
        if material in DIRECTIONAL_BLOCKS or material in GATE_TYPES:
            self.draw_iso_direction(x, y, z, self.model.voxel_directions.get((x, y, z), "east"), active, material)

    def draw_background(self) -> None:
        c = self.canvas
        c.create_rectangle(0, 0, self.W, self.H, fill=self.BG, outline="")
        c.create_rectangle(self.WORLD_W, 0, self.W, self.H, fill=self.PANEL, outline="")
        c.create_line(self.WORLD_W, 0, self.WORLD_W, self.H, fill="#18313b", width=2)
        # Subtle scanlines make the lab look like an instrument display.
        for y in range(92, self.H, 32):
            c.create_line(22, y, self.WORLD_W - 18, y, fill="#0c1b25")
        c.create_text(28, 28, anchor="nw", text=f"LITHO // {self.model.system_name}", fill=self.TEXT, font=("TkFixedFont", 16, "bold"))
        if self.view == "chip":
            mode_label = f"CHIP SCALE  ·  {self.active_chip_code}  ·  GATE ROUTER"
        elif self.topdown:
            mode_label = f"TOP-DOWN BUILD  ·  LAYER {self.active_layer:02d}  ·  {len(MATERIAL_ORDER)} BLOCK TYPES"
        elif self.flight_mode:
            mode_label = f"FAB RUN 004  ·  FLIGHT MODE  ·  ALT {self.flight_altitude:0.1f}"
        else:
            mode_label = "FAB RUN 004  ·  PARTICLE ENGINEER MODE"
        c.create_text(30, 58, anchor="nw", text=mode_label, fill=self.TEAL, font=("TkFixedFont", 9, "bold"))
        c.create_text(self.WORLD_W - 25, 32, anchor="ne", text=f"LIVE / {'TOP-DOWN' if self.topdown else 'ISO'} / L{self.active_layer:02d}", fill=self.MUTED, font=("TkFixedFont", 9, "bold"))
        c.create_line(25, 82, self.WORLD_W - 24, 82, fill="#1b3540")

    def visible_grid_bounds(self) -> Tuple[range, range]:
        scale = max(0.25, self.zoom)
        half_x = min(48, max(10, math.ceil(21 / scale)))
        half_y = min(36, max(8, math.ceil(16 / scale)))
        return (
            range(math.floor(self.camera_x) - half_x, math.floor(self.camera_x) + half_x + 1),
            range(math.floor(self.camera_y) - half_y, math.floor(self.camera_y) + half_y + 1),
        )

    def draw_infinite_grid(self) -> None:
        c = self.canvas
        xs, ys = self.visible_grid_bounds()
        plane_z = max(0, self.active_layer - 0.06)
        for x in xs:
            for y in ys:
                pts = self.grid_diamond(x, y, plane_z)
                if max(point[0] for point in pts) < 0 or min(point[0] for point in pts) > self.WORLD_W:
                    continue
                if max(point[1] for point in pts) < 84 or min(point[1] for point in pts) > self.H - 114:
                    continue
                fill = "#0b1b23" if (x + y) % 2 else "#0d2028"
                c.create_polygon(pts, fill=fill, outline="#173742", width=1)

    def draw_lithography_fields(self) -> None:
        c = self.canvas
        xs, ys = self.visible_grid_bounds()
        x_min, x_max = xs.start, xs.stop
        y_min, y_max = ys.start, ys.stop
        for field in self.model.lithography_regions:
            if field["layer"] != self.active_layer:
                continue
            ox, oy = field["origin"]
            width, height = field["size"]
            if ox + width < x_min or ox > x_max or oy + height < y_min or oy > y_max:
                continue
            tint = field["tint"]
            pitch = field["pitch"]
            # The boundary and label make the scale of the mask field legible.
            corners = [
                self.grid_to_screen(ox, oy, self.active_layer + 0.10),
                self.grid_to_screen(ox + width, oy, self.active_layer + 0.10),
                self.grid_to_screen(ox + width, oy + height, self.active_layer + 0.10),
                self.grid_to_screen(ox, oy + height, self.active_layer + 0.10),
            ]
            c.create_polygon(corners, outline=tint, fill="", width=2, dash=(6, 3))
            label_x, label_y = self.grid_to_screen(ox + 0.3, oy + 0.2, self.active_layer + 0.18)
            loci = width * height
            c.create_text(label_x, label_y, anchor="sw", text=f"{field['name']}  //  {loci:,} LITHO LOCI  //  L{self.active_layer}", fill=tint, font=("TkFixedFont", 8, "bold"))

            pattern = field["pattern"]
            visible_x = range(max(x_min, ox), min(x_max, ox + width))
            visible_y = range(max(y_min, oy), min(y_max, oy + height))
            if pattern in {"crosshatch", "grid"}:
                for x in visible_x:
                    if (x - ox) % pitch == 0:
                        x1, y1 = self.grid_to_screen(x, max(y_min, oy), self.active_layer + 0.12)
                        x2, y2 = self.grid_to_screen(x, min(y_max - 1, oy + height - 1) + 1, self.active_layer + 0.12)
                        c.create_line(x1, y1, x2, y2, fill=tint, width=1)
                for y in visible_y:
                    if (y - oy) % pitch == 0:
                        x1, y1 = self.grid_to_screen(max(x_min, ox), y, self.active_layer + 0.12)
                        x2, y2 = self.grid_to_screen(min(x_max - 1, ox + width - 1) + 1, y, self.active_layer + 0.12)
                        c.create_line(x1, y1, x2, y2, fill=tint, width=1)
            else:
                for x in visible_x:
                    for y in visible_y:
                        if pattern == "checker" and ((x - ox) + (y - oy)) % 2:
                            continue
                        sx, sy = self.grid_to_screen(x + 0.5, y + 0.5, self.active_layer + 0.14)
                        c.create_oval(sx - 2, sy - 2, sx + 2, sy + 2, fill=tint, outline="")

            # Field taps are explicit PCB hand-off points.
            center = self.grid_to_screen(ox + width / 2, oy + height / 2, self.active_layer + 0.16)
            for tap in field["bus_taps"]:
                tx, ty = self.grid_to_screen(tap[0], tap[1], self.active_layer + 0.18)
                c.create_line(center[0], center[1], tx, ty, fill="#f6b85f", width=2, dash=(3, 4))
                c.create_oval(tx - 5, ty - 5, tx + 5, ty + 5, fill="#342919", outline="#f6b85f", width=2)
                c.create_text(tx + 8, ty - 6, text="PCB TAP", fill="#ffd185", anchor="w", font=("TkFixedFont", 7, "bold"))

    def draw_board_markings(self) -> None:
        c = self.canvas
        self.draw_infinite_grid()
        self.draw_lithography_fields()
        bus_cells = self.model.layer_bus_cells.get(self.active_layer, self.model.bus_cells)
        points = [self.grid_to_screen(x, y, self.active_layer + 0.08) for x, y in bus_cells]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            c.create_line(x1, y1, x2, y2, fill="#3f989d", width=3)
        if bus_cells:
            c.create_text(*self.grid_to_screen(bus_cells[0][0] + 0.1, bus_cells[0][1], self.active_layer + 0.2), text=f"{self.model.bus_name} / L{self.active_layer}", anchor="e", fill="#8bc8c8", font=("TkFixedFont", 7, "bold"))

        # Empty chip pattern cells remain visible as a stencil overlay on L1.
        for chip in CHIPS:
            result = self.model.results[chip.code]
            for cell, required in chip.pattern.items():
                if self.active_layer == 1 and self.model.top_z(cell) in {0, None}:
                    pts = self.grid_diamond(cell[0], cell[1], self.active_layer + 0.12)
                    color = chip.tint if not result.exposed else (self.GREEN if result.passed else self.RED)
                    c.create_polygon(pts, fill="#101f28", outline=color, width=1)
                    c.create_text(pts[0][0], pts[0][1] + 1, text=MATERIALS[required].short, fill="#6b8c95", font=("TkFixedFont", 7, "bold"))
            label_x, label_y = self.grid_to_screen(chip.anchor[0] + 0.6, chip.anchor[1] - 0.30, self.active_layer + 0.1)
            c.create_text(label_x, label_y, text=f"{chip.code}  {chip.name}", anchor="s", fill=self.GREEN if result.passed else chip.tint, font=("TkFixedFont", 7, "bold"))

    def draw_voxels(self) -> None:
        xs, ys = self.visible_grid_bounds()
        x_min, x_max = xs.start, xs.stop
        y_min, y_max = ys.start, ys.stop
        ordered = sorted(
            ((coord, material) for coord, material in self.model.voxels.items()
             if coord[2] == self.active_layer and x_min <= coord[0] < x_max and y_min <= coord[1] < y_max),
            key=lambda item: (item[0][0] + item[0][1], item[0][2]),
        )
        for (x, y, z), material in ordered:
            self.iso_block(x, y, z, material)
        self.draw_layer_connections()
        self.draw_iso_packet()

    def draw_layer_connections(self) -> None:
        c = self.canvas
        xs, ys = self.visible_grid_bounds()
        visible = {(x, y) for x in xs for y in ys}
        layers_by_cell: Dict[GridCell, List[int]] = {}
        for (x, y, z), material in self.model.voxels.items():
            if z > 0 and (x, y) in visible and material in {"copper", "mask", "silicon"}:
                layers_by_cell.setdefault((x, y), []).append(z)
        for (x, y), layers in layers_by_cell.items():
            layers = sorted(set(layers))
            low, high = min(layers), max(max(layers), self.active_layer)
            if high <= low:
                continue
            sx1, sy1 = self.grid_to_screen(x, y, low)
            sx2, sy2 = self.grid_to_screen(x, y, high)
            c.create_line(sx1, sy1, sx2, sy2, fill="#76eff4", width=3, dash=(4, 3))
            for layer in sorted(set(layers + [self.active_layer])):
                sx, sy = self.grid_to_screen(x, y, layer)
                c.create_oval(sx - 5, sy - 5, sx + 5, sy + 5, fill="#102c39", outline="#76eff4", width=2)
                c.create_text(sx + 9, sy - 7, text=f"L{layer}", fill="#9afcff", anchor="w", font=("TkFixedFont", 7, "bold"))

    def draw_target(self) -> None:
        if self.target is None or not self.model.valid_cell(self.target):
            return
        x, y = self.target
        z = self.active_layer
        pts = self.grid_diamond(x, y, z + 0.12)
        self.canvas.create_polygon(pts, outline=self.CYAN, fill="", width=2)
        sx, sy = self.grid_to_screen(x, y, z + 0.14)
        self.canvas.create_text(sx, sy - 20, text=f"[{x:02d},{y:02d}]", fill=self.CYAN, font=("TkFixedFont", 8, "bold"))

    def draw_player(self) -> None:
        c = self.canvas
        player_z = self.flight_altitude if self.flight_mode else 1.72
        sx, sy = self.grid_to_screen(self.player_x, self.player_y, player_z)
        if self.flight_mode:
            shadow_x, shadow_y = self.grid_to_screen(self.player_x, self.player_y, 1.18)
            c.create_oval(shadow_x - 10, shadow_y - 4, shadow_x + 10, shadow_y + 4, outline="#2b8587", fill="#10282e")
            c.create_line(shadow_x, shadow_y, sx, sy, fill="#2a757d", dash=(3, 4))
        pulse = 5 + math.sin(self.frame / 8) * 2
        c.create_oval(sx - 14 - pulse / 3, sy - 14 - pulse / 3, sx + 14 + pulse / 3, sy + 14 + pulse / 3, outline="#1c7f8d", width=1)
        c.create_oval(sx - 7, sy - 7, sx + 7, sy + 7, fill=self.CYAN, outline="#d8ffff", width=1)
        c.create_oval(sx - 2, sy - 2, sx + 2, sy + 2, fill="#ffffff", outline="")
        c.create_line(sx - 17, sy, sx - 9, sy, fill=self.CYAN)
        c.create_line(sx + 9, sy, sx + 17, sy, fill=self.CYAN)
        label = f"FLIGHT // z={self.flight_altitude:0.1f}" if self.flight_mode else "ENGINEER // q-bit"
        c.create_text(sx + 13, sy - 18, text=label, anchor="sw", fill=self.CYAN, font=("TkFixedFont", 8, "bold"))

    def draw_gatebar(self) -> None:
        c = self.canvas
        y = self.H - 82
        c.create_rectangle(22, y - 12, self.WORLD_W - 22, self.H - 18, fill="#0c1923", outline="#1e3c47")
        c.create_text(35, y + 8, anchor="w", text="PARTICLE GATES", fill=self.MUTED, font=("TkFixedFont", 8, "bold"))
        visible_count = 4
        pages = max(1, (len(GATE_ORDER) + visible_count - 1) // visible_count)
        start_index = self.gate_page * visible_count
        for local_index, key in enumerate(GATE_ORDER[start_index:start_index + visible_count]):
            gate = GATE_TYPES[key]
            x = 145 + local_index * 142
            active = key == self.selected_gate
            c.create_rectangle(x, y - 2, x + 126, y + 30, fill="#152834" if active else "#0d1c26", outline=gate.color if active else "#24404a", width=2 if active else 1)
            c.create_text(x + 9, y + 6, anchor="nw", text=f"{local_index + 1}  {gate.symbol} {gate.label}", fill=self.TEXT if active else self.MUTED, font=("TkFixedFont", 7, "bold"))
            supply = "∞" if self.model.infinite_supply else f"{self.model.gate_inventory[key]:02d}"
            c.create_text(x + 9, y + 19, anchor="nw", text=f"{supply}  {gate.help_text}", fill=gate.color if active else "#55707b", font=("TkFixedFont", 6))
        self.draw_palette_scrollbar(self.gate_page, pages, y - 2, y + 30, gate=True)
        selected_gate = GATE_TYPES[self.selected_gate]
        self.panel_text(35, y + 43, f"Q-FAB // {selected_gate.label} // PARTICLES: {selected_gate.particle} // {selected_gate.fabrication}", fill=selected_gate.color, size=7, bold=True)
        if selected_gate.equation:
            self.panel_text(self.WORLD_W - 35, y + 43, selected_gate.equation, fill="#d6a7ff", size=7, bold=True, anchor="e")
        self.panel_text(self.WORLD_W - 35, y + 8, f"GATES {self.gate_page + 1}/{pages}  ·  DIR {self.build_direction.upper()}  ·  Z RETURN", fill=self.AMBER, size=7, bold=True, anchor="e")

    def topdown_to_screen(self, x: float, y: float) -> Tuple[float, float]:
        cell = self.TOP_CELL * self.zoom
        return (
            self.ORIGIN_X + (x - self.camera_x) * cell,
            self.ORIGIN_Y + (y - self.camera_y) * cell,
        )

    def topdown_rect(self, x: int, y: int, inset: float = 0.0) -> Tuple[float, float, float, float]:
        sx, sy = self.topdown_to_screen(x, y)
        cell = self.TOP_CELL * self.zoom
        inset *= self.zoom
        return sx + inset, sy + inset, sx + cell - inset, sy + cell - inset

    def topdown_bounds(self) -> Tuple[range, range]:
        cell = self.TOP_CELL * max(0.25, self.zoom)
        half_x = min(56, max(14, math.ceil((self.WORLD_W / 2) / cell)))
        half_y = min(45, max(9, math.ceil((self.H - 120) / 2 / cell)))
        return (
            range(math.floor(self.camera_x) - half_x, math.floor(self.camera_x) + half_x + 1),
            range(math.floor(self.camera_y) - half_y, math.floor(self.camera_y) + half_y + 1),
        )

    def draw_topdown_fields(self) -> None:
        c = self.canvas
        xs, ys = self.topdown_bounds()
        for field in self.model.lithography_regions:
            if field["layer"] != self.active_layer:
                continue
            ox, oy = field["origin"]
            width, height = field["size"]
            tint = field["tint"]
            left, top = self.topdown_to_screen(ox, oy)
            right, bottom = self.topdown_to_screen(ox + width, oy + height)
            c.create_rectangle(left, top, right, bottom, outline=tint, width=2, dash=(6, 3))
            c.create_text(left + 5, top + 4, anchor="nw", text=f"{field['name']} // {width * height:,} LOCI", fill=tint, font=("TkFixedFont", 8, "bold"))
            pattern = field["pattern"]
            pitch = field["pitch"]
            if pattern in {"crosshatch", "grid"}:
                for x in range(max(xs.start, ox), min(xs.stop, ox + width)):
                    if (x - ox) % pitch == 0:
                        x1, y1 = self.topdown_to_screen(x, max(ys.start, oy))
                        x2, y2 = self.topdown_to_screen(x, min(ys.stop, oy + height))
                        c.create_line(x1, y1, x2, y2, fill=tint, width=1)
                for y in range(max(ys.start, oy), min(ys.stop, oy + height)):
                    if (y - oy) % pitch == 0:
                        x1, y1 = self.topdown_to_screen(max(xs.start, ox), y)
                        x2, y2 = self.topdown_to_screen(min(xs.stop, ox + width), y)
                        c.create_line(x1, y1, x2, y2, fill=tint, width=1)
            else:
                for x in range(max(xs.start, ox), min(xs.stop, ox + width)):
                    for y in range(max(ys.start, oy), min(ys.stop, oy + height)):
                        if pattern == "checker" and ((x - ox) + (y - oy)) % 2:
                            continue
                        x1, y1, x2, y2 = self.topdown_rect(x, y, 10)
                        c.create_rectangle(x1, y1, x2, y2, fill=tint, outline="")
            for tap in field["bus_taps"]:
                tx, ty = self.topdown_to_screen(tap[0], tap[1])
                c.create_oval(tx + 7, ty + 7, tx + self.TOP_CELL - 7, ty + self.TOP_CELL - 7, outline="#ffd185", width=2)
                c.create_text(tx + self.TOP_CELL / 2, ty + self.TOP_CELL / 2, text="TAP", fill="#ffd185", font=("TkFixedFont", 7, "bold"))

    def draw_topdown_connections(self) -> None:
        c = self.canvas
        xs, ys = self.topdown_bounds()
        visible = {(x, y) for x in xs for y in ys}
        layers_by_cell: Dict[GridCell, List[int]] = {}
        for (x, y, z), material in self.model.voxels.items():
            if z > 0 and (x, y) in visible and material in {"copper", "mask", "silicon", "via", "gold"}:
                layers_by_cell.setdefault((x, y), []).append(z)
        for (x, y), layers in layers_by_cell.items():
            layers = sorted(set(layers))
            if len(layers) < 2 and self.active_layer in layers:
                continue
            x1, y1, x2, y2 = self.topdown_rect(x, y, 3)
            c.create_rectangle(x1, y1, x2, y2, outline="#8bffff", width=2)
            c.create_rectangle(x1 + 4, y1 + 4, x1 + 9, y2 - 4, fill="#8bffff", outline="")
            c.create_text(x2 - 4, y1 + 4, anchor="ne", text="/".join(f"L{layer}" for layer in layers), fill="#b8ffff", font=("TkFixedFont", 7, "bold"))

    def draw_topdown_packet(self) -> None:
        cells = self.model.layer_bus_cells.get(self.active_layer, self.model.bus_cells)
        state = self.bus_packet_state(cells)
        if state is None or self.model.bus_health() <= 0.24:
            return
        first, second, fraction, direction, hop, hop_count = state
        a = self.topdown_to_screen(first[0] + 0.5, first[1] + 0.5)
        b = self.topdown_to_screen(second[0] + 0.5, second[1] + 0.5)
        point = (a[0] + (b[0] - a[0]) * fraction, a[1] + (b[1] - a[1]) * fraction)
        self.draw_packet_marker(point, b, "#ffe76b", f"PKT {direction.upper()}")

    def draw_topdown_direction(self, x: int, y: int, material: str, active: bool) -> None:
        direction = self.model.voxel_directions.get((x, y, self.active_layer), "east")
        if direction not in DIRECTIONS:
            return
        sx, sy = self.topdown_to_screen(x + 0.5, y + 0.5)
        vx, vy = self.direction_vector(direction)
        length = 11 + (4 * math.sin(self.frame / 6) if active else 0)
        ex = sx + vx * length
        ey = sy + vy * length
        mat = self.visual_material(material) or MATERIALS["via"]
        self.canvas.create_line(sx, sy, ex, ey, fill=mat.glow if active else "#38515a", width=2, arrow=tk.LAST)

    def draw_topdown_board(self) -> None:
        c = self.canvas
        xs, ys = self.topdown_bounds()
        for x in xs:
            for y in ys:
                x1, y1, x2, y2 = self.topdown_rect(x, y)
                fill = "#0c1d25" if (x + y) % 2 else "#10242d"
                c.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#1a3a45")
        self.draw_topdown_fields()
        bus_cells = self.model.layer_bus_cells.get(self.active_layer, self.model.bus_cells)
        for first, second in zip(bus_cells, bus_cells[1:]):
            a = self.topdown_to_screen(first[0] + 0.5, first[1] + 0.5)
            b = self.topdown_to_screen(second[0] + 0.5, second[1] + 0.5)
            c.create_line(a[0], a[1], b[0], b[1], fill="#73e8e2", width=4)
        for (x, y, z), material in self.model.voxels.items():
            if z != self.active_layer or not (xs.start <= x < xs.stop and ys.start <= y < ys.stop):
                continue
            x1, y1, x2, y2 = self.topdown_rect(x, y, 2)
            mat = self.visual_material(material)
            fill = mat.top if mat else "#1d5548"
            active = self.block_is_active(x, y, z, material)
            outline = mat.glow if active and mat else (mat.glow if mat else "#3ad9b9")
            c.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=3 if active else 2)
            if active and mat:
                pulse = 2 + int((math.sin(self.frame / 5 + x + y) + 1) * 2)
                c.create_oval(x1 - pulse, y1 - pulse, x2 + pulse, y2 + pulse, outline=mat.glow, width=1)
            if mat:
                c.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=mat.short, fill="#071118", font=("TkFixedFont", 7, "bold"))
                if material in DIRECTIONAL_BLOCKS or material in GATE_TYPES:
                    self.draw_topdown_direction(x, y, material, active)
        self.draw_topdown_connections()
        self.draw_topdown_packet()
        for chip in CHIPS:
            result = self.model.results[chip.code]
            for cell, required in chip.pattern.items():
                if self.active_layer == 1 and self.model.top_z(cell) in {0, None}:
                    x1, y1, x2, y2 = self.topdown_rect(cell[0], cell[1], 4)
                    c.create_rectangle(x1, y1, x2, y2, outline=chip.tint, width=2)
                    c.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=MATERIALS[required].short, fill=chip.tint, font=("TkFixedFont", 7, "bold"))
            lx, ly = self.topdown_to_screen(chip.anchor[0], chip.anchor[1] - 0.18)
            c.create_text(lx, ly, anchor="sw", text=f"{chip.code} {chip.name}", fill=self.GREEN if result.passed else chip.tint, font=("TkFixedFont", 8, "bold"))
        if self.target is not None:
            x1, y1, x2, y2 = self.topdown_rect(self.target[0], self.target[1], 1)
            c.create_rectangle(x1, y1, x2, y2, outline=self.CYAN, width=3)
        self.draw_preset_preview()
        sx, sy = self.topdown_to_screen(self.player_x + 0.5, self.player_y + 0.5)
        c.create_oval(sx - 9, sy - 9, sx + 9, sy + 9, fill=self.CYAN, outline="#ffffff", width=2)
        c.create_text(sx + 13, sy - 13, anchor="sw", text="ENGINEER", fill=self.CYAN, font=("TkFixedFont", 8, "bold"))
        self.panel_text(30, 100, f"TOP-DOWN BUILD // LAYER {self.active_layer:02d} // SQUARE SNAP ENABLED", fill=self.CYAN, size=9, bold=True)

    def draw_palette_scrollbar(self, page: int, pages: int, top: float, bottom: float, gate: bool = False) -> None:
        c = self.canvas
        track_x = self.WORLD_W - 70 if gate else self.WORLD_W - 62
        c.create_rectangle(track_x, top, track_x + 12, bottom, fill="#132a33", outline="#2b5962")
        thumb_h = max(12, (bottom - top) / max(1, pages))
        travel = max(0, bottom - top - thumb_h)
        thumb_y = top + travel * (page / max(1, pages - 1))
        c.create_rectangle(track_x + 2, thumb_y, track_x + 10, thumb_y + thumb_h, fill=self.CYAN if not gate else self.AMBER, outline="")

    def draw_hotbar(self) -> None:
        c = self.canvas
        bar_top = self.H - 102
        bar_bottom = self.H - 18
        c.create_rectangle(22, bar_top - 12, self.WORLD_W - 22, bar_bottom, fill="#0c1923", outline="#1e3c47")
        c.create_text(35, bar_top - 1, anchor="w", text="BUILD BLOCKS // SCROLL LIST", fill=self.MUTED, font=("TkFixedFont", 8, "bold"))
        visible_count = 10
        pages = max(1, (len(MATERIAL_ORDER) + visible_count - 1) // visible_count)
        self.material_page = min(self.material_page, pages - 1)
        start_index = self.material_page * visible_count
        slot_w = 142
        start_x = 118
        for local_index, key in enumerate(MATERIAL_ORDER[start_index:start_index + visible_count]):
            row, col = divmod(local_index, 5)
            x = start_x + col * slot_w
            y = bar_top + row * 37
            mat = MATERIALS[key]
            active = key == self.selected
            global_index = start_index + local_index
            keycap = str(global_index + 1) if global_index < 9 else ("0" if global_index == 9 else "·")
            c.create_rectangle(x, y, x + 132, y + 30, fill="#152834" if active else "#0d1c26", outline=mat.glow if active else "#24404a", width=2 if active else 1)
            c.create_rectangle(x + 7, y + 8, x + 20, y + 21, fill=mat.top, outline="")
            c.create_text(x + 27, y + 5, anchor="nw", text=f"{keycap} {mat.label}", fill=self.TEXT if active else self.MUTED, font=("TkFixedFont", 7, "bold"))
            supply = "∞" if self.model.infinite_supply else f"{self.model.inventory[key]:02d}"
            c.create_text(x + 27, y + 17, anchor="nw", text=f"{supply} {mat.help_text}", fill=mat.glow if active else "#55707b", font=("TkFixedFont", 6))
        self.draw_palette_scrollbar(self.material_page, pages, bar_top, bar_bottom - 10)
        c.create_text(self.WORLD_W - 35, bar_top - 1, anchor="e", text=f"BLOCKS {self.material_page + 1}/{pages}  ·  DIR {self.build_direction.upper()}  ·  ZOOM {self.zoom:0.2f}x", fill=self.AMBER, font=("TkFixedFont", 7, "bold"))

    def panel_text(self, x: float, y: float, text: str, fill: str = TEXT, size: int = 9, bold: bool = False, anchor: str = "nw") -> None:
        self.canvas.create_text(x, y, anchor=anchor, text=text, fill=fill, font=("TkFixedFont", size, "bold" if bold else "normal"))

    def editor_origin(self) -> Tuple[float, float]:
        width = self.EDITOR_COLS * self.EDITOR_CELL
        return ((self.WORLD_W - width) / 2, 150)

    def editor_cell_rect(self, cell: GridCell) -> Tuple[float, float, float, float]:
        ox, oy = self.editor_origin()
        x, y = cell
        return (ox + x * self.EDITOR_CELL, oy + y * self.EDITOR_CELL, ox + (x + 1) * self.EDITOR_CELL, oy + (y + 1) * self.EDITOR_CELL)

    def editor_port_center(self, chip: ChipSpec, face: str, index: int) -> Tuple[float, float]:
        ox, oy = self.editor_origin()
        count = chip.face_slots[face]
        if face in {"north", "south"}:
            x = ox + (index + 1) * (self.EDITOR_COLS * self.EDITOR_CELL) / (count + 1)
            y = oy - 30 if face == "north" else oy + self.EDITOR_ROWS * self.EDITOR_CELL + 30
        else:
            x = ox - 30 if face == "west" else ox + self.EDITOR_COLS * self.EDITOR_CELL + 30
            y = oy + (index + 1) * (self.EDITOR_ROWS * self.EDITOR_CELL) / (count + 1)
        return x, y

    def draw_chip_editor(self) -> None:
        c = self.canvas
        chip = next(item for item in CHIPS if item.code == self.active_chip_code)
        logic = self.model.chip_logic[chip.code]
        ox, oy = self.editor_origin()
        width = self.EDITOR_COLS * self.EDITOR_CELL
        height = self.EDITOR_ROWS * self.EDITOR_CELL
        c.create_rectangle(ox - 18, oy - 18, ox + width + 18, oy + height + 18, fill="#0c222c", outline=chip.tint, width=2)
        c.create_text(ox, oy - 55, anchor="sw", text=f"{chip.code}  {chip.name}  //  PARTICLE GATE ARRAY", fill=chip.tint, font=("TkFixedFont", 15, "bold"))
        self.panel_text(ox + width, oy - 55, "CLICK A GRID SLOT TO SNAP A GATE", fill=self.MUTED, size=8, bold=True, anchor="se")
        for y in range(self.EDITOR_ROWS):
            for x in range(self.EDITOR_COLS):
                x1, y1, x2, y2 = self.editor_cell_rect((x, y))
                gate_key = logic.gates.get((x, y))
                fill = "#132d38" if gate_key is None else GATE_TYPES[gate_key].color
                outline = "#244c58" if gate_key is None else "#e3ffff"
                c.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, fill=fill if gate_key else "#0f202a", outline=outline, width=2 if gate_key else 1)
                if gate_key:
                    gate = GATE_TYPES[gate_key]
                    c.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 7, text=gate.symbol, fill="#071118", font=("TkFixedFont", 18, "bold"))
                    c.create_text((x1 + x2) / 2, (y1 + y2) / 2 + 15, text=gate.label, fill="#071118", font=("TkFixedFont", 7, "bold"))
                else:
                    c.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="+", fill="#315362", font=("TkFixedFont", 15))
        for face, count in chip.face_slots.items():
            for index in range(count):
                px, py = self.editor_port_center(chip, face, index)
                connected = logic.ports[face][index]
                color = self.GREEN if connected else self.AMBER
                c.create_line(px, py, min(max(px, ox), ox + width), min(max(py, oy), oy + height), fill="#347b82" if connected else "#533c27", width=2)
                c.create_rectangle(px - 12, py - 12, px + 12, py + 12, fill="#173c3d" if connected else "#342919", outline=color, width=2)
                c.create_text(px, py, text=f"{face[0].upper()}{index + 1}", fill=color, font=("TkFixedFont", 7, "bold"))
        gate_ratio = min(1.0, len(logic.gates) / max(1, chip.gate_target))
        port_ratio = logic.connected_ports / max(1, chip.port_total)
        self.panel_text(ox, oy + height + 48, f"GATES  {len(logic.gates):02d}/{chip.gate_target:02d}", fill=self.CYAN, size=9, bold=True)
        self.panel_text(ox + 160, oy + height + 48, f"BUS PORTS  {logic.connected_ports:02d}/{chip.port_total:02d}", fill=self.GREEN if port_ratio == 1 else self.AMBER, size=9, bold=True)
        self.panel_text(ox + width, oy + height + 48, "L = EXPOSE THIS CHIP", fill=self.AMBER, size=9, bold=True, anchor="e")
        selected_gate = GATE_TYPES[self.selected_gate]
        self.panel_text(ox, oy + height + 89, f"Q-FAB // {selected_gate.particle} // {selected_gate.fabrication}", fill=selected_gate.color, size=7, bold=True)
        c.create_rectangle(ox, oy + height + 68, ox + width, oy + height + 75, fill="#162630", outline="")
        c.create_rectangle(ox, oy + height + 68, ox + width * ((gate_ratio + port_ratio) / 2), oy + height + 75, fill=chip.tint, outline="")

    def chip_at_cell(self, cell: GridCell) -> Optional[ChipSpec]:
        for chip in CHIPS:
            if cell in chip.pattern:
                return chip
        return None

    def nearest_chip(self) -> ChipSpec:
        return min(CHIPS, key=lambda chip: (chip.anchor[0] + 0.5 - self.player_x) ** 2 + (chip.anchor[1] + 0.5 - self.player_y) ** 2)

    def enter_chip_mode(self, chip: Optional[ChipSpec] = None) -> None:
        selected = chip or next(item for item in CHIPS if item.code == self.active_chip_code)
        self.active_chip_code = selected.code
        self.view = "chip"
        self.flight_mode = False
        self.place_preset_widgets()
        self.model.last_event = f"CHIP SCALE // editing {selected.name} / {selected.port_total} bus slots"

    def exit_chip_mode(self) -> None:
        self.view = "macro"
        self.place_preset_widgets()
        self.model.last_event = "FAB SCALE // returned to PCB floor"

    def editor_cell_at(self, sx: float, sy: float) -> Optional[GridCell]:
        ox, oy = self.editor_origin()
        x = int((sx - ox) // self.EDITOR_CELL)
        y = int((sy - oy) // self.EDITOR_CELL)
        if 0 <= x < self.EDITOR_COLS and 0 <= y < self.EDITOR_ROWS:
            return x, y
        return None

    def editor_port_at(self, chip: ChipSpec, sx: float, sy: float) -> Optional[Tuple[str, int]]:
        for face, count in chip.face_slots.items():
            for index in range(count):
                px, py = self.editor_port_center(chip, face, index)
                if (sx - px) ** 2 + (sy - py) ** 2 <= 18 ** 2:
                    return face, index
        return None

    def draw_monitor(self) -> None:
        """Render the independently scrollable monitor and graphical output."""
        c = self.sidebar_canvas
        sidebar_width = max(160, self.W - self.WORLD_W - 16)
        x0 = 18
        x1 = sidebar_width - 24
        # Keep the screen below the full chip queue, including larger JSON systems.
        screen_y = max(590, 367 + len(CHIPS) * 49 + 42)
        screen_bottom = screen_y + 420
        content_height = max(1120, screen_bottom + 125)
        self.sidebar_content_height = content_height
        viewport_height = max(1, self.H - 70)
        max_scroll = max(0.0, content_height - viewport_height)
        self.sidebar_scroll = min(max_scroll, max(0.0, self.sidebar_scroll))
        c.configure(scrollregion=(0, 0, sidebar_width, content_height))
        if max_scroll:
            self.sidebar_scrollbar.set(self.sidebar_scroll / content_height, (self.sidebar_scroll + viewport_height) / content_height)
        else:
            self.sidebar_scrollbar.set(0.0, 1.0)
        c.delete("all")

        offset = -self.sidebar_scroll

        def sy(value: float) -> float:
            return value + offset

        def text(x: float, y: float, value: str, fill: str = self.TEXT, size: int = 9, bold: bool = False, anchor: str = "nw") -> None:
            c.create_text(x, sy(y), anchor=anchor, text=value, fill=fill, font=("TkFixedFont", size, "bold" if bold else "normal"))

        def line(xa: float, ya: float, xb: float, yb: float, **kwargs: Any) -> None:
            c.create_line(xa, sy(ya), xb, sy(yb), **kwargs)

        def rect(xa: float, ya: float, xb: float, yb: float, **kwargs: Any) -> None:
            c.create_rectangle(xa, sy(ya), xb, sy(yb), **kwargs)

        text(x0, 22, "BUS MONITOR // LIVE", fill=self.TEXT, size=13, bold=True)
        text(x0, 47, "CHIPSET INPUT  ·  SCREEN OUTPUT", fill=self.TEAL, size=8, bold=True)
        text(x1, 24, "SCROLL", fill=self.MUTED, size=7, bold=True, anchor="ne")
        health = self.model.bus_health()
        if health > 0.82:
            status, status_color = "NOMINAL", self.GREEN
        elif health > 0.46:
            status, status_color = "DEGRADED", self.AMBER
        else:
            status, status_color = "FAULT", self.RED
        rect(x1 - 88, 18, x1, 43, fill="#132c2d" if status == "NOMINAL" else "#2d2419", outline=status_color)
        text(x1 - 44, 23, status, fill=status_color, size=8, bold=True, anchor="n")
        line(x0, 64, x1, 64, fill="#23404a")

        uptime = time.time() - self.started_at
        passed = sum(result.passed for result in self.model.results.values())
        exposed = sum(result.exposed for result in self.model.results.values())
        freq = self.model.base_clock_ghz + health * 2.7 + math.sin(self.frame / 19) * 0.06
        temp = 29.4 + health * 8.0 + math.sin(self.frame / 14) * 0.7
        load = 23 + passed * 14 + int((self.frame / 7) % 11)
        rows = [
            ("BUS HEALTH", f"{health * 100:05.1f}%", status_color),
            ("CLOCK", f"{freq:0.2f} GHz", self.CYAN),
            ("THERMAL", f"{temp:0.1f} C", self.AMBER if temp > 35 else self.GREEN),
            ("RUNTIME", f"{uptime:06.1f} s", self.TEXT),
            ("OPS / TICK", f"{load:02d} active", self.TEXT),
        ]
        for i, (label, value, color) in enumerate(rows):
            yy = 86 + i * 20
            text(x0, yy, label, fill=self.MUTED, size=8, bold=True)
            text(x1, yy, value, fill=color, size=9, bold=True, anchor="ne")
        line(x0, 192, x1, 192, fill="#23404a")

        text(x0, 208, "FAB PIPELINE", fill=self.TEXT, size=9, bold=True)
        pipeline = [
            ("INPUT", "schematic raster", self.CYAN),
            ("MASK", f"{exposed:02d} / {len(CHIPS):02d} exposed", self.AMBER),
            ("ETCH", f"{self.model.operations:03d} operations", self.TEAL),
            ("SCREEN", "output monitor online", self.GREEN if passed else self.MUTED),
        ]
        for i, (label, value, color) in enumerate(pipeline):
            yy = 232 + i * 22
            text(x0, yy, label, fill=color, size=8, bold=True)
            text(x0 + 70, yy, value, fill=self.TEXT, size=8)
            line(x0, yy + 16, x1, yy + 16, fill="#122936")

        text(x0, 340, "CHIP QUEUE", fill=self.TEXT, size=9, bold=True)
        for i, chip in enumerate(CHIPS):
            result = self.model.results[chip.code]
            yy = 367 + i * 49
            state = "PASS" if result.passed else ("FAIL" if result.exposed else "READY")
            state_color = self.GREEN if result.passed else (self.RED if result.exposed else chip.tint)
            text(x0, yy, chip.name, fill=self.TEXT, size=8, bold=True)
            logic = self.model.chip_logic[chip.code]
            text(x1, yy, f"{state} {result.matched}/{result.total}  G{len(logic.gates)}/{chip.gate_target} P{logic.connected_ports}/{chip.port_total}", fill=state_color, size=7, bold=True, anchor="ne")
            bar_x = x0
            bar_y = yy + 19
            bar_w = x1 - x0
            rect(bar_x, bar_y, bar_x + bar_w, bar_y + 7, fill="#162630", outline="")
            rect(bar_x, bar_y, bar_x + bar_w * result.ratio, bar_y + 7, fill=state_color, outline="")
            text(x0, yy + 29, chip.output if result.passed else ("pattern cells update as you deposit" if not result.exposed else "repair pattern, then use a fresh run"), fill="#66818a", size=7)

        # Dedicated graphical output area. It is intentionally taller than the
        # default sidebar viewport, so the scrollbar reveals the full display.
        # Keep the program telemetry in bounded rows: long cluster status text
        # must never run into the title or the latest program output.
        status_parts = self.model.program_status().split("  ")
        status_head = "  ".join(status_parts[:3])[:48]
        text(x0, screen_y - 52, "PROGRAM // LITHO-ISA", fill="#d6a7ff", size=8, bold=True)
        text(x1, screen_y - 52, status_head, fill=self.GREEN if not self.model.program_error else self.RED, size=7, bold=True, anchor="ne")
        if self.model.cluster_enabled:
            link_text = f"{self.model.cluster_link_name} // {self.model.cluster_last_transfer[:22]} // TX {self.model.cluster_transfers}"
            lane_text = "/".join(f"{worker['bus_value']:0.2f}" for worker in self.model.program_workers)
            text(x0, screen_y - 34, link_text[:48], fill="#82d9de", size=7)
            text(x1, screen_y - 34, f"LANES {lane_text}"[:48], fill="#ffe76b", size=7, bold=True, anchor="ne")
        if self.model.program_output:
            text(x0, screen_y - 17, "> " + self.model.program_output[-1][:48], fill="#9bbcc2", size=7)
        rect(x0, screen_y, x1, screen_bottom, fill="#06131b", outline="#3c9ca2", width=2)
        rect(x0 + 7, screen_y + 7, x1 - 7, screen_y + 31, fill="#102b32", outline="")
        screen_name = str(self.model.output_config.get("screen_name", "SCREEN OUTPUT // LIVE"))
        text(x0 + 14, screen_y + 12, screen_name, fill=self.CYAN, size=9, bold=True)
        text(x1 - 14, screen_y + 12, "ONLINE / FRAME 0x%04X" % (self.frame % 65536), fill=self.GREEN, size=7, bold=True, anchor="ne")
        text(x0 + 14, screen_y + 43, self.model.system_output(), fill=self.GREEN if passed else self.CYAN, size=8)
        text(x0 + 14, screen_y + 62, "> " + self.model.last_event, fill=self.AMBER if "FAIL" in self.model.last_event else self.CYAN, size=8)
        stream = "".join(self.rng.choice("01") for _ in range(32))
        text(x0 + 14, screen_y + 82, f"{self.model.bus_name}  {stream}", fill="#60989e", size=8)
        text(x0 + 14, screen_y + 101, f"FIELDS {len(self.model.lithography_regions):02d}  /  {self.model.lithography_cells_total:,} LOCI   ·   LAYER {self.active_layer:02d}", fill="#d08bf2", size=8, bold=True)
        active_packet = self.bus_packet_state(self.model.layer_bus_cells.get(self.active_layer, self.model.bus_cells))
        if active_packet is not None:
            _, _, _, packet_direction, packet_hop, packet_hops = active_packet
            text(x1 - 14, screen_y + 101, f"PACKET HOP {packet_hop + 1:02d}/{packet_hops:02d}  {packet_direction.upper()}", fill="#ffe76b", size=7, bold=True, anchor="ne")
        if self.model.equations:
            equation_index = (self.frame // 120) % len(self.model.equations)
            text(x0 + 14, screen_y + 120, "EQ // " + self.model.equation_text(equation_index), fill="#d6a7ff", size=7, bold=True)

        graph_left = x0 + 14
        graph_right = x1 - 14
        graph_top = screen_y + 140
        graph_bottom = screen_y + 285
        rect(graph_left, graph_top, graph_right, graph_bottom, fill="#031018", outline="#1c5962", width=1)
        text(graph_left + 8, graph_top + 8, "GRAPHICAL OUTPUT // LIVE CARRIER PLOT", fill="#83cfd3", size=7, bold=True)
        for grid in range(1, 5):
            gy = graph_top + 28 + grid * (graph_bottom - graph_top - 44) / 5
            line(graph_left + 5, gy, graph_right - 5, gy, fill="#12313b", dash=(2, 4))
        for grid in range(1, 9):
            gx = graph_left + grid * (graph_right - graph_left) / 9
            line(gx, graph_top + 22, gx, graph_bottom - 10, fill="#0d2730", dash=(2, 4))
        plot_left = graph_left + 8
        plot_right = graph_right - 8
        plot_top = graph_top + 28
        plot_bottom = graph_bottom - 12
        waveform = []
        for index in range(80):
            px = plot_left + index * (plot_right - plot_left) / 79
            signal = math.sin(self.frame / 6.0 + index * 0.48) * (0.22 + health * 0.18)
            signal += math.sin(self.frame / 19.0 + index * 0.12) * 0.12
            py = (plot_top + plot_bottom) / 2 - signal * (plot_bottom - plot_top)
            waveform.extend((px, py))
        c.create_line(*[value for pair in zip(waveform[0::2], waveform[1::2]) for value in pair], fill=self.GREEN if health > 0.46 else self.RED, width=2, smooth=True)
        line(plot_left, (plot_top + plot_bottom) / 2, plot_right, (plot_top + plot_bottom) / 2, fill="#1e4b53")
        for lane, layer in enumerate(sorted(self.model.layer_bus_cells)[:3]):
            lane_y = graph_bottom - 28 - lane * 16
            line(plot_left, lane_y, plot_right, lane_y, fill="#16424b", width=1)
            text(plot_left + 2, lane_y - 7, f"L{layer} BUS", fill="#5e9da4", size=6, bold=True)
            if health > 0.24:
                lane_packet = self.bus_packet_state(self.model.layer_bus_cells.get(layer, []))
                if lane_packet is not None:
                    _, _, lane_fraction, lane_direction, lane_hop, lane_hops = lane_packet
                    phase = (lane_hop + lane_fraction) / max(1, lane_hops)
                    particle_x = plot_left + phase * (plot_right - plot_left)
                    # The graph is time-oriented, so horizontal motion is the
                    # lane's packet flow; the live hop label above carries the
                    # actual spatial direction (including corners).
                    arrow = {
                        "east": ">", "west": "<", "north": "^", "south": "v",
                        "northeast": "^>", "northwest": "^<",
                        "southeast": "v>", "southwest": "v<",
                    }.get(lane_direction, "·")
                    c.create_oval(particle_x - 5, sy(lane_y) - 5, particle_x + 5, sy(lane_y) + 5, fill="#ffe76b", outline="#ffffff", width=1)
                    c.create_text(particle_x, sy(lane_y), text=arrow, fill="#071118", font=("TkFixedFont", 7, "bold"))

        text(x0 + 14, screen_y + 300, "CHIP OUTPUT CHANNELS", fill="#83cfd3", size=8, bold=True)
        channel_top = screen_y + 322
        channel_w = max(1, (x1 - x0 - 28) / max(1, len(CHIPS)))
        for index, chip in enumerate(CHIPS):
            result = self.model.results[chip.code]
            bar_left = x0 + 14 + index * channel_w
            bar_right = bar_left + channel_w - 8
            bar_top = channel_top + 25
            bar_bottom = channel_top + 96
            rect(bar_left, bar_top, bar_right, bar_bottom, fill="#0d232d", outline="#1a4650")
            fill_height = (bar_bottom - bar_top) * result.ratio
            rect(bar_left + 4, bar_bottom - fill_height, bar_right - 4, bar_bottom - 4, fill=chip.tint if not result.passed else self.GREEN, outline="")
            text((bar_left + bar_right) / 2, channel_top + 7, chip.code, fill=chip.tint, size=7, bold=True, anchor="n")
            text((bar_left + bar_right) / 2, bar_bottom + 8, "PASS" if result.passed else "WAIT", fill=self.GREEN if result.passed else self.AMBER, size=6, bold=True, anchor="n")

        controls_y = screen_bottom + 55
        controls = "SIDEBAR WHEEL / DRAG BAR TO SCROLL"
        text(x0 + 14, controls_y, controls, fill=self.MUTED, size=7)
        text(x0 + 14, controls_y + 18, "CTRL+S save   CTRL+P program editor   SCREEN OUTPUT = live computer display", fill=self.MUTED, size=7)
        text(x0 + 14, controls_y + 36, "PACKET ARROW = current hop direction", fill="#8faeb3", size=7)
        text(x0 + 14, controls_y + 54, "BOARD WHEEL zoom   CTRL+WHEEL/Q-E blocks   +/- zoom", fill=self.MUTED, size=7)

    def draw(self, include_monitor: bool = True) -> None:
        self.canvas.delete("all")
        self.model.refresh_results()
        self.draw_background()
        if self.view == "chip":
            self.draw_chip_editor()
            self.draw_gatebar()
        elif self.topdown:
            self.draw_topdown_board()
            self.draw_hotbar()
        else:
            self.draw_board_markings()
            self.draw_voxels()
            self.draw_target()
            self.draw_player()
            self.draw_hotbar()
        if include_monitor:
            self.draw_monitor()

    def screen_to_grid(self, sx: float, sy: float) -> GridCell:
        # Invert the isometric projection.  Mouse interaction operates on the
        # board surface, so the cursor's target is intentionally z-agnostic.
        if self.topdown:
            cell = self.TOP_CELL * self.zoom
            return (
                math.floor((sx - self.ORIGIN_X) / cell + self.camera_x),
                math.floor((sy - self.ORIGIN_Y) / cell + self.camera_y),
            )
        dx = (sx - self.ORIGIN_X) / (self.TILE_W * self.zoom / 2)
        dy = (sy - self.ORIGIN_Y) / (self.TILE_H * self.zoom / 2)
        return (math.floor((dx + dy) / 2 + self.camera_x + 0.5), math.floor((dy - dx) / 2 + self.camera_y + 0.5))

    def material_palette_area(self, x: float, y: float) -> bool:
        return x < self.WORLD_W and self.H - 114 <= y <= self.H - 18

    def gate_palette_area(self, x: float, y: float) -> bool:
        return x < self.WORLD_W and self.H - 94 <= y <= self.H - 18

    def palette_page_from_y(self, y: float, gate: bool = False) -> int:
        top = self.H - 84 if gate else self.H - 102
        bottom = self.H - 52 if gate else self.H - 28
        count = 4 if gate else 10
        total = len(GATE_ORDER) if gate else len(MATERIAL_ORDER)
        pages = max(1, (total + count - 1) // count)
        ratio = min(1.0, max(0.0, (y - top) / max(1, bottom - top)))
        return round(ratio * (pages - 1))

    def palette_hit(self, x: float, y: float, gate: bool = False) -> Optional[str]:
        if gate:
            top = self.H - 84
            if not self.gate_palette_area(x, y) or y < top - 2 or y > top + 30:
                return None
            local = int((x - 145) // 142)
            if not 0 <= local < 4:
                return None
            index = self.gate_page * 4 + local
            return GATE_ORDER[index] if index < len(GATE_ORDER) else None
        top = self.H - 102
        if not self.material_palette_area(x, y) or y < top or y >= top + 74:
            return None
        col = int((x - 118) // 142)
        row = int((y - top) // 37)
        if not 0 <= col < 5 or not 0 <= row < 2:
            return None
        index = self.material_page * 10 + row * 5 + col
        return MATERIAL_ORDER[index] if index < len(MATERIAL_ORDER) else None

    def on_palette_drag(self, event: tk.Event) -> None:
        if self.palette_dragging:
            self.material_page = self.palette_page_from_y(event.y)
        elif self.gate_palette_dragging:
            self.gate_page = self.palette_page_from_y(event.y, gate=True)

    def on_palette_release(self, event: tk.Event) -> None:
        self.palette_dragging = False
        self.gate_palette_dragging = False

    def cycle_choice(self, delta: int) -> None:
        if self.view == "chip":
            index = GATE_ORDER.index(self.selected_gate)
            self.selected_gate = GATE_ORDER[(index + delta) % len(GATE_ORDER)]
            self.model.last_event = f"GATE SELECT // {GATE_TYPES[self.selected_gate].label}"
            return
        index = MATERIAL_ORDER.index(self.selected)
        self.selected = MATERIAL_ORDER[(index + delta) % len(MATERIAL_ORDER)]
        self.model.last_event = f"BLOCK SELECT // {MATERIALS[self.selected].label}"

    def on_sidebar_scrollbar(self, *args: str) -> None:
        viewport_height = max(1, self.H - 70)
        max_scroll = max(0.0, self.sidebar_content_height - viewport_height)
        if not args:
            return
        if args[0] == "moveto" and len(args) > 1:
            self.sidebar_scroll = float(args[1]) * self.sidebar_content_height
        elif args[0] == "scroll" and len(args) > 1:
            amount = int(args[1])
            self.sidebar_scroll += amount * (viewport_height * 0.12 if len(args) < 3 or args[2] == "pages" else 36)
        self.sidebar_scroll = min(max_scroll, max(0.0, self.sidebar_scroll))
        self.draw_monitor()

    def on_sidebar_wheel(self, event: tk.Event) -> None:
        num = getattr(event, "num", None)
        if num == 4:
            delta = 1
        elif num == 5:
            delta = -1
        else:
            delta = 1 if getattr(event, "delta", 0) > 0 else -1
        self.sidebar_scroll -= delta * 48
        viewport_height = max(1, self.H - 70)
        max_scroll = max(0.0, self.sidebar_content_height - viewport_height)
        self.sidebar_scroll = min(max_scroll, max(0.0, self.sidebar_scroll))
        self.draw_monitor()

    def zoom_at(self, sx: float, sy: float, steps: int) -> None:
        """Zoom around a world point in either macro construction view."""
        if self.view == "chip" or sx >= self.WORLD_W:
            return
        old_zoom = self.zoom
        if self.topdown:
            world_x = self.camera_x + (sx - self.ORIGIN_X) / (self.TOP_CELL * old_zoom)
            world_y = self.camera_y + (sy - self.ORIGIN_Y) / (self.TOP_CELL * old_zoom)
        else:
            dx = (sx - self.ORIGIN_X) / (self.TILE_W * old_zoom / 2)
            dy = (sy - self.ORIGIN_Y) / (self.TILE_H * old_zoom / 2)
            world_x = self.camera_x + (dx + dy) / 2
            world_y = self.camera_y + (dy - dx) / 2
        self.zoom = min(6.0, max(0.25, old_zoom * (1.18 ** steps)))
        if self.topdown:
            self.camera_x = world_x - (sx - self.ORIGIN_X) / (self.TOP_CELL * self.zoom)
            self.camera_y = world_y - (sy - self.ORIGIN_Y) / (self.TOP_CELL * self.zoom)
        else:
            dx = (sx - self.ORIGIN_X) / (self.TILE_W * self.zoom / 2)
            dy = (sy - self.ORIGIN_Y) / (self.TILE_H * self.zoom / 2)
            self.camera_x = world_x - (dx + dy) / 2
            self.camera_y = world_y - (dy - dx) / 2
        self.camera_offset_x = self.camera_x - self.player_x
        self.camera_offset_y = self.camera_y - self.player_y
        self.model.last_event = f"ZOOM // {self.zoom:0.2f}x // {'TOP-DOWN' if self.topdown else 'ISO'}"

    def on_mouse_wheel(self, event: tk.Event) -> None:
        num = getattr(event, "num", None)
        if num == 4:
            delta = 1
        elif num == 5:
            delta = -1
        else:
            delta = 1 if getattr(event, "delta", 0) > 0 else -1
        if self.view == "chip" and self.gate_palette_area(getattr(event, "x", -1), getattr(event, "y", -1)):
            pages = max(1, (len(GATE_ORDER) + 3) // 4)
            self.gate_page = (self.gate_page - delta) % pages
        elif self.view != "chip" and self.material_palette_area(getattr(event, "x", -1), getattr(event, "y", -1)):
            pages = max(1, (len(MATERIAL_ORDER) + 9) // 10)
            self.material_page = (self.material_page - delta) % pages
        elif self.view != "chip" and (getattr(event, "state", 0) & 0x0004):
            self.cycle_choice(delta)
        else:
            self.zoom_at(getattr(event, "x", self.WORLD_W / 2), getattr(event, "y", self.H / 2), delta)

    def on_mouse_motion(self, event: tk.Event) -> None:
        if self.view == "chip":
            self.target = None
            return
        if event.x < self.WORLD_W:
            self.target = self.screen_to_grid(event.x, event.y)
        else:
            self.target = None

    def on_left_click(self, event: tk.Event) -> None:
        if self.view == "chip" and self.gate_palette_area(event.x, event.y):
            gate = self.palette_hit(event.x, event.y, gate=True)
            if gate:
                self.selected_gate = gate
                return
            if event.x >= self.WORLD_W - 100:
                self.gate_palette_dragging = True
                self.gate_page = self.palette_page_from_y(event.y, gate=True)
                return
        if self.view != "chip" and self.material_palette_area(event.x, event.y):
            material = self.palette_hit(event.x, event.y)
            if material:
                self.selected = material
                self.selected_preset = None
                self.preset_var.set("FREE BUILD")
                return
            if event.x >= self.WORLD_W - 100:
                self.palette_dragging = True
                self.material_page = self.palette_page_from_y(event.y)
                return
        if self.view == "chip":
            chip = next(item for item in CHIPS if item.code == self.active_chip_code)
            port = self.editor_port_at(chip, event.x, event.y)
            if port is not None:
                self.model.toggle_port(chip.code, port[0], port[1])
                return
            cell = self.editor_cell_at(event.x, event.y)
            if cell is not None:
                self.model.logic_place(chip.code, cell, self.selected_gate)
            return
        if event.x >= self.WORLD_W:
            return
        cell = self.screen_to_grid(event.x, event.y)
        chip = self.chip_at_cell(cell)
        if chip is not None and (event.state & 0x0001):
            self.enter_chip_mode(chip)
            return
        if self.selected_preset is not None:
            self.model.place_preset(cell, self.selected_preset, self.active_layer, self.build_direction)
        else:
            self.model.place(cell, self.selected, self.active_layer, self.build_direction)

    def on_right_click(self, event: tk.Event) -> None:
        if self.view == "chip":
            chip = next(item for item in CHIPS if item.code == self.active_chip_code)
            port = self.editor_port_at(chip, event.x, event.y)
            if port is not None:
                self.model.toggle_port(chip.code, port[0], port[1], False)
                return
            cell = self.editor_cell_at(event.x, event.y)
            if cell is not None:
                self.model.logic_break(chip.code, cell)
            return
        if event.x >= self.WORLD_W:
            return
        self.model.break_top(self.screen_to_grid(event.x, event.y), self.active_layer)

    def on_double_click(self, event: tk.Event) -> None:
        if self.view == "macro" and event.x < self.WORLD_W:
            chip = self.chip_at_cell(self.screen_to_grid(event.x, event.y))
            if chip is not None:
                self.enter_chip_mode(chip)

    def update_program_editor_status(self) -> None:
        if self.program_editor_status is not None and self.program_editor_status.winfo_exists():
            self.program_editor_status.configure(text=self.model.program_status())

    def _program_editor_source(self) -> str:
        if self.program_text_widget is None:
            return self.model.program_source
        return self.program_text_widget.get("1.0", "end-1c")

    def _program_editor_compile(self) -> bool:
        source = self._program_editor_source()
        try:
            if source != self.model.program_source:
                self.model.load_program(source)
            self.model.program_speed = min(512, max(1, int(self.program_speed_var.get())))
            self.update_program_editor_status()
            return True
        except ValueError as exc:
            self.model.program_error = str(exc)
            self.model.last_event = f"PROGRAM ERROR // {exc}"
            self.update_program_editor_status()
            messagebox.showerror("LITHO-ISA", str(exc), parent=self.program_editor_window)
            return False

    def program_editor_run(self) -> None:
        if self._program_editor_compile():
            self.model.start_program()
            self.update_program_editor_status()

    def program_editor_step(self) -> None:
        if not self._program_editor_compile():
            return
        if self.model.cluster_enabled:
            self.model.start_program(announce=False)
            self.model.run_program(1)
            self.model.stop_program(announce=False)
        else:
            self.model.stop_program(announce=False)
            self.model.step_program()
        self.update_program_editor_status()

    def program_editor_stop(self) -> None:
        self.model.stop_program()
        self.update_program_editor_status()

    def program_editor_reset(self) -> None:
        self.model.reset_program()
        self.update_program_editor_status()

    def program_editor_speed(self, value: str) -> None:
        self.model.program_speed = min(512, max(1, int(float(value))))
        self.update_program_editor_status()

    def program_editor_load_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="Load LITHO-ISA Program",
            initialdir=str(Path(__file__).parent),
            filetypes=[("LITHO-ISA source", "*.litho"), ("Text source", "*.txt"), ("All files", "*")],
            parent=self.program_editor_window,
        )
        if not selected or self.program_text_widget is None:
            return
        try:
            source = Path(selected).read_text(encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Load Program", str(exc), parent=self.program_editor_window)
            return
        self.program_text_widget.delete("1.0", "end")
        self.program_text_widget.insert("1.0", source)
        self.model.last_event = f"PROGRAM EDIT // loaded {Path(selected).name}"
        self.update_program_editor_status()

    def program_editor_save_file(self) -> None:
        if self.program_text_widget is None:
            return
        selected = filedialog.asksaveasfilename(
            title="Save LITHO-ISA Program",
            defaultextension=".litho",
            filetypes=[("LITHO-ISA source", "*.litho"), ("Text source", "*.txt"), ("All files", "*")],
            initialdir=str(Path(__file__).parent),
            parent=self.program_editor_window,
        )
        if not selected:
            return
        try:
            Path(selected).write_text(self._program_editor_source(), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Save Program", str(exc), parent=self.program_editor_window)
            return
        self.model.last_event = f"PROGRAM SAVE // {Path(selected).name}"
        self.update_program_editor_status()

    def open_program_editor(self) -> None:
        if self.program_editor_window is not None and self.program_editor_window.winfo_exists():
            self.program_editor_window.deiconify()
            self.program_editor_window.lift()
            return
        window = tk.Toplevel(self.root)
        self.program_editor_window = window
        window.title("LITHO-ISA // Computer Program")
        window.geometry("820x650")
        window.minsize(620, 460)
        window.configure(bg=self.PANEL)
        window.transient(self.root)
        window.protocol("WM_DELETE_WINDOW", lambda: self._close_program_editor())

        header = tk.Frame(window, bg=self.PANEL)
        header.pack(fill="x", padx=14, pady=(12, 5))
        tk.Label(header, text="LITHO-ISA PROGRAM CONSOLE", bg=self.PANEL, fg=self.CYAN, font=("TkFixedFont", 13, "bold")).pack(anchor="w")
        tk.Label(
            header,
            text="A tiny signal language for the fabricated computer: registers, noisy observation, Bayesian math, bus output, loops, and quantum-style operations.",
            bg=self.PANEL, fg=self.MUTED, justify="left", wraplength=780, font=("TkFixedFont", 8),
        ).pack(anchor="w", pady=(4, 0))

        editor_frame = tk.Frame(window, bg=self.PANEL)
        editor_frame.pack(fill="both", expand=True, padx=14, pady=6)
        scrollbar = tk.Scrollbar(editor_frame, orient="vertical")
        text_widget = tk.Text(
            editor_frame, wrap="none", undo=True, yscrollcommand=scrollbar.set,
            bg="#06131b", fg="#d8e7ef", insertbackground="#76eff4",
            selectbackground="#285d69", relief="flat", bd=0,
            font=("TkFixedFont", 10), padx=12, pady=10,
        )
        scrollbar.configure(command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.pack(side="left", fill="both", expand=True)
        text_widget.insert("1.0", self.model.program_source)
        self.program_text_widget = text_widget

        button_row = tk.Frame(window, bg=self.PANEL)
        button_row.pack(fill="x", padx=14, pady=(2, 4))
        button_style = {"bg": "#15313b", "fg": self.TEXT, "activebackground": "#2d5c68", "activeforeground": "#ffffff", "relief": "flat", "font": ("TkFixedFont", 8, "bold"), "padx": 10}
        for label, command in (
            ("RUN", self.program_editor_run),
            ("STEP", self.program_editor_step),
            ("STOP", self.program_editor_stop),
            ("RESET", self.program_editor_reset),
            ("LOAD .LITHO", self.program_editor_load_file),
            ("SAVE .LITHO", self.program_editor_save_file),
        ):
            tk.Button(button_row, text=label, command=command, **button_style).pack(side="left", padx=(0, 5))
        tk.Label(button_row, text="INSTRUCTIONS / FRAME", bg=self.PANEL, fg=self.MUTED, font=("TkFixedFont", 8, "bold")).pack(side="left", padx=(14, 5))
        speed = tk.Scale(
            button_row, from_=1, to=512, orient="horizontal", showvalue=True, length=170,
            variable=self.program_speed_var, command=self.program_editor_speed,
            bg=self.PANEL, fg=self.CYAN, troughcolor="#102a34", highlightthickness=0,
            activebackground=self.CYAN, font=("TkFixedFont", 8), resolution=1,
        )
        speed.pack(side="left")

        self.program_editor_status = tk.Label(window, text=self.model.program_status(), anchor="w", bg="#071820", fg=self.GREEN, font=("TkFixedFont", 8), padx=14, pady=7)
        self.program_editor_status.pack(fill="x", padx=14, pady=(0, 8))

    def _close_program_editor(self) -> None:
        if self.program_editor_window is not None and self.program_editor_window.winfo_exists():
            self.program_editor_window.destroy()
        self.program_editor_window = None
        self.program_text_widget = None
        self.program_editor_status = None

    def load_system_path(self, filename: Path) -> None:
        try:
            data = load_system_file(str(filename))
            self.model = LabModel(data)
            self.root.title(self.model.system_name)
            self.active_chip_code = CHIPS[0].code
            self.active_layer = 1
            self.view = "macro"
            self.topdown = False
            self.flight_mode = False
            self.camera_offset_x = 0.0
            self.camera_offset_y = 0.0
            self.camera_x = self.player_x
            self.camera_y = self.player_y
            ui_state = data.get("state", {}).get("ui", {}) if isinstance(data.get("state", {}), dict) else {}
            self.zoom = min(6.0, max(0.25, float(ui_state.get("zoom", 1.0)))) if isinstance(ui_state, dict) else 1.0
            self.selected_preset = None
            self.preset_var.set("FREE BUILD")
            self.save_path = filename.with_name("savegame.json")
            self.program_speed_var.set(self.model.program_speed)
            self.compute_speed_value.configure(text=f"{self.model.program_speed:03d} INST/TICK")
            if self.program_text_widget is not None and self.program_text_widget.winfo_exists():
                self.program_text_widget.delete("1.0", "end")
                self.program_text_widget.insert("1.0", self.model.program_source)
                self.update_program_editor_status()
            self.place_preset_widgets()
            self.model.last_event = f"LOAD PASS // {filename.name} // {len(CHIPS)} chips online"
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            messagebox.showerror("Load System", f"Could not load {filename.name}:\n{exc}")

    def load_system_dialog(self) -> None:
        selected = filedialog.askopenfilename(
            title="Load Lithography System",
            initialdir=str(Path(__file__).parent),
            filetypes=[("System JSON", "*.json"), ("All files", "*")],
        )
        if selected:
            self.load_system_path(Path(selected))

    def save_game(self, save_as: bool = False) -> None:
        filename = self.save_path
        if save_as:
            selected = filedialog.asksaveasfilename(
                title="Save Lithography System",
                defaultextension=".json",
                filetypes=[("JSON system save", "*.json"), ("All files", "*")],
                initialfile=filename.name,
                initialdir=str(filename.parent),
            )
            if not selected:
                return
            filename = Path(selected)
            self.save_path = filename
        self.model.save_json(str(filename), {
            "layer": self.active_layer,
            "topdown": self.topdown,
            "flight_mode": self.flight_mode,
            "player": [self.player_x, self.player_y, self.flight_altitude],
            "active_chip": self.active_chip_code,
            "preset": self.selected_preset,
            "direction": self.build_direction,
            "zoom": self.zoom,
        })
        self.model.last_event = f"SAVE PASS // {filename.name}"

    def on_key_down(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        was_down = key in self.keys
        self.keys.add(key)
        if key in {"w", "a", "s", "d", "up", "down", "left", "right", "space", "shift"} and was_down and not (event.state & 0x0004):
            return
        if key == "s" and (event.state & 0x0004):
            self.save_game(save_as=bool(event.state & 0x0001))
            return
        if key == "o" and (event.state & 0x0004):
            self.load_system_dialog()
            return
        if key == "p" and (event.state & 0x0004):
            self.open_program_editor()
            return
        if key.isdigit() and key != "0":
            index = int(key) - 1
            if self.view == "chip" and index < len(GATE_ORDER):
                self.selected_gate = GATE_ORDER[index]
            elif self.view != "chip" and index < len(MATERIAL_ORDER):
                self.selected = MATERIAL_ORDER[index]
        elif key == "0" and self.view != "chip" and len(MATERIAL_ORDER) >= 10:
            self.selected = MATERIAL_ORDER[9]
        elif key in {"q", "e"} and self.view != "chip":
            self.cycle_choice(-1 if key == "q" else 1)
        elif key == "r" and self.view == "macro":
            self.build_direction = DIRECTIONS[(DIRECTIONS.index(self.build_direction) + 1) % len(DIRECTIONS)]
            self.model.last_event = f"DIRECTION // {self.build_direction.upper()}"
        elif key == "t" and self.view == "macro":
            self.topdown = not self.topdown
            self.model.last_event = "TOP-DOWN BUILD // square snap online" if self.topdown else "ISO BUILD // voxel perspective restored"
        elif key == "z":
            if self.view == "chip":
                self.exit_chip_mode()
            else:
                self.enter_chip_mode(self.nearest_chip())
        elif key == "f" and self.view == "macro":
            self.flight_mode = not self.flight_mode
            self.model.last_event = "FLIGHT MODE // thrusters online" if self.flight_mode else "WALK MODE // board contact restored"
        elif key in {"plus", "equal"} and self.view == "macro":
            self.zoom_at(self.WORLD_W / 2, self.H / 2, 1)
        elif key in {"minus", "underscore"} and self.view == "macro":
            self.zoom_at(self.WORLD_W / 2, self.H / 2, -1)
        elif key in {"pageup", "prior"} and self.view == "macro":
            self.active_layer = min(32, self.active_layer + 1)
            self.model.last_event = f"LAYER SHIFT // viewing L{self.active_layer:02d}"
        elif key in {"pagedown", "next"} and self.view == "macro":
            self.active_layer = max(1, self.active_layer - 1)
            self.model.last_event = f"LAYER SHIFT // viewing L{self.active_layer:02d}"
        elif key == "l":
            self.model.scan(self.active_chip_code if self.view == "chip" else None)
            self.message_flash = 16
        elif key == "[" and self.view == "macro":
            index = next(i for i, chip in enumerate(CHIPS) if chip.code == self.active_chip_code)
            self.active_chip_code = CHIPS[(index - 1) % len(CHIPS)].code
        elif key == "]" and self.view == "macro":
            index = next(i for i, chip in enumerate(CHIPS) if chip.code == self.active_chip_code)
            self.active_chip_code = CHIPS[(index + 1) % len(CHIPS)].code
        elif key == "escape":
            if self.view == "chip":
                self.exit_chip_mode()
            else:
                self.root.destroy()

    def on_key_up(self, event: tk.Event) -> None:
        self.keys.discard(event.keysym.lower())

    def update_player(self, delta_seconds: float = 1.0 / 24.0) -> None:
        if self.view == "chip":
            return
        delta_seconds = min(0.08, max(0.0, float(delta_seconds)))
        speed = (7.0 if self.flight_mode else 4.5) * delta_seconds
        dx = (1 if "d" in self.keys or "right" in self.keys else 0) - (1 if "a" in self.keys or "left" in self.keys else 0)
        dy = (1 if "s" in self.keys or "down" in self.keys else 0) - (1 if "w" in self.keys or "up" in self.keys else 0)
        if dx or dy:
            length = math.sqrt(dx * dx + dy * dy)
            if self.flight_mode:
                max_x, max_y = self.player_x + 100000.0, self.player_y + 100000.0
                min_x, min_y = self.player_x - 100000.0, self.player_y - 100000.0
            else:
                max_x, max_y = self.player_x + 100000.0, self.player_y + 100000.0
                min_x, min_y = self.player_x - 100000.0, self.player_y - 100000.0
            self.player_x = min(max_x, max(min_x, self.player_x + dx / length * speed))
            self.player_y = min(max_y, max(min_y, self.player_y + dy / length * speed))
        if self.flight_mode:
            altitude_axis = (1 if "space" in self.keys else 0) - (1 if "shift" in self.keys else 0)
            self.flight_altitude = min(32.0, max(1.8, self.flight_altitude + altitude_axis * 2.0 * delta_seconds))
        self.camera_x = self.player_x + self.camera_offset_x
        self.camera_y = self.player_y + self.camera_offset_y

    def animate(self) -> None:
        if not self.root.winfo_exists():
            return
        now = time.perf_counter()
        delta_seconds = min(0.08, max(0.0, now - self.last_tick_time))
        self.last_tick_time = now
        self.frame += 1
        self.cycles += 1
        self.update_player(delta_seconds)
        self.model.run_program()
        self.update_program_editor_status()
        # Input and simulation stay responsive at a fast cadence; expensive
        # canvas composition is intentionally amortized across ticks.
        if self.frame % self.render_stride == 0:
            self.draw(include_monitor=(self.frame % self.monitor_stride == 0))
        self.root.after(16, self.animate)

    def run(self) -> None:
        self.root.mainloop()


def self_test() -> None:
    # The normal default is intentionally a live computer.  Use a clean copy
    # here so the fabrication mechanics can still be tested from bare PCB.
    boot_model = LabModel()
    assert all(result.passed for result in boot_model.results.values())
    assert "ALL CHIP PATHS NOMINAL" in boot_model.system_output()
    test_config = json.loads(json.dumps(SYSTEM_CONFIG))
    test_config["boot_working"] = False
    model = LabModel(test_config)
    assert model.top_material((3, 2)) == "pcb"
    assert model.place((3, 2), "silicon")
    assert model.top_material((3, 2)) == "silicon"
    assert model.break_top((3, 2))
    assert model.top_material((3, 2)) == "pcb"
    for chip in CHIPS:
        model.full_pattern_for(chip)
        model.refresh_results()
    assert all(result.matched == result.total for result in model.results.values())
    for chip in CHIPS:
        model.auto_complete_logic(chip)
    for _ in CHIPS:
        model.scan()
    assert all(result.passed for result in model.results.values())
    assert model.bus_health() > 0.75
    print("Lithography Voxel Lab self-test: PASS")
    print(f"  chips passed: {sum(result.passed for result in model.results.values())}/{len(CHIPS)}")
    print(f"  operations:   {model.operations}")
    print(f"  bus health:   {model.bus_health() * 100:.1f}%")


def main() -> None:
    if "--self-test" in sys.argv:
        self_test()
        return
    system_file: Optional[str] = None
    if "--system" in sys.argv:
        flag_index = sys.argv.index("--system")
        if flag_index + 1 >= len(sys.argv):
            raise SystemExit("--system needs a JSON filename")
        system_file = sys.argv[flag_index + 1]
    else:
        positional = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
        if positional and positional[0].lower().endswith(".json"):
            system_file = positional[0]
    if system_file:
        try:
            load_system_file(system_file)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise SystemExit(f"Could not load system JSON: {exc}") from exc
    app = LithoLab()
    app.run()


if __name__ == "__main__":
    main()
