from pathlib import Path
from lib import plot_test, plot_simu, pic_setter


class plot_comp:
    def __init__(self, simu_dir: Path, excel_file: Path, out_dir: Path,
                width: float = 6, height: float = 4.5, 
                font_size: int = 8, label_size: int = 8, linewidth: float = 0.5,
                l_brace: float = 5060, l_ed: float = 1800, d_ed: float = 44,
                line_y: int = 1, line_xs: dict = {"e": 2, "1": 5, "2": 6, "a": 7, "r": 8},
                colors: list = ['#66ccff', '#ff66cc', '#ccff66']):
        self.simu_dir = simu_dir
        self.excel_file = excel_file
        self.out_dir = out_dir
        self.out_dir.mkdir(exist_ok=True)

        self.width = width
        self.height = height
        self.font_size = font_size
        self.label_size = label_size
        self.linewidth = linewidth
        self.l_brace = l_brace
        self.l_ed = l_ed
        self.d_ed = d_ed
        self.line_y = line_y
        self.line_xs = line_xs
        self.colors = colors

    def plot_comp(self, x_key:str, Test: str, pic_name:str, **kwargs):
        simu_path = self.simu_dir / f'{Test}.out'
        ps = plot_simu.plot_simu(simu_path, self.out_dir, 
                                self.width, self.height, self.font_size,
                                l_brace=self.l_brace, l_ed=self.l_ed, d_ed=self.d_ed)
        f_simu, d_simu = ps.brace_force_disp()

        pt = plot_test.plot_test(self.excel_file, self.out_dir, 
                                self.width, self.height, self.font_size, self.label_size, 
                                self.linewidth, self.colors,
                                self.line_y, self.line_xs)
        f_test,d_test = pt.read_sheet(x_key, Test)

        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size, **kwargs)
        
        ax.plot(d_test, f_test, linewidth=self.linewidth, label=Test, color=self.colors[0])
        ax.plot(d_simu, f_simu, linewidth=self.linewidth, label=Test, color=self.colors[1], linestyle='--')
        leg = ax.legend(loc="upper left",
                        bbox_to_anchor=(0, 1),
                        fontsize=self.label_size)
        for line in leg.get_lines():
            line.set_linewidth(1.5)

        outp = self.out_dir / pic_name
        fig.savefig(outp)
        print(outp)
        return outp