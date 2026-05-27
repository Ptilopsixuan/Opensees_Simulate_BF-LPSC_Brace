import openseespy.opensees as ops

class ModelSetter:
    """Class to initialize the OpenSees model with standard settings."""
    def __init__(self, ndm: int = 2, ndf: int = 3):
        self.ndm = ndm
        self.ndf = ndf

    def initialize(self) -> None:
        ops.wipe()
        ops.model('basic', '-ndm', self.ndm, '-ndf', self.ndf)

class AnalysisSetter:
    """Class to set up the analysis parameters for the OpenSees model."""
    def __init__(self, test_type: str = 'static', dt: float = 1.0):
        self.test_type = test_type
        self.dt = dt

    def setup_analysis(self) -> None:
        if self.test_type == 'static':
            # Follow user's preferred sequence
            ops.constraints('Transformation')
            ops.numberer('RCM')
            # Energy incremental test (tolerance, maxIter)
            ops.test('EnergyIncr', 1.0e-6, 500)
            # algorithm: Modified Newton for better nonlinear convergence
            ops.algorithm('ModifiedNewton')
            ops.system('BandGeneral')
            # Use LoadControl with specified dt (uses integer step if appropriate)
            ops.integrator('LoadControl', self.dt)
            ops.analysis('Static')
            # perform a single load step and then hold loads constant at time 0.0
            ops.analyze(1)
            ops.loadConst('-time', 0.0)

        elif self.test_type == 'dynamic':
            ops.system('BandGeneral')
            ops.numberer('RCM')
            ops.constraints('Plain')
            ops.integrator('Newmark', 0.5, 0.25)
            ops.algorithm('Linear')
            ops.analysis('Transient')
        else:
            raise ValueError(f"Unsupported test type: {self.test_type}")