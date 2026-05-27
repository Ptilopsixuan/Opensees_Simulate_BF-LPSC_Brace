import openseespy.opensees as ops
from lib import brace, material, setter
from pathlib import Path
import os

# Complete OpenSeesPy version of BraceTestStatic.tcl
if __name__ == "__main__":
    # geometry & material
    l_brace = 5060.0
    P = 30000.0

    m_ed = material.StainlessSteel(es=200e3, fy=210.0, fu=570.0, epsilon_u=0.35, epsilon_platform=0.001, esh=0.02*200e3)
    b = brace.LLPSCB(mat_ed=m_ed, angle_deg=50.0, l_brace=l_brace, design_drift=0.04)

    # initialize model
    modelSetter = setter.ModelSetter()
    analysisSetter = setter.AnalysisSetter(test_type='static', dt=1)
    modelSetter.initialize()

    # nodes and BCs
    ops.node(1, 0.0, 0.0)
    ops.node(2, l_brace, 0.0)
    ops.fix(1, 1, 1, 1)
    ops.fix(2, 0, 1, 1)

    # register materials and create element
    brace_mat_tag = b.build_in_opensees()
    ops.element('Truss', 1, 1, 2, b.a_ed, brace_mat_tag)

    # Analysis setup (this will perform initial analyze(1) and loadConst per setter)
    analysisSetter.setup_analysis()

    # Define loads and pattern (time series linear)
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)
    ops.load(2, P, 0.0, 0.0)

    # Ensure output directory exists and helper for paths
    out_dir = Path(__file__).resolve().parent / '.out'
    out_dir.mkdir(exist_ok=True)
    def outpath(name):
        return str(out_dir / name)

    # Recorders (match tcl outputs) -> files placed into .out
    ops.recorder('Node', '-file', outpath('BraceTest2Disp.out'), '-node', 2, '-dof', 1, 'disp')
    ops.recorder('Node', '-file', outpath('BraceTest2Force.out'), '-node', 1, '-dof', 1, 'reaction')
    ops.recorder('Element', '-file', outpath('BraceTest2BraceStreeStrain.out'), '-ele', 1, 'material', 'stressStrain')
    ops.recorder('Element', '-file', outpath('BraceTest2Dissipator.out'), '-ele', 1, 'material', 'component', 2, 'component', 2, 'component', 2, 'stressStrain')
    ops.recorder('Element', '-file', outpath('BraceTest2Ratchet.out'), '-ele', 1, 'material', 'component', 2, 'component', 2, 'component', 1, 'stressStrain')
    ops.recorder('Element', '-file', outpath('BraceTest2RatchetSystem.out'), '-ele', 1, 'material', 'component', 2, 'stressStrain')
    ops.recorder('Element', '-file', outpath('BraceTest2Spring.out'), '-ele', 1, 'material', 'component', 1, 'stressStrain')

    # cyclic displacement control sequence (copied from tcl)
    numIter_list = [
        104,104,104,104,104,104,104,104,104,104,104,104,
        223,223,223,223,223,223,223,223,223,223,223,223,
        478,478,478,478,478,478,478,478,478,478,478,478,
        734,734,734,734,734,734,734,734,734,734,734,734,
        995,995,995,995
    ]
    dU_list = [
        -0.1,0.1,0.1,-0.1, -0.1,0.1,0.1,-0.1, -0.1,0.1,0.1,-0.1,
        -0.1,0.1,0.1,-0.1, -0.1,0.1,0.1,-0.1, -0.1,0.1,0.1,-0.1,
        -0.1,0.1,0.1,-0.1, -0.1,0.1,0.1,-0.1, -0.1,0.1,0.1,-0.1,
        -0.1,0.1,0.1,-0.1, -0.1,0.1,0.1,-0.1, -0.1,0.1,0.1,-0.1,
        -0.1,0.1,0.1,-0.1
    ]

    # run cycles
    for numIter, dU in zip(numIter_list, dU_list):
        ops.integrator('DisplacementControl', 2, 1, dU)
        if ops.analyze(numIter) != 0:
            raise RuntimeError(f'Analysis failed at step with dU={dU}, numIter={numIter}')
        factor = ops.getTime()
        disp2 = ops.nodeDisp(2, 1)
        print(f"{factor*P} {disp2}")

    print('Analysis successful')




