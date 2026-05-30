import openseespy.opensees as ops
from lib import brace, material, setter
from pathlib import Path
import numpy as np
import os

# Complete OpenSeesPy version of BraceTestStatic.tcl
if __name__ == "__main__":
    # geometry & material
    l_brace = 5060.0
    P = 30000.0

    m = material.StainlessSteel(es=130e3, fy=210.0, fu=570.0, epsilon_u=0.35, 
                                epsilon_platform=0.001, esh=0.02*130e3)
    b = brace.LLPSCB(mat_ed=m, angle_deg=45.0, l_brace=l_brace, design_drift=0.04, 
                     reserved_length = 700, slip = 2.0, chuck_k_ratio=1.6,
                     l_ed = 1800.0, d_ed = 44, f_pre = 15e3, f_spr = 200e3,)

    # initialize model
    modelSetter = setter.ModelSetter()
    analysisSetter = setter.AnalysisSetter(test_type='static', dt=1)
    modelSetter.initialize()

    # nodes and BCs
    ops.node(1, 0.0, 0.0)
    ops.node(2, b.l_brace, 0.0)
    ops.fix(1, 1, 1, 1)
    ops.fix(2, 0, 1, 1)

        # Ensure output directory exists and helper for paths
    out_dir = Path(__file__).resolve().parent / '.out'
    out_dir.mkdir(exist_ok=True)
    def outpath(name):
        return str(out_dir / name)
    
    b.build_in_opensees(outpath)

    # Analysis setup (this will perform initial analyze(1) and loadConst per setter)
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.test('EnergyIncr', 1.0e-6, 5000)
    ops.algorithm('ModifiedNewton')
    ops.system('BandGeneral')
    ops.integrator('LoadControl', 1)
    ops.analysis('Static')

    # initial analyze and hold
    ops.loadConst('-time', 0.0)

    # Define loads and pattern (time series linear)
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)
    ops.load(2, P, 0.0, 0.0)



    

    # cyclic displacement control sequence (copied from tcl)
    numIter_list = [
        104,104,104,104,104,104,104,104,104,104,104,104,
        223,223,223,223,223,223,223,223,223,223,223,223,
        478,478,478,478,478,478,478,478,478,478,478,478,
        734,734,734,734,734,734,734,734,734,734,734,734,
        995,995,995,995
    ]
    dU_list = [
        -0.05,0.05,0.05,-0.05, -0.05,0.05,0.05,-0.05, -0.05,0.05,0.05,-0.05,
        -0.05,0.05,0.05,-0.05, -0.05,0.05,0.05,-0.05, -0.05,0.05,0.05,-0.05,
        -0.05,0.05,0.05,-0.05, -0.05,0.05,0.05,-0.05, -0.05,0.05,0.05,-0.05,
        -0.05,0.05,0.05,-0.05, -0.05,0.05,0.05,-0.05, -0.05,0.05,0.05,-0.05,
        -0.05,0.05,0.05,-0.05
        # -0.01,0.01,0.01,-0.01, -0.01,0.01,0.01,-0.01, -0.01,0.01,0.01,-0.01,
        # -0.01,0.01,0.01,-0.01, -0.01,0.01,0.01,-0.01, -0.01,0.01,0.01,-0.01,
        # -0.01,0.01,0.01,-0.01, -0.01,0.01,0.01,-0.01, -0.01,0.01,0.01,-0.01,
        # -0.01,0.01,0.01,-0.01, -0.01,0.01,0.01,-0.01, -0.01,0.01,0.01,-0.01,
        # -0.01,0.01,0.01,-0.01
    ]

    # run cycles
    for numIter, dU in zip(numIter_list, dU_list):
        ops.integrator('DisplacementControl', 2, 1, dU)
        if ops.analyze(numIter) != 0:
            raise RuntimeError(f'Analysis failed at step with dU={dU}, numIter={numIter}')
        factor = ops.getTime()
        disp2 = ops.nodeDisp(2, 1)
        # print(f"{factor*P} {disp2}")

    # print('Analysis successful')

    # Execute analyze_brace_results.py after analysis completes
    with open('analyze_brace_results.py', 'r', encoding='utf-8') as f:
        exec(f.read())




