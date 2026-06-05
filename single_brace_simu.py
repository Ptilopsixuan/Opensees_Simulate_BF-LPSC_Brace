import openseespy.opensees as ops
from lib import brace, material, opensees_setter, plot_simu
from pathlib import Path

# Complete OpenSeesPy version of BraceTestStatic.tcl
if __name__ == "__main__":
    protocols = {
        'static': { 10.4: 3, 22.3: 3, 47.8: 3, 73.4: 3, 99.5: 1 },
        'fatigue': { 47.8: 30 },
        # 'dynamic': { 10.4: 3, 22.3: 3, 47.8: 3, 73.4: 3, 99.5: 1 },
    }

    for name, protocol in protocols.items():
        out_dir = Path(__file__).resolve().parent / 'single_brace_simu'
        out_dir.mkdir(exist_ok=True)
        out_dir = out_dir / f'{name}.out'
        out_dir.mkdir(exist_ok=True)
        
        l_brace = 5060.0
        P = 30000.0

        if name == 'static':
            m = material.StainlessSteel(es=130e3, fy=210.0, fu=570.0, epsilon_u=0.35, 
                                        epsilon_platform=0.001, esh=0.02*130e3)
            b = brace.LLPSCB(mat_ed=m, angle_deg=45.0, l_brace=l_brace, design_drift=0.04, 
                            reserved_length = 720, slip = 1.0, chuck_k_ratio=1.6,
                            l_ed = 1800.0, d_ed = 44, f_pre = 15e3, f_spr = 100e3,)
        elif name == 'fatigue':
            m = material.StainlessSteel(es=160e3, fy=210.0, fu=570.0, epsilon_u=0.35, 
                                        epsilon_platform=0.001, esh=0.02*160e3)
            b = brace.LLPSCB(mat_ed=m, angle_deg=45.0, l_brace=l_brace, design_drift=0.04, 
                            reserved_length = 720, slip = 1.0, chuck_k_ratio=1.6,
                            l_ed = 1800.0, d_ed = 44, f_pre = 15e3, f_spr = 100e3,)
        
        # initialize model
        modelSetter = opensees_setter.ModelSetter(dt=0.01)
        modelSetter.initialize()

        # nodes and BCs
        ops.node(1, 0.0, 0.0)
        ops.node(2, b.l_brace, 0.0)
        ops.fix(1, 1, 1, 1)
        ops.fix(2, 0, 1, 1)

        b_NO = b.build_in_opensees(out_dir)
        ops.element('Truss', 1, 1, 2, b.a_ed, b_NO)
        modelSetter.set_analysis(test_type=name)

        # Define loads and pattern (time series linear)
        ops.timeSeries('Linear', 1)
        ops.pattern('Plain', 1, 1)
        ops.load(2, P, 0.0, 0.0)

        numIter, du = modelSetter.set_disp_protocol(protocol, step_len=0.005)
        
        for n, dU in zip(numIter, du):
            ops.integrator('DisplacementControl', 2, 1, dU)
            if ops.analyze(n) != 0:
                raise RuntimeError(f'Analysis failed at step with dU={dU}, numIter={n}')
            factor = ops.getTime()

        pbr = plot_simu.plot_brace_results(out_dir, out_dir, width=4.5 / 2.54, height=4.5 / 2.54, font_size=9, 
                             l_brace=b.l_brace, l_ed=b.l_ed, d_ed=b.d_ed)
        pbr.plot_brace_force_disp(x_min = -120, x_max = 120, y_min = -200, y_max = 1000, 
                              x_major_locator=40, x_minor_locator=10, y_major_locator=200, y_minor_locator=50)
        pbr.plot_ratchet(x_min = -800, x_max = 50, y_min = -200, y_max = 1000, 
                        x_major_locator=200, x_minor_locator=50, y_major_locator=200, y_minor_locator=50)

        # # Execute analyze_brace_results.py after analysis completes
        # with open('analyze_brace_results.py', 'r', encoding='utf-8') as f:
        #     exec(f.read())
