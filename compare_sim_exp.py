import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd

# Defaults matching project
ROOT = Path(__file__).resolve().parent
SIM_DIR = ROOT / 'single_brace_simu'
EXCEL_FILE = ROOT / 'revise.xlsx'

# default geometry from project
DEFAULT_L_BRACE = 5060.0
DEFAULT_D_ED = 44.0

# ratchet row ranges used previously
DEFAULT_STATIC_RATCHET_ROWS = (1, 13)
DEFAULT_FATIGUE_RATCHET_ROWS = (16, 41)


def load_sim_xy(sim_out_dir: Path, l_brace=DEFAULT_L_BRACE, d_ed=DEFAULT_D_ED):
    """Load simulation Brace force-displacement from recorder output files.
    Expects file BraceTest2Ratchet.out with columns [stress, strain, ...]
    Computes force (kN) = stress * a_ed / 1e3 and disp (mm) = strain * l_brace
    """
    p = Path(sim_out_dir)
    f = p / 'BraceTest2Ratchet.out'
    if not f.exists():
        raise FileNotFoundError(f"Simulation output missing: {f}")
    arr = np.loadtxt(f)
    if arr.ndim == 1:
        # single row
        arr = arr.reshape(1, -1)
    stress = arr[:, 0]
    strain = arr[:, 1]
    a_ed = np.pi * d_ed ** 2 / 4.0
    force = stress * a_ed / 1e3
    disp = strain * l_brace
    return disp, force


# reuse helper logic similar to plot_from_revise
def rows_to_ranges_from_df(df_ratchet: pd.DataFrame, start_row: int, end_row: int):
    start_idx = max(0, start_row - 1)
    end_idx = min(len(df_ratchet), end_row)
    ranges = []
    for r in range(start_idx, end_idx):
        row = df_ratchet.iloc[r]
        try:
            s = int(row.iloc[0])
            e = int(row.iloc[2])
            ranges.append((s, e))
        except Exception:
            continue
    return ranges


def build_xy_from_arrays(y_vals, e_vals, ranges):
    N = len(y_vals)
    x = np.zeros(N)
    for i in range(1, N):
        one_based = i + 1
        in_range = any(start <= one_based < end for (start, end) in ranges)
        if in_range:
            x[i] = x[i-1] + (e_vals[i] - e_vals[i-1])
        else:
            x[i] = x[i-1]
    return x, np.array(y_vals)


def load_exp_xy_from_excel(excel_path: Path, sheet_name: str, y_col='A', e_col='E',
                           ratchet_ranges=(2, 13)):
    xl = pd.ExcelFile(excel_path)
    df = xl.parse(sheet_name)
    df_ratchet = xl.parse('ratchet')

    # simple column fallback mapping
    def get_col(df_local, col_letter):
        if col_letter in df_local.columns:
            return df_local[col_letter].to_numpy()
        mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'H': 7}
        idx = mapping.get(col_letter)
        if idx is None or idx >= df_local.shape[1]:
            raise KeyError(f"Column {col_letter} not found and fallback failed")
        return df_local.iloc[:, idx].to_numpy()

    y = get_col(df, y_col)
    e = get_col(df, e_col)
    ranges = rows_to_ranges_from_df(df_ratchet, ratchet_ranges[0], ratchet_ranges[1])
    x, y_arr = build_xy_from_arrays(y, e, ranges)
    # clamp negative values to zero
    y_arr = np.maximum(y_arr, 0)
    return x, y_arr


def plot_compare(x_sim, y_sim, x_exp, y_exp, title, out_path: Path):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_sim, y_sim, label='Simulated', linewidth=1.0)
    ax.plot(x_exp, y_exp, label='Experimental', linewidth=1.0)
    ax.set_xlabel('Disp (mm) / X')
    ax.set_ylabel('Force or Y')
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(out_path)
    print(f'Saved {out_path}')


def produce_comparisons(
    excel_path: Path = EXCEL_FILE,
    sim_root: Path = SIM_DIR,
    l_brace: float = DEFAULT_L_BRACE,
    d_ed: float = DEFAULT_D_ED,
    out_dir: Path | str = ROOT,
    static_ratchet_rows=DEFAULT_STATIC_RATCHET_ROWS,
    fatigue_ratchet_rows=DEFAULT_FATIGUE_RATCHET_ROWS,
):
    out_dir = Path(out_dir)
    # Static
    sim_static_dir = sim_root / 'static.out'
    x_sim_s, y_sim_s = load_sim_xy(sim_static_dir, l_brace=l_brace, d_ed=d_ed)
    x_exp_s, y_exp_s = load_exp_xy_from_excel(excel_path, 'Static', y_col='A', e_col='E', ratchet_ranges=static_ratchet_rows)
    out_static = out_dir / 'compare_static.png'
    plot_compare(x_sim_s, y_sim_s, x_exp_s, y_exp_s, 'Static: Sim vs Exp', out_static)

    # Fatigue
    sim_fat_dir = sim_root / 'fatigue.out'
    x_sim_f, y_sim_f = load_sim_xy(sim_fat_dir, l_brace=l_brace, d_ed=d_ed)
    x_exp_f, y_exp_f = load_exp_xy_from_excel(excel_path, 'Fatigue', y_col='A', e_col='H', ratchet_ranges=fatigue_ratchet_rows)
    out_fat = out_dir / 'compare_fatigue.png'
    plot_compare(x_sim_f, y_sim_f, x_exp_f, y_exp_f, 'Fatigue: Sim vs Exp', out_fat)

    return out_static, out_fat


if __name__ == '__main__':
    try:
        # run the simulation script first (uses same Python executable)
        import sys, subprocess
        subprocess.run([sys.executable, str(Path(__file__).parent / 'single_brace_simu.py')], check=True)

        output_path = Path(__file__).parent / 'ratchet_plots'
        s, f = produce_comparisons(out_dir=output_path)
        print('Produced comparison plots:', s, f)
    except Exception as e:
        print('Error:', e)
