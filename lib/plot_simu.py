from pathlib import Path
import numpy as np
from lib import pic_setter

class plot_simu:
    def __init__(self, in_dir:Path, out_dir: Path, width=4.5, height=5, font_size=9, **kwargs):
        self.width = width
        self.height = height
        self.font_size = font_size

        self._decode_kwargs(kwargs)
        self._calculate_derived_params()

        self.IN_DIR = in_dir
        self.OUT_DIR = out_dir# / 'single_brace_simu.out'
        self.OUT_DIR.mkdir(exist_ok=True)

    def _decode_kwargs(self, kwargs):
        self.l_brace = kwargs.get('l_brace', 5060.0)
        self.l_ed = kwargs.get('l_ed', 1800.0)
        self.d_ed = kwargs.get('d_ed', 44.0)

    def _calculate_derived_params(self):
        self.a_ed = np.pi * self.d_ed ** 2 / 4.0
        self.ed_ratio = self.l_ed / self.l_brace

    # Helper to load text file safely
    def _load_out(self, name):
        p = self.IN_DIR / name
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

    def brace_force_disp(self):
        data = self._load_out('BraceTest2BraceStreeStrain.out')
        if not self._validate_cols(data, 'BraceTest2BraceStreeStrain.out', 2):
            return

        force = data[:, 0] * self.a_ed / 1e3  # kN
        disp = data[:, 1] * self.l_brace      # mm
        return force, disp

    def plot_brace_force_disp(self, color='#66ccff', linewidth=0.2, pic_name='Brace_Force_Displacement.png', 
                              **kwargs):
        force, disp = self.brace_force_disp()
        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size,
                            # x_label='Deformation (mm)', y_label='Force (kN)',
                            **kwargs)
        ax.plot(disp, force, color=color, linewidth=linewidth)
        
        outp = self.OUT_DIR / pic_name
        fig.savefig(outp)
        print(f'Saved {outp}')

    def ed_stress_strain(self):
        data = self._load_out('BraceTest2Dissipator.out')
        if not self._validate_cols(data, 'BraceTest2Dissipator.out', 2):
            return
        
        stress = data[:, 0]
        strain = data[:, 1] / self.ed_ratio
        return stress, strain

    def plot_ed_stress_strain(self, color='#66ccff', linewidth=0.2, pic_name='ED_Stress_Strain.png', **kwargs):
        stress, strain = self.ed_stress_strain()
        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size,
                                        x_label='Strain', y_label='Stress (MPa)',
                                        **kwargs)
        ax.plot(strain, stress, color=color, linewidth=linewidth)
        outp = self.OUT_DIR / pic_name
        fig.savefig(outp)
        print(f'Saved {outp}')

    def ratchet_force_disp(self):
        data = self._load_out('BraceTest2Ratchet.out')
        if not self._validate_cols(data, 'BraceTest2Ratchet.out', 2):
            return
        
        force = data[:, 0] * self.a_ed / 1000.0
        disp = data[:, 1] * self.l_brace
        return force, disp
    
    def plot_ratchet_force_disp(self, color='#66ccff', linewidth=0.2, pic_name='Ratchet_Force_Disp.png', **kwargs):
        force, disp = self.ratchet_force_disp()
        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size,
                                        # x_label='Disp (mm)', y_label='Force (kN)', title='Ratchet Force - Disp', 
                                        **kwargs)
        ax.plot(disp, force, color=color, linewidth=linewidth)
        outp = self.OUT_DIR / pic_name
        # plt.show()
        fig.savefig(outp)
        print(f'Saved {outp}')

    def ratchet_system(self):
        data = self._load_out('BraceTest2RatchetSystem.out')
        if not self._validate_cols(data, 'BraceTest2RatchetSystem.out', 2):
            return
        x = data[:, 2] if data.shape[1] > 2 else data[:, 1]
        y = data[:, 0]
        return x, y

    def plot_ratchet_system(self, color='#66ccff', linewidth=0.2, pic_name='RatchetSystem_Force_Disp.png', **kwargs):
        x, y = self.ratchet_system()
        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size,
                            x_label='Brace Disp (mm)', y_label='Prestressing element Force (kN)',
                            title='Ratchet System Force - Disp', **kwargs)
        ax.plot(x, y, color=color, linewidth=linewidth)
        
        outp = self.OUT_DIR / pic_name
        fig.savefig(outp)
        print(f'Saved {outp}')

    def spring_force_disp(self):
        data = self._load_out('BraceTest2Spring.out')
        if not self._validate_cols(data, 'BraceTest2Spring.out', 2):
            return
        force = data[:, 0] * self.a_ed / 1000.0
        disp = data[:, 1] * self.l_brace
        return force, disp

    def plot_spring_force_disp(self, color='#66ccff', linewidth=0.2, pic_name='Spring_Force_Disp.png', **kwargs):
        force, disp = self.spring_force_disp()
        fig, ax = pic_setter.pic_setting(self.width, self.height, self.font_size,
                            x_label='Disp (mm)', y_label='Force (kN)', title='Spring Force - Disp',
                            **kwargs)
        ax.plot(disp, force, color=color, linewidth=linewidth)
        ax.relim()
        ax.autoscale_view()
        outp = self.OUT_DIR / pic_name
        fig.savefig(outp)
        print(f'Saved {outp}')


if __name__ == '__main__':
    # Default geometric/material values (match simulation defaults)
    CURR_DIR = Path(__file__).parent.parent
    in_dir = CURR_DIR / 'single_brace_simu' / 'Dynamic'
    out_dir = in_dir
    l_brace = 5060.0
    l_ed = 1800
    d_ed = 44.0  # mm
    a_ed = np.pi * d_ed ** 2 / 4.0

    pbr = plot_simu(in_dir, out_dir, width=4.5, height=4.5, font_size=9, 
                    l_brace=l_brace, l_ed=l_ed, d_ed=d_ed)
    pbr.plot_brace_force_disp(color='#66ccff', linewidth=0.2, pic_name='Brace_Force_Displacement.png',
                              x_min = -120, x_max = 120, y_min = -200, y_max = 1000, 
                              x_major_locator=40, x_minor_locator=10, y_major_locator=200, y_minor_locator=50)
    pbr.plot_ratchet_force_disp(color='#66ccff', linewidth=0.2, pic_name='Ratchet_Force_Disp.png',
                     x_min = -800, x_max = 50, y_min = -200, y_max = 1000, 
                     x_major_locator=200, x_minor_locator=50, y_major_locator=200, y_minor_locator=50)
