from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np
from lib import pic_setter


class plot_test:
    def __init__(self, excel_file: Path, out_dir: Path, 
                 width: float=4.5, height:float=5, font_size:int=8, label_size:int = 8, 
                 linewidth: float = 0.5, colors: list = ['#66ccff', '#ff66cc', '#ccff66'],
                 Test_name: str = 'Static', force_line: int = 1, disp_line: int = 2,
                #  LINE_Y:int = 1, LINE_XS:dict = {"e": 2, "1": 5, "2": 6, "a": 7, "r": 8},
                 ):
        self.width = width
        self.height = height
        self.font_size = font_size
        self.label_size = label_size
        self.linewidth = linewidth
        self.colors = colors

        self.Test_name = Test_name
        self.force_line = force_line
        self.disp_line = disp_line

        self.excel_file = excel_file
        self.OUT_DIR = out_dir
        self.OUT_DIR.mkdir(exist_ok=True)

    def read_sheet(self, Test_name):
        """读取sheet"""
        y_col_idx = self.force_line - 1
        x_col_idx = self.disp_line - 1

        df = pd.read_excel(self.excel_file, sheet_name=Test_name, header=0)

        # 检查列索引是否超出范围
        if x_col_idx >= df.shape[1] or y_col_idx >= df.shape[1]:
            raise IndexError(
                f"Sheet {Test_name} 列索引超出范围: x={x_col_idx + 1}, y={y_col_idx + 1}, 总列数={df.shape[1]}"
            )
        
        x = df.iloc[:, x_col_idx]
        y = df.iloc[:, y_col_idx]
        # 保证为数值型并去除 x 为 NaN 的行
        x = pd.to_numeric(x, errors="coerce")
        y = pd.to_numeric(y, errors="coerce")
        valid = x.notna()
        x = x[valid]
        y = y[valid]
        return y, x

    def plot_sheet(self, pic_name: str, **kwargs):
        """绘制图片保存到文件夹"""
        plt.rcParams["font.family"] = 'Times New Roman'
        plt.rcParams["font.size"] = self.font_size

        fig,ax = pic_setter.pic_setting(self.width, self.height, self.font_size, **kwargs,
                                        # x_min=-120, x_max=120, y_min=-200, y_max=1000, 
                                        # x_major_locator=40, y_major_locator=200, x_minor_locator=10, y_minor_locator=40, 
                                        # x_label="Deformation (mm)", y_label="Force (kN)", title=x_key,
                                        )
        if self.Test_name == 'Fatigue':
            Fati_names = ["Cycle 1-25", "Cycle 26-30"]
            for i, Fati_name in enumerate(Fati_names):
                # 绘制曲线，Fatigue 的 Cycle 26-30 使用虚线
                y, x = self.read_sheet(Fati_name)
                ax.plot(x, y, linewidth=self.linewidth, label=Fati_name, color=self.colors[i % len(self.colors)],
                        linestyle='--' if Fati_name == "Cycle 26-30" else '-')
                leg = ax.legend(
                    loc="upper left",
                    bbox_to_anchor=(0, 1),
                    fontsize=self.label_size,
                )
                for line in leg.get_lines():
                    line.set_linewidth(1.5)
        else:
            y, x = self.read_sheet(self.Test_name)
            ax.plot(x, y, linewidth=self.linewidth, color=self.colors[0])

        output_path = self.OUT_DIR / f'{pic_name}'
        fig.savefig(output_path)
        plt.close(fig)
        return str(output_path)

    def _rows_to_ranges(self, df_ratchet, start_row, end_row):
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
    
    def _apply_slip(self, x, marked_ranges, slip:float = -1.5):
        if slip == 0 or not marked_ranges:
            return x
        else:
            x_temp = x.astype(float)
            ends = [end for (_s, end) in marked_ranges]
            prev_one = 1
            n = x_temp.size
            for idx, end in enumerate(ends):
                # slice for one-based [prev_one, end-1] -> 0-based [prev_one-1, end-1]
                s_idx = max(0, prev_one - 1)
                e_idx = min(n, end - 1)
                if s_idx < e_idx:
                    x_temp[s_idx:e_idx] = x_temp[s_idx:e_idx] - (slip * idx)
                prev_one = end
            if prev_one <= n:
                s_idx = max(0, prev_one - 1)
                x_temp[s_idx:n] = x_temp[s_idx:n] - (slip * len(ends))
            return x_temp

    def _derive_ratchet(self, y_read, x_read, marked_ranges, slip: float = -1.5):
        N = len(y_read)
        x = np.zeros(N)
        ranges = list(marked_ranges) if isinstance(marked_ranges[0], (list, tuple)) else marked_ranges

        for i in range(1, N):
            one_based = i + 1
            in_range = any(start <= one_based < end for (start, end) in ranges)
            if in_range:
                x[i] = x[i-1] + (x_read[i] - x_read[i-1])
            else:
                x[i] = x[i-1]
        
        x = self._apply_slip(x, marked_ranges, slip)
        y = np.maximum(np.array(y_read), 0)
        return y, x

    def read_ratchet(self, row: tuple = (1,14), slip: float = -1.5):
        xl = pd.ExcelFile(self.excel_file)
        df_ratchet = xl.parse('ratchet')
        marked_ranges = self._rows_to_ranges(df_ratchet, row[0], row[1])
        y_read, x_read = self.read_sheet(self.Test_name)
        y, x = self._derive_ratchet(y_read, x_read, marked_ranges, slip)
        return y, x
    
    def plot_ratchet(self, row: tuple, slip: float, pic_name: str, H_len: float, D_len: float, **kwargs):
        plt.rcParams["font.family"] = 'Times New Roman'
        plt.rcParams["font.size"] = self.font_size

        y, x = self.read_ratchet(row, slip)

        fig,ax = pic_setter.pic_setting(self.width, self.height, self.font_size, **kwargs,)
        ax.plot(x, y, linewidth=self.linewidth, color=self.colors[0], label='Derivation')
        if x.size:
            ax.plot(x[-1], y[-1], marker='o', markersize=4, markeredgewidth=0, markeredgecolor='none', markerfacecolor=self.colors[0], zorder=10, clip_on=False)
        # draw H_len and D_len vertical markers for Static (index 0)
        ax.plot(H_len, 0, marker='*', markersize=6, markerfacecolor=self.colors[1], markeredgecolor='none', zorder=10, clip_on=False)
        ax.plot(D_len, 0, marker='s', markersize=4, markerfacecolor=self.colors[2], markeredgecolor='none', zorder=10, clip_on=False)
        # ax.axvline(x=H_len, color=self.colors[1], linewidth=0.5, linestyle='--', label='HSR')
        # ax.axvline(x=D_len, color=self.colors[2], linewidth=0.5, linestyle='--', label='Dissipater')

        handles = [
            Line2D([0], [0], lw=1, color=self.colors[0], label='Derivation'),
            Line2D([0], [0], marker='*', color='none', markerfacecolor=self.colors[1], markeredgecolor='none',label='HSR'),
            Line2D([0], [0], marker='s', color='none', markerfacecolor=self.colors[2], markeredgecolor='none',label='Dissipater'),
        ]
        leg = ax.legend(handles=handles, loc="upper right", bbox_to_anchor=(1, 1), fontsize=self.label_size)
        
        outp = self.OUT_DIR / f'{pic_name}'
        fig.savefig(outp)
        print(f'Saved {outp}')
        plt.close(fig)
        return str(outp)
        
        
if __name__ == '__main__':
    excel_file = "revise.xlsx"
    pic_path = Path(__file__).resolve().parent / "single_brace_test"
    pic_path.mkdir(parents=True, exist_ok=True)

    LINE_Y = 1
    LINE_XS = {"e": 2, "1": 5, "2": 6, "a": 7, "r": 8}

    width, 	height, font_size, 	label_size, linewidth = \
    6, 		4.5, 	8,			8,			0.5

    colors = ['#66ccff', '#ff66cc', '#ccff66']  # 预定义颜色列表

    m_static = "1"
    m_fatigue = "r"
    m_dynamic = "e"
    pt = plot_test.plot_test(excel_file, pic_path, width, height, 
                            font_size, label_size, linewidth, colors,
                            'Static', 1, 5)
