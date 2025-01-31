import sympy

from lcapy.impedanceConverter import ValueToComponent
from lcapy.unitWorkAround import UnitWorkAround as uwa
from lcapy import t
from lcapy.dictExportBase import DictExportBase
from typing import Union
from lcapy import resistance


class DictExportElement(DictExportBase):
    def __init__(self, solStep: 'lcapy.solutionStep', circuit: 'lcapy.Circuit',
                 omega_0, compName: str, langSymbols: 'lcapy.langSymbols.LangSymbols',
                 inHomCir=False, precision=3):
        super().__init__(precision=precision, langSymbol=langSymbols)
        self.circuit = circuit
        self.solStep = solStep
        self.omega_0 = omega_0

        self.toCptDict = self._toCptDictHom if inHomCir else self._toCptDictNHom
        self.inHomogeneousCircuit = inHomCir

        self.suffix = self.circuit[compName].id

        self._cpxValue, self._value, self.compType = self._convertValue(self.circuit[compName].Z)
        if compName[0] in ["I", "V"]:
            self.compType = compName[0]
            self.uName = self.ls.volt + self.ls.total
            self.iName = 'I' + self.ls.total
        else:
            self.uName = self.ls.volt + self.suffix
            self.iName = 'I' + self.suffix

        self._i = self.circuit[compName].I(t)
        # if it is a capacitor in an ac circuit where sin and cos is canceled out with _removeSinCos current
        # gets negative
        self._i = self._i * -1 if self.compType == "C" and self.circuit.has_ac and inHomCir else self._i

        self._u = self.circuit[compName].V(t)
        self.name = self.compType + self.suffix
        self._impedance = resistance(sympy.sqrt(sympy.im(self._cpxValue.expr)**2+sympy.re(self._cpxValue.expr)**2))

    @staticmethod
    def _removeSinCos(value: 'lcapy.expr'):
        for arg in value.sympy.args:
            if isinstance(arg, (sympy.sin, sympy.cos)):
                value = value / arg
        return value

    def _toCptDictHom(self) -> 'ExportDict':
        """
        toComponentDictHomogenous
        :return: a self.exportDictCpt in a homogenous circuit (only R, L or C) -> cancel out all sin and cos in results
        """
        impedance = self._removeSinCos(self.impedance)
        value = self._removeSinCos(self.value)
        i = self._removeSinCos(self.i)
        u = self._removeSinCos(self.u)

        return self.exportDictCpt(
            self.name,
            self.uName,
            self.iName,
            self.latexWithPrefix(impedance),
            self.latexWithPrefix(value),
            self.latexWithPrefix(u),
            self.latexWithPrefix(i),
            self.hasConversion
        )

    def _toCptDictNHom(self) -> 'ExportDict':
        """
        toComponentDictNonHomogenous
        :return: a self.exportDictCpt in a non-homogenous circuit (R, L, C in some combination) -> return results as
        they are calculated by lcapy
        """
        return self.exportDictCpt(
            self.name,
            self.uName,
            self.iName,
            self.latexWithPrefix(self.impedance),
            self.latexWithPrefix(self.value),
            self.latexWithPrefix(self.u),
            self.latexWithPrefix(self.i),
            self.hasConversion
        )

    def toCptDict(self) -> 'ExportDict':
        # dynamically assigned at runtime see __init__
        pass

    def _returnVal(self, value, prefixed=False) -> Union['lcapy.expr', sympy.Mul, str]:
        if prefixed:
            return self.prefixer.getSIPrefixedExpr(value)
        else:
            return value

    def toSourceDict(self):
        return self.step0ExportDictSource(self.compType, self.omega_0, self.toCptDict())

    def _convertValue(self, cpxVal) -> tuple:
        convValue, convCompType = ValueToComponent(cpxVal, self.omega_0)
        return cpxVal, uwa.addUnit(convValue, convCompType), convCompType

    @property
    def value(self, prefixed=True):
        return self._returnVal(self._value, prefixed)

    @property
    def cpxVal(self, prefixed=True):
        return self._returnVal(self._cpxValue, prefixed)

    @property
    def i(self, prefixed=True):
        return self._returnVal(self._i, prefixed)

    @property
    def u(self, prefixed=True):
        return self._returnVal(self._u, prefixed)

    @property
    def hasConversion(self) -> bool:
        return not self.compType == "Z"

    @property
    def impedance(self, prefixed=True):
        return self._returnVal(self._impedance, prefixed)
