"""
analyze_brace_results.py
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from lib import pic_setter


class plot_brace_results:
    def __init__(self, in_dir:Path, out_dir: Path, width=4.5, height=5, font_size=9, **kwargs):
        self.IN_DIR = in_dir
        self.out_dir = out_dir
        self.width = width
        self.height = height
        self.font_size = font_size

        self._decode_kwargs(kwargs)
        self._calculate_derived_params()

        self.OUT_DIR = self.out_dir# / 'single_brace_simu.out'
        self.OUT_DIR.mkdir(exist_ok=True)

        plt.rcParams["font.family"] = "Times New Roman"

    def _decode_kwargs(self, kwargs):
        self.l_brace = kwargs.get('l_brace', 5060.0)
        self.l_ed = kwargs.get('l_ed', 1800.0)
        self.d_ed = kwargs.get('d_ed', 44.0)

    def _calculate_derived_params(self):
        self.a_ed = np.pi * self.d_ed ** 2 / 4.0
        self.ed_ratio = self.l_ed / self.l_brace

    # Helper to load text file safely
    def load_out(self, name):
        p = self.OUT_DIR / name
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

    def _validate_cols(self, data, name: str, min_cols: int) -> bool:
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


    def plot_brace_force_disp(self, **kwargs):
        
        data = self.load_out('BraceTest2BraceStreeStrain.out')
        if not self._validate_cols(data, 'BraceTest2BraceStreeStrain.out', 2):
            return

        force = data[:, 0] * self.a_ed / 1e3  # kN
        disp = data[:, 1] * self.l_brace      # mm

        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size,
                            # x_label='Deformation (mm)', y_label='Force (kN)',
                            **kwargs)
        ax.plot(disp, force, color='#66ccff', linewidth=0.2)
        
        outp = self.OUT_DIR / 'Brace_Force_Displacement.png'
        fig.savefig(outp)
        print(f'Saved {outp}')


    def plot_ed_stress_strain(self):
        data = self.load_out('BraceTest2Dissipator.out')
        if not self._validate_cols(data, 'BraceTest2Dissipator.out', 2):
            return
        
        stress = data[:, 0]
        strain = data[:, 1] / self.ed_ratio
        
        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size,
                            x_label='Strain', y_label='Stress (MPa)',)
        ax.plot(strain, stress, color='#66ccff', linewidth=1)
        outp = self.OUT_DIR / 'ED_Stress_Strain.png'
        fig.savefig(outp)
        print(f'Saved {outp}')


    def plot_ratchet(self):
        data = self.load_out('BraceTest2Ratchet.out')
        if not self._validate_cols(data, 'BraceTest2Ratchet.out', 2):
            return
        
        force = data[:, 0] * self.a_ed / 1000.0
        disp = data[:, 1] * self.l_brace

        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size,
                            x_label='Disp (mm)', y_label='Force (kN)',
                            title='Ratchet Force - Disp')
        ax.plot(disp, force, color='#66ccff', linewidth=0.05)
        outp = self.OUT_DIR / 'Ratchet_Force_Disp.png'
        fig.savefig(outp)
        print(f'Saved {outp}')


    def plot_ratchet_system(self):
        data = self.load_out('BraceTest2RatchetSystem.out')
        if not self._validate_cols(data, 'BraceTest2RatchetSystem.out', 2):
            return
        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size,
                            x_label='Brace Disp (mm)', y_label='Prestressing element Force (kN)',
                            title='Ratchet System Force - Disp')
        ax.plot(data[:, 2] if data.shape[1] > 2 else data[:, 1], data[:, 0], color='#66ccff', linewidth=0.8)
        
        outp = self.OUT_DIR / 'RatchetSystem_Force_Disp.png'
        fig.savefig(outp)
        print(f'Saved {outp}')


    def plot_spring(self):
        data = self.load_out('BraceTest2Spring.out')
        if not self._validate_cols(data, 'BraceTest2Spring.out', 2):
            return
        force = data[:, 0] * self.a_ed / 1000.0
        disp = data[:, 1] * self.l_brace
        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size,
                            x_label='Disp (mm)', y_label='Force (kN)',
                            title='Spring Force - Disp')
        ax.plot(disp, force, color='#66ccff', linewidth=0.8)
        ax.relim()
        ax.autoscale_view()
        outp = self.OUT_DIR / 'Spring_Force_Disp.png'
        fig.savefig(outp)
        print(f'Saved {outp}')


    # def main(self, show: bool = False):
    #     # attempt to load parameter file if present
    #     # otherwise use defaults
    #     # Run plots
    #     self.plot_brace_stress_strain()
    #     self.plot_ed_stress_strain()
    #     self.plot_ratchet()
    #     self.plot_ratchet_system()
    #     self.plot_spring()

    #     if show:
    #         plt.show()


if __name__ == '__main__':
    
    # Default geometric/material values (match simulation defaults)
    CURR_DIR = Path(__file__).parent
    in_dir = CURR_DIR / 'single_brace_simu'
    out_dir = in_dir
    l_brace = 5060.0
    l_ed = 1800
    d_ed = 44.0  # mm
    a_ed = np.pi * d_ed ** 2 / 4.0

    bpr = plot_brace_results(in_dir, out_dir, width=5 / 2.54, height=4.5 / 2.54, font_size=9, 
                             l_brace=l_brace, l_ed=l_ed, d_ed=d_ed)
    bpr.plot_brace_force_disp(x_min = -120, x_max = 120, y_min = -200, y_max = 1000, 
                              x_major_locator=40, x_minor_locator=10, y_major_locator=200, y_minor_locator=50)
    
