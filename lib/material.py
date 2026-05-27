import openseespy as ops

class Material:
    """Base material container with simple derived properties and
    optional OpenSeesPy registration helper.

    Attributes:
        es: Young's modulus (MPa)
        fy: yield stress (MPa)
        fu: ultimate stress (MPa)
        epsilon_u: ultimate strain
    """
    _counter = 0

    def __init__(self, es: float, fy: float, fu: float, epsilon_u: float):
        type(self)._counter += 1
        self.NO = type(self)._counter
        self.es = float(es)
        self.fy = float(fy)
        self.fu = float(fu)
        self.epsilon_u = float(epsilon_u)
        self._supplement()

    def _supplement(self) -> None:
        self.epsilon_y = self.fy / self.es


class Steel(Material):
    """Standard mild steel container."""
    def __init__(self, es: float, fy: float, fu: float, epsilon_u: float):
        super().__init__(es, fy, fu, epsilon_u)


class StainlessSteel(Material):
    def __init__(self, es: float, fy: float, fu: float, epsilon_u: float, epsilon_platform: float, esh: float):
        super().__init__(es, fy, fu, epsilon_u)
        self.epsilon_sh = self.epsilon_y + float(epsilon_platform)
        self.esh = float(esh)

