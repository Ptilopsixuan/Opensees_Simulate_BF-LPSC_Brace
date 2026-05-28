"""
analyze_brace_results.py

Load recorder output files from the .out directory and reproduce the MATLAB plotting
from AHSC_TOB_simulation_v31.m. Saves figures into .out and optionally shows them.

Designed to be robust to missing files and to run without MATLAB.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import sys

# Default geometric/material values (match simulation defaults)
L_BRACE_DEF = 5060.0
L_ED_DEF = 1800.0
D_ED_DEF = 44.0  # mm

OUT_DIR = Path(__file__).resolve().parent / '.out'
OUT_DIR.mkdir(exist_ok=True)

# Helper to load text file safely
def load_out(name):
    p = OUT_DIR / name
    if not p.exists():
        print(f"Warning: {p} not found.")
        return None
    try:
        arr = np.loadtxt(p)
    except Exception as e:
        print(f"Failed to load {p}: {e}")
        return None
    # np.loadtxt returns an empty 1d array for empty files; treat as missing
    if arr.size == 0:
        print(f"Warning: {p} contains no data.")
        return None
    return arr


def _validate_cols(data, name: str, min_cols: int) -> bool:
    if data is None:
        return False
    if data.ndim == 1:
        # single-column or single-row — cannot parse into columns safely
        print(f"Warning: {name} has unexpected 1D shape; skipping plot.")
        return False
    if data.shape[1] < min_cols:
        print(f"Warning: {name} has only {data.shape[1]} columns; need >= {min_cols}.")
        return False
    return True


def plot_brace_stress_strain(a_ed=None, l_brace=None):
    data = load_out('BraceTest2BraceStreeStrain.out')
    if not _validate_cols(data, 'BraceTest2BraceStreeStrain.out', 2):
        return
    a_ed = a_ed or (np.pi * D_ED_DEF ** 2 / 4.0)
    l_brace = l_brace or L_BRACE_DEF

    force = data[:, 0] * a_ed / 1e3  # kN
    disp = data[:, 1] * l_brace      # mm

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(disp, force, '--', linewidth=2, color=(192/255, 0, 0))
    ax.set_ylabel('Force (kN)')
    ax.set_xlabel('Deformation (mm)')
    ax.grid(True)
    ax.set_title('Brace Force - Deformation')
    fig.tight_layout()
    outp = OUT_DIR / 'Brace_Force_Displacement.png'
    fig.savefig(outp)
    print(f'Saved {outp}')


def plot_ed_stress_strain(l_ed=None, l_brace=None):
    data = load_out('BraceTest2Dissipator.out')
    if not _validate_cols(data, 'BraceTest2Dissipator.out', 2):
        return
    l_ed = l_ed or L_ED_DEF
    l_brace = l_brace or L_BRACE_DEF
    r_ed = l_ed / l_brace
    a_ed = np.pi * D_ED_DEF ** 2 / 4.0

    stress = data[:, 0]
    strain = data[:, 1] / r_ed
    disp = (data[:, 2] if data.shape[1] > 2 else data[:, 1]) / r_ed * l_ed

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(strain, stress, color='k', linewidth=1)
    ax.set_ylabel('Stress (MPa)')
    ax.set_xlabel('Strain')
    ax.grid(True)
    fig.tight_layout()
    outp = OUT_DIR / 'ED_Stress_Strain.png'
    fig.savefig(outp)
    print(f'Saved {outp}')


def plot_ratchet():
    data = load_out('BraceTest2Ratchet.out')
    if not _validate_cols(data, 'BraceTest2Ratchet.out', 2):
        return
    l_brace = L_BRACE_DEF
    a_ed = np.pi * D_ED_DEF ** 2 / 4.0
    force = data[:, 0] * a_ed / 1000.0
    disp = data[:, 1] * l_brace

    fig, ax = plt.subplots()
    ax.plot(disp, force, color='r', linewidth=0.8)
    ax.set_title('Ratchet Force - Disp')
    ax.set_ylabel('Force (kN)')
    ax.set_xlabel('Disp (mm)')
    ax.grid(True)
    outp = OUT_DIR / 'Ratchet_Force_Disp.png'
    fig.savefig(outp)
    print(f'Saved {outp}')


def plot_ratchet_system():
    data = load_out('BraceTest2RatchetSystem.out')
    if not _validate_cols(data, 'BraceTest2RatchetSystem.out', 2):
        return
    fig, ax = plt.subplots()
    ax.plot(data[:, 2] if data.shape[1] > 2 else data[:, 1], data[:, 0], color='r', linewidth=0.8)
    ax.set_title('Ratchet System Force - Disp')
    ax.set_xlabel('Brace Disp (mm)')
    ax.set_ylabel('Prestressing element Force (kN)')
    ax.grid(True)
    outp = OUT_DIR / 'RatchetSystem_Force_Disp.png'
    fig.savefig(outp)
    print(f'Saved {outp}')


def plot_spring():
    data = load_out('BraceTest2Spring.out')
    if not _validate_cols(data, 'BraceTest2Spring.out', 2):
        return
    a_ed = np.pi * D_ED_DEF ** 2 / 4.0
    force = data[:, 0] * a_ed / 1000.0
    disp = data[:, 1] * L_BRACE_DEF
    fig, ax = plt.subplots()
    ax.plot(disp, force, color='r', linewidth=0.8)
    ax.set_title('Spring Force - Disp')
    ax.set_xlabel('Disp (mm)')
    ax.set_ylabel('Force (kN)')
    ax.grid(True)
    outp = OUT_DIR / 'Spring_Force_Disp.png'
    fig.savefig(outp)
    print(f'Saved {outp}')


def main(show: bool = False):
    # attempt to load parameter file if present
    # otherwise use defaults
    # Run plots
    plot_brace_stress_strain()
    plot_ed_stress_strain()
    plot_ratchet()
    plot_ratchet_system()
    plot_spring()

    if show:
        plt.show()


if __name__ == '__main__':
    show = ('--show' in sys.argv)
    main(show)
