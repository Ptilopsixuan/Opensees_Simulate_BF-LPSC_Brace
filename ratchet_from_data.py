import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from lib.pic_setter import pic_setting

EXCEL_FILE = Path(__file__).resolve().parent / 'revise.xlsx'

# Default ratchet row ranges (1-based, inclusive). Adjust if your file differs.
DEFAULT_STATIC_RATCHET_ROWS = (1, 13)
DEFAULT_FATIGUE_RATCHET_ROWS = (16, 46)
DEFAULT_DYNAMIC_RATCHET_ROWS = (49, 64)


def build_xy(y_vals, e_vals, ratchet_rows):
    """
    y_vals, e_vals: 1D arrays (ordered as in sheet, first data row corresponds to index 1)
    ratchet_rows: iterable of (start_row, end_row) tuples OR a single pair (start,end)
    Note: ratchet row numbers are 1-based and refer to the data-row index in the sheet (headers already considered).
    Behavior:
      - create N points where N = len(y_vals)
      - x0 = 0
      - for i from 1..N-1 (0-based indices):
          if i (1-based index) falls in any [start, end) range (i.e., start <= (i+1) < end):
              x[i] = x[i-1] + (E[i] - E[i-1])
          else:
              x[i] = x[i-1]
    """
    N = len(y_vals)
    x = np.zeros(N)
    # normalize ratchet_rows into list of (start,end)
    ranges = []
    if ratchet_rows is None:
        ranges = []
    elif isinstance(ratchet_rows[0], (list, tuple)):
        ranges = list(ratchet_rows)
    else:
        ranges = ratchet_rows

    for i in range(1, N):
        one_based = i + 1
        in_range = any(start <= one_based < end for (start, end) in ranges)
        if in_range:
            x[i] = x[i-1] + (e_vals[i] - e_vals[i-1])
        else:
            x[i] = x[i-1]
    return x, np.array(y_vals)


def get_col(df, col_letter):
    """Return numpy array for requested column letter or positional fallback."""
    if col_letter in df.columns:
        return df[col_letter].to_numpy()
    mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'H': 7}
    idx = mapping.get(col_letter)
    if idx is None or idx >= df.shape[1]:
        raise KeyError(f"Column {col_letter} not found and fallback failed")
    return df.iloc[:, idx].to_numpy()


def rows_to_ranges(df_ratchet, start_row, end_row):
    """Convert ratchet worksheet rows to list of (start,end) ranges.

    Assumes ratchet sheet rows contain start in first column (A) and end in C.
    start_row/end_row are 1-based inclusive indices selecting which rows in ratchet sheet
    to parse for ranges.
    """
    start_idx = max(0, start_row - 1)
    end_idx = min(len(df_ratchet), end_row)
    ranges = []
    for r in range(start_idx, end_idx):
        row = df_ratchet.iloc[r]
        try:
            s = int(row.iloc[0])
            e = int(row.iloc[2])
            # Treat end value in sheet as inclusive; convert to exclusive end
            # to match build_xy which expects ranges as [start, end) using 1-based indices.
            ranges.append((s, e + 1))
        except Exception:
            continue
    return ranges


def clamp_negative(y_array):
    return np.maximum(y_array, 0)


def get_ratchet_xy(
    excel_path: Path | str = EXCEL_FILE,
    static_sheet: str = 'Static',
    fatigue_sheet: str = 'Fatigue',
    dynamic_sheet: str = 'Dynamic',
    ratchet_sheet: str = 'ratchet',
    static_rows: tuple = DEFAULT_STATIC_RATCHET_ROWS,
    fatigue_rows: tuple = DEFAULT_FATIGUE_RATCHET_ROWS,
    dynamic_rows: tuple = DEFAULT_DYNAMIC_RATCHET_ROWS,
    y_col_static: str = 'A',
    e_col_static: str = 'E',
    y_col_fatigue: str = 'A',
    e_col_fatigue: str = 'H',
    y_col_dynamic: str = 'A',
    e_col_dynamic: str = 'B',
    clamp_neg_y: bool = True,
    out_dir: Path | str = Path(__file__).resolve().parent,
):
    """Read experiment Excel and compute ratchet curve coordinates.

    Returns: ((x_static, y_static), (x_fatigue, y_fatigue), (x_dynamic, y_dynamic))
    """
    excel_path = Path(excel_path)
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    xl = pd.ExcelFile(excel_path)
    required = {static_sheet, fatigue_sheet, dynamic_sheet, ratchet_sheet}
    if not required.issubset(set(xl.sheet_names)):
        raise ValueError(f"Missing sheets in {excel_path}: {xl.sheet_names}")

    df_static = xl.parse(static_sheet)
    df_fatigue = xl.parse(fatigue_sheet)
    df_dynamic = xl.parse(dynamic_sheet)
    df_ratchet = xl.parse(ratchet_sheet)

    y_static = get_col(df_static, y_col_static)
    e_static = get_col(df_static, e_col_static)
    y_fatigue = get_col(df_fatigue, y_col_fatigue)
    e_fatigue = get_col(df_fatigue, e_col_fatigue)
    y_dynamic = get_col(df_dynamic, y_col_dynamic)
    e_dynamic = get_col(df_dynamic, e_col_dynamic)


    static_ranges = rows_to_ranges(df_ratchet, static_rows[0], static_rows[1])
    fatigue_ranges = rows_to_ranges(df_ratchet, fatigue_rows[0], fatigue_rows[1])
    dynamic_ranges = rows_to_ranges(df_ratchet, dynamic_rows[0], dynamic_rows[1])

    x_static, y_static_arr = build_xy(y_static, e_static, static_ranges)
    x_fatigue, y_fatigue_arr = build_xy(y_fatigue, e_fatigue, fatigue_ranges)
    x_dynamic, y_dynamic_arr = build_xy(y_dynamic, e_dynamic, dynamic_ranges)

    if clamp_neg_y:
        y_static_arr = clamp_negative(y_static_arr)
        y_fatigue_arr = clamp_negative(y_fatigue_arr)
        y_dynamic_arr = clamp_negative(y_dynamic_arr)

    return (x_static, y_static_arr), (x_fatigue, y_fatigue_arr), (x_dynamic, y_dynamic_arr)



