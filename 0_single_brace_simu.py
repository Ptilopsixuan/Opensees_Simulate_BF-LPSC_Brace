import openseespy.opensees as ops
from lib import brace, material, opensees_setter, plot_simu
from pathlib import Path

if __name__ == "__main__":
    # Set up output directory and plot parameters
    OUT_DIR = Path(__file__).resolve().parent / 'single_brace_simu'
    OUT_DIR.mkdir(exist_ok=True)
    width, height, font_size= 4, 4.5, 8
    # Define material, brace parameters, analysis protocols and step length
    P = 30000.0
    es,                 fy,         fu,             epsilon_u,  epsilon_platform,   esh = \
    130e3,              210.0,      570.0,          0.35,       0.001,              0.02*130e3
    angle_deg,          l_brace,    design_drift    = \
    45.0,               5060,       0.04
    reserved_length,    slip,       chuck_k_ratio   = \
    720,                2,        1.6
    l_ed,               d_ed,       f_pre,          f_spr       = \
    1800.0,             44,         15e3,           100e3
    protocols = {
        'Static': { 10.4: 3, 22.3: 3, 47.8: 3, 73.4: 3, 99.5: 1 },
        'Fatigue': { 47.8: 30 },
        'Dynamic': { 10.4: 3, 22.3: 3, 47.8: 3, 73.4: 3, 99.5: 3 },
    }
    step_len = 0.005

    # Loop through each protocol and perform analysis
    for name, protocol in protocols.items():
        protocol_out_dir = OUT_DIR / f'{name}.out'
        protocol_out_dir.mkdir(exist_ok=True)

        # if name == 'Static' or name == 'Dynamic':
        m = material.StainlessSteel(es, fy, fu, epsilon_u, epsilon_platform, esh)
        b = brace.LLPSCB(m, angle_deg, l_brace, design_drift, 
                        reserved_length, slip, chuck_k_ratio,
                        l_ed, d_ed, f_pre, f_spr,)
        # elif name == 'Fatigue':
        #     m = material.StainlessSteel(es=160e3, fy=210.0, fu=570.0, epsilon_u=0.35, 
        #                                 epsilon_platform=0.001, esh=0.02*160e3)
        #     b = brace.LLPSCB(m, angle_deg, l_brace, design_drift, 
        #                     reserved_length, slip, chuck_k_ratio,
        #                     l_ed, d_ed, f_pre, f_spr,)
        
        # initialize model
        modelSetter = opensees_setter.ModelSetter()
        modelSetter.initialize()

        # nodes and BCs
        ops.node(1, 0.0, 0.0)
        ops.node(2, b.l_brace, 0.0)
        ops.fix(1, 1, 1, 1)
        ops.fix(2, 0, 1, 1)

        b_NO = b.build_in_opensees(protocol_out_dir)
        ops.element('Truss', 1, 1, 2, b.a_ed, b_NO)
        modelSetter.set_analysis(name, protocol, step_len)

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
            
        # Plot results
        ps = plot_simu.plot_simu(protocol_out_dir, protocol_out_dir, width, height, font_size, 
                                l_brace = b.l_brace, l_ed=b.l_ed, d_ed=b.d_ed)
        ps.plot_brace_force_disp(x_min = -120, x_max = 120, y_min = -200, y_max = 1000, 
                                x_major_locator=40, x_minor_locator=10, y_major_locator=200, y_minor_locator=50)
        ps.plot_ratchet_force_disp(x_min = -800, x_max = 50, y_min = -200, y_max = 1000, 
                        x_major_locator=200, x_minor_locator=50, y_major_locator=200, y_minor_locator=50)
