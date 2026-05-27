import numpy as np
import openseespy.opensees as ops
from . import material

class Brace:
    """Generic brace object that holds geometry and material reference.

    This class focuses on data organization. Methods that register
    OpenSees objects should be implemented in derived classes.
    """
    _counter = 0

    def __init__(self, mat_ed: material.Material, angle_deg: float, l_brace: float, design_drift: float):
        type(self)._counter += 1
        self.NO = type(self)._counter           # Unique identifier for the brace instance
        self.material_ed = mat_ed               # ED material
        self.angle = float(angle_deg)           # 支撑与水平线的夹角，单位为度
        self.l_brace = float(l_brace)           # 支撑长度，单位为mm
        self.design_drift = float(design_drift) # 设计层间位移角，单位为无量纲


class LLPSCB(Brace):
    """LLPSCB brace containing parameters and OpenSeesPy registration
    routines that replace writing TCL files.
    """
    def __init__(self, mat_ed: material.Material, angle_deg: float, 
                 l_brace: float, design_drift: float = 0.04, *,
                 reserved_length: float = 720.0, slip: float = 2.0, chuck_k_ratio: float = 1.0, 
                 l_ed: float = 1800.0, d_ed:float = 44,
                 f_pre: float = 15e3, f_spr: float = 200e3, ):
        super().__init__(mat_ed, angle_deg, l_brace, design_drift)

        # ratech part
        self.reserved_length = -float(reserved_length)   # 预留长度，单位为mm
        self.slip = float(slip)                         # 滑移，单位为mm
        self.chuck_k_ratio = float(chuck_k_ratio)       # chuck_k_ratio = k_chuck / k_ed
        
        # ED part
        self.l_ed = float(l_ed)                         # ED钢棒长度，单位为mm
        self.d_ed = float(d_ed)                         # ED钢棒直径，单位为mm
        
        # Prestress and Spring Force
        self.f_pre = float(f_pre)                       # 预应力，单位为N
        self.f_spr = float(f_spr)                       # 碟簧的最大力，单位为N
        self._supplement()

    def _supplement(self) -> None:
        self.reserved_length_ratio = self.reserved_length / self.l_brace  # 预留长度与支撑长度的比值
        self.slip_ratio = self.slip / self.l_brace               # 滑移与支撑长度的比值
        self.ed_ratio = self.l_ed / self.l_brace                 # ED长度与支撑长度的比值
        self.a_ed = np.pi * self.d_ed**2 / 4.0                   # ED截面面积，单位为mm^2
        self.l_yield = self.material_ed.epsilon_y * self.l_ed    # ED屈服长度，单位为mm
        self.delta_l_max_ratio = 0.5 * self.design_drift * np.sin(np.deg2rad(self.angle * 2.0))  # 支撑最大形变率
        self.delta_l_max = self.delta_l_max_ratio * self.l_brace      # 支撑最大形变量，单位为mm

    def parameters(self) -> dict:
        return {
            'es': self.material_ed.es,
            'fy': self.material_ed.fy,
            'fu': self.material_ed.fu,
            'epsilon_u': self.material_ed.epsilon_u,
            'epsilon_sh': self.material_ed.epsilon_sh,
            'esh': self.material_ed.esh,
            'angle': self.angle,
            'l_brace': self.l_brace,
            'reserved_length': self.reserved_length,
            'slip': self.slip,
            'chuck_k_ratio': self.chuck_k_ratio,
            'l_ed': self.l_ed,
            'd_ed': self.d_ed,
            'f_pre': self.f_pre,
            'f_spr': self.f_spr,
            'reserved_length_ratio': self.reserved_length_ratio,
            'slip_ratio': self.slip_ratio,
            'ed_ratio': self.ed_ratio,
            'a_ed': self.a_ed,
            'l_yield': self.l_yield,
            'delta_l_max_ratio': self.delta_l_max_ratio,
            'delta_l_max': self.delta_l_max,
            }

    def build_in_opensees(self) -> int:
        """Create the uniaxial materials in the current OpenSees model.

        Returns the next available material index after the created materials.
        """
        p = self.parameters()
        epsilon_tiny = 1e-6 * p['delta_l_max_ratio']
        [sigma_tiny, sigma_giant] = np.array([1e-6, 1e6]) * p['f_spr']/p['a_ed']
        
        tag_base = lambda code: int(f"{100+self.NO}{int(code):02d}")

        # 1. Ratchet: 这个只有E，但是没有长度，而且这个E的定义是k_chuck * l_brace / a_ed
        # Ratchet: OpenSees expects E, freeTravel, freeTravelInitial, RatType (no keywords)
        ops.uniaxialMaterial('Ratchet', tag_base(1), p["chuck_k_ratio"] * p['es'] / p['ed_ratio'], p['slip_ratio'], 0, 2)
        # 2. 限制ratchet的累计滑移量reserved_length
        ops.uniaxialMaterial('ElasticMultiLinear', tag_base(2), '-strain', p['reserved_length_ratio'] +epsilon_tiny, p['reserved_length_ratio'], 0, '-stress', sigma_giant, 0, 0)
        # 3. 并联
        ops.uniaxialMaterial('Parallel', tag_base(3), tag_base(1), tag_base(2))
        # 4. 耗能钢棒，且刚度转换为基于支撑长度的等效刚度
        ops.uniaxialMaterial('ReinforcingSteel', tag_base(4), p['fy'], p['fu'], p['es']/p['ed_ratio'], p['esh']/p['ed_ratio'], p['epsilon_sh']*p['ed_ratio'], p['epsilon_u']*p['ed_ratio'])
        # 5. 串联
        ops.uniaxialMaterial('Series', tag_base(5), tag_base(3), tag_base(4))
        # 6. 限制ratchet单次滑移量，保障支撑整体不会缩短
        ops.uniaxialMaterial('ElasticMultiLinear', tag_base(6), '-strain', -epsilon_tiny, 0.0, epsilon_tiny, '-stress', -sigma_giant, 0.0, sigma_tiny)
        # 7. 并联
        ops.uniaxialMaterial('Parallel', tag_base(7), tag_base(6), tag_base(5))
        # 8. Prestressed Spring 其中0.001是一个随便给的数
        strains = [-p["delta_l_max_ratio"], -0.001 * p["delta_l_max_ratio"], 0.0, epsilon_tiny]
        stresses = [-p["f_spr"] / p["a_ed"], -p["f_pre"]/p["a_ed"], 0.0, sigma_giant]
        ops.uniaxialMaterial('ElasticMultiLinear', tag_base(8), '-strain', *strains, '-stress', *stresses)
        # 9. 并联
        ops.uniaxialMaterial('Parallel', tag_base(0), tag_base(7), tag_base(8))

        

        return tag_base(0)