if __name__ == '__main__':
    try:
        excel_path = Path(__file__).resolve().parent / 'revise.xlsx'
        output_path = Path(__file__).resolve().parent / 'ratchet_plots'
        (x_static, y_static), (x_fatigue, y_fatigue), (x_dynamic, y_dynamic) = get_ratchet_xy(excel_path)

        # helper to choose reasonable tick spacing
        plt.rcParams["font.family"] = "Times New Roman"

        # Static plot
        fig, ax = pic_setting(4.5, 4, 9,
                            #   x_label='Disp (mm)', y_label='Force (kN)',
                              x_min=-400, x_max=25,
                              y_min=0, y_max=1000,
                              x_major_locator=100, x_minor_locator=25,
                              y_major_locator=200, y_minor_locator=50)
        ax.plot(x_static, y_static, linewidth=0.5, color='#66ccff')
        outp = output_path / 'static_processed.png'
        fig.savefig(outp)
        print(f'Saved {outp}')

        # Fatigue plot
        fig, ax = pic_setting(4.5, 4 , 9,
                            #   x_label='Disp (mm)', y_label='Force (kN)',
                              x_min=-800, x_max=50,
                              y_min=0, y_max=1000,
                              x_major_locator=200, x_minor_locator=50,
                              y_major_locator=200, y_minor_locator=50)
        ax.plot(x_fatigue, y_fatigue, linewidth=0.5, color='#66ccff')
        outp2 = output_path / 'fatigue_processed.png'
        fig.savefig(outp2)
        print(f'Saved {outp2}')

        # Dynamic plot
        fig, ax = pic_setting(4.5, 4 , 9,
                            #   x_label='Disp (mm)', y_label='Force (kN)',
                              x_min=-600, x_max=50,
                              y_min=0, y_max=1000,
                              x_major_locator=100, x_minor_locator=25,
                              y_major_locator=200, y_minor_locator=50)
        ax.plot(x_dynamic, y_dynamic, linewidth=0.5, color='#66ccff')
        outp3 = output_path / 'dynamic_processed.png'
        fig.savefig(outp3)
        print(f'Saved {outp3}')

        # # Dynamic plot with segmented colors per ratchet ranges
        # # predefined colors
        # colors = ['#66ccff', '#ff9999', '#99ff99']

        # # reload ratchet ranges from sheet
        # xl = pd.ExcelFile(excel_path)
        # df_ratchet = xl.parse('ratchet')
        # dynamic_ranges = rows_to_ranges(df_ratchet, DEFAULT_DYNAMIC_RATCHET_ROWS[0], DEFAULT_DYNAMIC_RATCHET_ROWS[1])

        # fig, ax = pic_setting(4.5, 4 , 9,
        #                                         #   x_label='Disp (mm)', y_label='Force (kN)',
        #                                             x_min=-600, x_max=50,
        #                                             y_min=0, y_max=1000,
        #                                             x_major_locator=100, x_minor_locator=25,
        #                                             y_major_locator=200, y_minor_locator=50)

        # # plot background full curve faint
        # ax.plot(x_dynamic, y_dynamic, linewidth=0.4, zorder=1)

        # prev_end = 0
        # for idx, (start, end) in enumerate(dynamic_ranges):
        #     # Color from the line after the previous segment's end
        #     # up to this segment's end (use `end` as the reference).
        #     # `dynamic_ranges` are 1-based; convert to 0-based slice indices.
        #     s = max(0, prev_end)
        #     e = max(0, end)
        #     # clamp to available data
        #     s = min(s, x_dynamic.size)
        #     e = min(e, x_dynamic.size)
        #     seg_x = x_dynamic[s:e]
        #     seg_y = y_dynamic[s:e]

        #     if seg_x.size == 0:
        #         prev_end = end
        #         continue
        #     col = colors[idx % len(colors)]
        #     ax.plot(seg_x, seg_y, color=col, linewidth=0.8, zorder=2)
        #     prev_end = end

        # outp3 = Path(__file__).resolve().parent / 'dynamic_processed.png'
        # fig.savefig(outp3)
        # print(f'Saved {outp3}')

    except Exception as e:
        print('Error producing plots:', e)
