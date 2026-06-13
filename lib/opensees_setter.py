import openseespy.opensees as ops

class ModelSetter:
    """Class to initialize the OpenSees model with standard settings."""
    def __init__(self, ndm: int = 2, ndf: int = 3):
        self.ndm = ndm
        self.ndf = ndf

    def initialize(self) -> None:
        ops.wipe()
        ops.model('basic', '-ndm', self.ndm, '-ndf', self.ndf)

    def set_analysis(self, test_type: str, protocol: dict, step_len: float) -> None:
        if test_type == 'Static' or test_type == 'Fatigue' or test_type == 'Dynamic':
            # Follow user's preferred sequence
            ops.constraints('Transformation')
            ops.numberer('RCM')
            # Energy incremental test (tolerance, maxIter)
            ops.test('EnergyIncr', 1.0e-6, 5000)
            # algorithm: Modified Newton for better nonlinear convergence
            ops.algorithm('ModifiedNewton')
            ops.system('BandGeneral')
            # Use LoadControl with specified dt (uses integer step if appropriate)
            ops.integrator('LoadControl', 1)
            ops.analysis('Static')
            # perform a single load step and then hold loads constant at time 0.0
            ops.loadConst('-time', 0.0)
###################################################################
###################         unusable        #######################
###################################################################
        # elif test_type == 'dynamic':
        #     ops.constraints('Plain')
        #     ops.numberer('RCM')
        #     # convergence test and nonlinear algorithm for robustness
        #     ops.test('NormDispIncr', 1.0e-5, 2000)
        #     ops.algorithm('NewtonLineSearch')
        #     ops.system('BandGeneral')
        #     # Newmark integrator for transient analysis
        #     ops.integrator('Newmark', 0.5, 0.25)
        #     # small Rayleigh damping to improve transient stability (adjust as needed)
        #     ops.rayleigh(0.02, 0.0, 0.0, 0.0)
        #     ops.analysis('Transient')
####################################################################
        else:
            raise ValueError(f"Unsupported test type: {test_type}")
        
    def set_disp_protocol(self, protocol: dict, step_len: float) -> tuple:
        """Set analysis protocol parameters."""
        numIter,du = [], []
        for key, value in protocol.items():
            temp_unmIter = [int(key / step_len)] * value * 4
            numIter.extend(temp_unmIter)
            temp_du = [step_len] * value * 4
            du.extend(temp_du)
        for i in range(len(du)):
            if i % 4 == 0 or i % 4 == 3:
                du[i] = -du[i]
        return numIter, du
        
if __name__ == "__main__":
    # Example usage
    modelSetter = ModelSetter()
    modelSetter.initialize()
    modelSetter.set_analysis(test_type='static')
    protocol = { 10.4: 3, 22.3: 3, 47.8: 3, 73.4: 3, 99.5: 1 }
    numIter, du = modelSetter.set_disp_protocol(protocol, step_len=0.05)
    print(numIter)
    print(du)