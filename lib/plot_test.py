from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from lib import pic_setter

class plot_test:
    def __init__(self, excel_file: Path, out_dir: Path, 
                 width: float=4.5, height:float=5, font_size:int=8, label_size:int = 8, 
                 linewidth:float = 0.5, colors: list = ['#66ccff', '#ff9999', '#99ff99'],
                 LINE_Y:int = 1, LINE_XS:dict = {"e": 2, "1": 5, "2": 6, "a": 7, "r": 8},
                 ):
        self.width = width
        self.height = height
        self.font_size = font_size
        self.label_size = label_size
        self.linewidth = linewidth
        self.colors = colors

        self.y = LINE_Y
        self.xs = LINE_XS

        self.excel_file = excel_file
        self.OUT_DIR = out_dir
        self.OUT_DIR.mkdir(exist_ok=True)

    def read_sheet(self, x_key: str, Test_name: str):
        """读取sheet"""
        if x_key not in self.xs:
            raise ValueError(f"x_key 必须是 {list(self.xs.keys())} 之一")
        
        y_col_idx = self.y - 1
        x_col_idx = self.xs[x_key] - 1

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

    def plot_sheet(self, x_key: str, Test_names: list, pic_name: str, **kwargs):
        """绘制图片保存到文件夹"""
        plt.rcParams["font.family"] = 'Times New Roman'
        plt.rcParams["font.size"] = self.font_size

        fig,ax = pic_setter.pic_setting(self.width, self.height, self.font_size, **kwargs,
                                        # x_min=-120, x_max=120, y_min=-200, y_max=1000, 
                                        # x_major_locator=40, y_major_locator=200, x_minor_locator=10, y_minor_locator=40, 
                                        # x_label="Deformation (mm)", y_label="Force (kN)", title=x_key,
                                        )
        
        for i, Test_name in enumerate(Test_names):
            # 绘制曲线，Fatigue 的 Cycle 26-30 使用虚线
            y, x = self.read_sheet(x_key, Test_name)
            ax.plot(x, y, linewidth=self.linewidth, label=Test_name, color=self.colors[i % len(self.colors)],
                    linestyle='--' if Test_name == "Cycle 26-30" else '-')
            if i > 0:
                leg = ax.legend(
                    loc="upper left",
                    bbox_to_anchor=(0, 1),
                    fontsize=self.label_size,
                )
                for line in leg.get_lines():
                    line.set_linewidth(1.5)

        output_path = self.OUT_DIR / f'{pic_name}'
        fig.savefig(output_path)
        plt.close(fig)
        return str(output_path)
