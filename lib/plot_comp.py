from pathlib import Path
from lib import plot_test, plot_simu, pic_setter


class plot_comp:
    def __init__(self, simu_dir: Path, excel_file: Path, out_dir: Path,
                width: float = 6, height: float = 4.5, 
                font_size: int = 8, label_size: int = 8, linewidth: float = 0.5,
                l_brace: float = 5060, l_ed: float = 1800, d_ed: float = 44,
                Test_name: str = 'Static', force_line: int = 1, disp_line: int = 2,
                colors: list = ['#66ccff', '#ff66cc', '#ccff66']):
        self.simu_dir = simu_dir
        self.excel_file = excel_file
        self.out_dir = out_dir
        self.out_dir.mkdir(exist_ok=True)
        self.Test_name = Test_name

        self.width = width
        self.height = height
        self.font_size = font_size
        self.label_size = label_size
        self.linewidth = linewidth
        self.l_brace = l_brace
        self.l_ed = l_ed
        self.d_ed = d_ed
        self.Test_name = Test_name
        self.force_line = force_line
        self.disp_line = disp_line
        self.colors = colors

        self.ps = plot_simu.plot_simu(self.simu_dir, self.out_dir, 
                                self.width, self.height, self.font_size,
                                l_brace=self.l_brace, l_ed=self.l_ed, d_ed=self.d_ed)
        self.pt = plot_test.plot_test(self.excel_file, self.out_dir, 
                                self.width, self.height, self.font_size, self.label_size, 
                                self.linewidth, self.colors,
                                self.Test_name, self.force_line, self.disp_line)

    def plot_comp_brace(self, pic_name:str, **kwargs):
        f_simu, d_simu = self.ps.brace_force_disp()
        f_test, d_test = self.pt.read_sheet(self.Test_name)

        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size, **kwargs)
        ax.plot(d_test, f_test, linewidth=self.linewidth, label='Test', color=self.colors[0])
        ax.plot(d_simu, f_simu, linewidth=self.linewidth, label='Simu', color=self.colors[1], linestyle='--')
        leg = ax.legend(loc="upper left", bbox_to_anchor=(0, 1), fontsize=self.label_size)
        for line in leg.get_lines():
            line.set_linewidth(1.5)

        outp = self.out_dir / pic_name
        fig.savefig(outp)
        print(outp)
        return outp
    
    def plot_comp_ratchet(self, row, slip, pic_name, **kwargs):
        f_simu, d_simu = self.ps.ratchet_force_disp()
        f_test, d_test = self.pt.read_ratchet(row, slip)
        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size, **kwargs)
        ax.plot(d_test, f_test, linewidth=self.linewidth, label='Test', color=self.colors[0])
        ax.plot(d_simu, f_simu, linewidth=self.linewidth, label='Simu', color=self.colors[1], linestyle='--')
        ax.plot(d_test[-1], 0, marker='o', markersize=4, markerfacecolor=self.colors[0], markeredgecolor='none', zorder=10, clip_on=False)
        ax.plot(d_simu[-1], 0, marker='*', markersize=6, markerfacecolor=self.colors[1], markeredgecolor='none', zorder=10, clip_on=False)
        leg = ax.legend(loc="upper right", bbox_to_anchor=(1, 1), fontsize=self.label_size)
        for line in leg.get_lines():
            line.set_linewidth(1.5)

        outp = self.out_dir / pic_name
        fig.savefig(outp)
        print(outp)
        return outp
