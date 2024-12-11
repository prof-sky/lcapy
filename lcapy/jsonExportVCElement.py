from lcapy.netlistLine import NetlistLine
from lcapy.impedanceConverter import ValueToComponent
from lcapy.unitWorkAround import UnitWorkAround as uwa
from lcapy import t


class VCElement:
    def __init__(self, solStep: 'lcapy.solutionStep', circuit: 'lcapy.Circuit',
                 omega_0, compName: str, prefixer: 'lcapy.unitPrefixer.SiUnitPrefixer', voltSym="U"):
        self.circuit = circuit
        self.solStep = solStep
        self.omega_0 = omega_0
        self.prefixer = prefixer

        self.suffix = NetlistLine(str(self.circuit[compName])).typeSuffix
        self.uName = voltSym + self.suffix
        self.iName = 'I' + self.suffix
        self._value, self._convValue, compType = self._checkForConversion(self.circuit[compName].Z)
        self._i = self.circuit[compName].I(t)
        self._u = self.circuit[compName].V(t)
        self.name = compType + self.suffix

    def _checkForConversion(self, value) -> tuple:
        convValue, convCompType = ValueToComponent(value, self.omega_0)
        if 'Z' == convCompType:
            return value, None, 'Z'
        else:
            return value, uwa.addUnit(convValue, convCompType), convCompType

    @property
    def value(self):
        return self.prefixer.getSIPrefixedExpr(self._value)

    @property
    def convVal(self):
        return self.prefixer.getSIPrefixedExpr(self._convValue)

    @property
    def i(self):
        return self.prefixer.getSIPrefixedExpr(self._i)

    @property
    def u(self):
        return self.prefixer.getSIPrefixedExpr(self._u)
