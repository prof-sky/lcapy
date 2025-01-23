import sympy

from lcapy.netlistLine import NetlistLine
from lcapy.impedanceConverter import ValueToComponent
from lcapy.unitWorkAround import UnitWorkAround as uwa
from lcapy import t
from lcapy.dictExportBase import DictExportBase


class DictExportElement(DictExportBase):
    def __init__(self, solStep: 'lcapy.solutionStep', circuit: 'lcapy.Circuit',
                 omega_0, compName: str, langSymbols: 'lcapy.langSymbols.LangSymbols',
                 inHomogeneousCircuit=False, precision=3):
        super().__init__(precision=precision, langSymbol=langSymbols)
        self.circuit = circuit
        self.solStep = solStep
        self.omega_0 = omega_0
        self.inHomogeneousCircuit = inHomogeneousCircuit

        self.suffix = NetlistLine(str(self.circuit[compName])).typeSuffix

        self.uName = self.ls.volt + self.suffix
        self.iName = 'I' + self.suffix
        self._cpxValue, self._value, self.compType = self._convertValue(self.circuit[compName].Z)
        self._i = self.circuit[compName].I(t)
        self._u = self.circuit[compName].V(t)
        self.name = self.compType + self.suffix

    @staticmethod
    def _removeSinCos(value: 'lcapy.expr'):
        for arg in value.sympy.args:
            if isinstance(arg, (sympy.sin, sympy.cos)):
                value = value / arg
        return value

    def _toDictHomogenous(self):
        cpxVal = self._removeSinCos(self.cpxVal)
        value = self._removeSinCos(self.value)
        i = self._removeSinCos(self.i)
        u = self._removeSinCos(self.u)

        return self.exportDictCpt(
            self.name,
            self.uName,
            self.iName,
            self.latexWithPrefix(cpxVal),
            self.latexWithPrefix(value),
            self.latexWithPrefix(u),
            self.latexWithPrefix(i),
            self.hasConversion
        )

    def _toDictNonHomogenous(self):
        return self.exportDictCpt(
            self.name,
            self.uName,
            self.iName,
            self.latexWithPrefix(self.cpxVal),
            self.latexWithPrefix(self.value),
            self.latexWithPrefix(self.u),
            self.latexWithPrefix(self.i),
            self.hasConversion
        )

    def toDict(self):
        if self.inHomogeneousCircuit:
            return self._toDictHomogenous()
        else:
            return self._toDictNonHomogenous()

    def _convertValue(self, cpxVal) -> tuple:
        convValue, convCompType = ValueToComponent(cpxVal, self.omega_0)
        return cpxVal, uwa.addUnit(convValue, convCompType), convCompType

    @property
    def value(self):
        return self.prefixer.getSIPrefixedExpr(self._value)

    @property
    def cpxVal(self):
        return self.prefixer.getSIPrefixedExpr(self._cpxValue)

    @property
    def i(self):
        return self.prefixer.getSIPrefixedExpr(self._i)

    @property
    def u(self):
        return self.prefixer.getSIPrefixedExpr(self._u)

    @property
    def hasConversion(self) -> bool:
        return not self.compType == "Z"
