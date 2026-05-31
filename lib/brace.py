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
    def __init__(self, mat_ed: material.Material, angle_deg: float, l_brace: float, design_drift: float, *,
                 reserved_length: float = 720.0, slip: float = 2.0, chuck_k_ratio: float = 1.6, 
                 l_ed: float = 1800.0, d_ed:float = 44, f_pre: float = 15e3, f_spr: float = 200e3, ):
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
            'chuck_k_ratio': self.chuck_k_ratio,
            'd_ed': self.d_ed,
            'a_ed': self.a_ed,
            'l_ed': self.l_ed,
            'ed_ratio': self.ed_ratio,
            'f_pre': self.f_pre,
            'f_spr': self.f_spr,
            'l_yield': self.l_yield,
            'reserved_length': self.reserved_length,
            'reserved_length_ratio': self.reserved_length_ratio,
            'slip': self.slip,
            'slip_ratio': self.slip_ratio,
            'delta_l_max': self.delta_l_max,
            'delta_l_max_ratio': self.delta_l_max_ratio,
            }

    def build_in_opensees(self, out_dir) -> int:
        """Create the uniaxial materials in the current OpenSees model.

        Returns the next available material index after the created materials.
        """
        p = self.parameters()
        tag_base = lambda code: int(f"{100+self.NO}{int(code):02d}")
        outpath = lambda filename: str(out_dir / filename)

        # # 1. Ratchet: 这个只有E，但是没有长度，而且这个E的定义是k_chuck * l_brace / a_ed
        # # Ratchet: OpenSees expects E, freeTravel, freeTravelInitial, RatType (no keywords)
        # ops.uniaxialMaterial('Ratchet', tag_base(1), p["chuck_k_ratio"] * p['es'] / p['ed_ratio'], p['slip_ratio'], 0.0, 2)
        # # 2. 限制ratchet的累计滑移量reserved_length
        # ops.uniaxialMaterial('ElasticMultiLinear', tag_base(2), '-strain', p['reserved_length_ratio'] - epsilon_tiny, p['reserved_length_ratio'], 0, '-stress', -sigma_giant, 0, sigma_tiny)
        # # 3. 并联
        # ops.uniaxialMaterial('Parallel', tag_base(3), tag_base(1), tag_base(2))
        # # 4. 耗能钢棒，且刚度转换为基于支撑长度的等效刚度
        # ops.uniaxialMaterial('ReinforcingSteel', tag_base(4), p['fy'], p['fu'], p['es']/p['ed_ratio'], p['esh']/p['ed_ratio'], p['epsilon_sh']*p['ed_ratio'], p['epsilon_u']*p['ed_ratio'])
        # # 5. 串联
        # ops.uniaxialMaterial('Series', tag_base(5), tag_base(3), tag_base(4))
        # # 6. 限制ratchet单次滑移量，保障支撑整体不会缩短
        # ops.uniaxialMaterial('ElasticMultiLinear', tag_base(6), '-strain', -epsilon_tiny, 0.0, epsilon_tiny, '-stress', -sigma_giant, 0.0, sigma_tiny)
        # # 7. 并联
        # ops.uniaxialMaterial('Parallel', tag_base(7), tag_base(6), tag_base(5))
        # # 8. Prestressed Spring 其中0.001是一个随便给的数
        # ops.uniaxialMaterial('ElasticMultiLinear', tag_base(8), '-strain', -p["delta_l_max_ratio"], -0.001 * p["delta_l_max_ratio"], 0.0, p['delta_l_max_ratio'], '-stress', -p["f_spr"] / p["a_ed"], -p["f_pre"]/p["a_ed"], 0.0, sigma_giant)
        # # 9. 并联
        # ops.uniaxialMaterial('Series', tag_base(0), tag_base(7), tag_base(8))

        bias = p['delta_l_max'] / p['l_brace']

        # 1. Ratchet: 这个只有E，但是没有长度，而且这个E的定义是k_chuck * l_brace / a_ed
        # Ratchet: OpenSees expects E, freeTravel, freeTravelInitial, RatType (no keywords)
        ops.uniaxialMaterial('Ratchet', tag_base(1),  p["chuck_k_ratio"]*p["es"]/p["ed_ratio"], self.slip_ratio, 0.0, 2)
        # 2. 限制ratchet的累计滑移量reserved_length
        ops.uniaxialMaterial('ElasticMultiLinear', tag_base(2),
                             '-strain', p["reserved_length_ratio"] - bias, p["reserved_length_ratio"], p["reserved_length_ratio"] + bias, 
                             '-stress', -p["f_spr"]/p["a_ed"]*(1e6), 0, p["f_spr"]/p["a_ed"]/(1e6))
        # 3. 并联
        ops.uniaxialMaterial('Parallel', tag_base(3), tag_base(1), tag_base(2))
        # 4. 耗能钢棒，且刚度转换为基于支撑长度的等效刚度
        ops.uniaxialMaterial('ReinforcingSteel', tag_base(4), p["fy"], p["fu"], p["es"]/p["ed_ratio"], p["esh"]/p["ed_ratio"], p["epsilon_sh"]*p["ed_ratio"], p["epsilon_u"]*p["ed_ratio"])
        # 5. 串联
        ops.uniaxialMaterial('Series', tag_base(5), tag_base(3), tag_base(4))
        # 6. 限制ratchet单次滑移量，保障支撑整体不会缩短
        ops.uniaxialMaterial('ElasticMultiLinear', tag_base(6), 
                             '-strain', -p["delta_l_max"]/p["l_brace"], 0, p["delta_l_max"]/p["l_brace"], 
                             '-stress', -p["f_spr"]/p["a_ed"]*(1e6), 0, p["f_spr"]/p["a_ed"]/(1e6))
        # 7. 并联
        ops.uniaxialMaterial('Parallel', tag_base(7), tag_base(5), tag_base(6))
        # 8. Prestressed Spring 其中0.001是一个随便给的数
        ops.uniaxialMaterial('ElasticMultiLinear', tag_base(8), 
                             '-strain', -p["delta_l_max"]/p["l_brace"], -0.002 * p["delta_l_max"]/p["l_brace"], 0, p["delta_l_max"]/p["l_brace"], 
                             '-stress', -p["f_spr"]/p["a_ed"], -p["f_pre"]/p["a_ed"], 0, p["f_spr"]/p["a_ed"]*(1e6))
        # 9. 并联
        ops.uniaxialMaterial('Series', tag_base(0), tag_base(7), tag_base(8))

        ops.element('Truss', 1, 1, 2, self.a_ed, tag_base(0))

        ops.recorder('Node', '-file', outpath('BraceTest2Disp.out'), '-node', 2, '-dof', 1, 'disp')
        ops.recorder('Node', '-file', outpath('BraceTest2Force.out'), '-node', 1, '-dof', 1, 'reaction')
        ops.recorder('Element', '-file', outpath('BraceTest2BraceStreeStrain.out'), '-ele', 1, 'material', 'stressStrain')
        ops.recorder('Element', '-file', outpath('BraceTest2Dissipator.out'), '-ele', 1, 'material', 'component', 1, 'component', 1, 'component', 2, 'stressStrain')
        ops.recorder('Element', '-file', outpath('BraceTest2Ratchet.out'), '-ele', 1, 'material', 'component', 1, 'component', 1, 'component', 1, 'component', 1, 'stressStrain')
        ops.recorder('Element', '-file', outpath('BraceTest2RatchetSystem.out'), '-ele', 1, 'material', 'component', 1, 'stressStrain')
        ops.recorder('Element', '-file', outpath('BraceTest2Spring.out'), '-ele', 1, 'material', 'component', 2, 'stressStrain')

    #     MATERIALS = [
    #     ("Ratchet", tag_base(1), [p["chuck_k_ratio"] * p['es'] / p['ed_ratio'], p['slip_ratio'], 0, 2]),
    #     ("ElasticMultiLinear", tag_base(2), ["-strain", p['reserved_length_ratio'] - epsilon_tiny, p['reserved_length_ratio'], 0.0, "-stress", -sigma_giant, 0.0, sigma_tiny]),
    #     ("Parallel", tag_base(3), [tag_base(1), tag_base(2)]),
    #     ("ReinforcingSteel", tag_base(4), [p['fy'], p['fu'], p['es']/p['ed_ratio'], p['esh']/p['ed_ratio'], p['epsilon_sh']*p['ed_ratio'], p['epsilon_u']*p['ed_ratio']]),
    #     ("Series", tag_base(5), [tag_base(3), tag_base(4)]),
    #     ("ElasticMultiLinear", tag_base(6), ["-strain", -epsilon_tiny, 0.0, epsilon_tiny, '-stress', -sigma_giant, 0.0, sigma_tiny]),
    #     ("Parallel", tag_base(7), [tag_base(6), tag_base(5)]),
    #     ("ElasticMultiLinear", tag_base(8), ["-strain", -p["delta_l_max_ratio"], -0.001 * p["delta_l_max_ratio"], 0.0, epsilon_tiny, "-stress", -p["f_spr"] / p["a_ed"], -p["f_pre"]/p["a_ed"], 0.0, sigma_giant]),
    #     ("Series", tag_base(0), [tag_base(8), tag_base(7)])
    # ]
    #     for mtype, mtag, args in MATERIALS:
    #         try:
    #             ops.uniaxialMaterial(mtype, mtag, *args)
    #             print(f"Registered material {mtype} {mtag}")
    #         except Exception as e:
    #             print(f"Warning: failed to register {mtype} {mtag}: {e}")

        return tag_base(0)