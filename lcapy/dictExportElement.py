import sympy
from sympy import re,im
from sympy.physics.units import deg

from lcapy.impedanceConverter import ValueToComponent
from lcapy.unitWorkAround import UnitWorkAround as uwa
from lcapy import t, j, resistance, phasor, Expr
from lcapy.dictExportBase import DictExportBase
from typing import Union


class DictExportElement(DictExportBase):
    def __init__(self, solStep: 'lcapy.solutionStep', circuit: 'lcapy.Circuit',
                 omega_0, compName: str, langSymbols: 'lcapy.langSymbols.LangSymbols',
                 inHomCir=False, prefAndUnit=True, precision=3):
        super().__init__(precision=precision, langSymbol=langSymbols, isSymbolic=(not prefAndUnit))
        self.circuit = circuit
        self.solStep = solStep
        self.omega_0 = omega_0

        self._returnFkt = self.prefixer.getSIPrefixedExpr if prefAndUnit else self._returnExpr
        self.prefAndUnit = prefAndUnit

        self.toCptDict = self._toCptDictNoUnitNoPrefix if self.isSymbolic else self._toCptDict
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
        self._u = self.circuit[compName].V(t)
        self.name = self.compType + self.suffix
        self._magnitude = resistance(sympy.sqrt(sympy.im(self._cpxValue.expr) ** 2 + sympy.re(self._cpxValue.expr) ** 2))

    @staticmethod
    def _removeSinCos(value: 'lcapy.expr'):
        for arg in value.sympy.args:
            if isinstance(arg, (sympy.sin, sympy.cos)):
                value = value / arg
        return value

    def _toCptDictNoUnitNoPrefix(self) -> 'ExportDict':
        """
        toComponentDictHomogenous
        :return: a self.exportDictCpt in a homogenous circuit (only R, L or C) -> cancel out all sin and cos in results
        """
        return self.exportDictCpt(
            self.name,
            self.uName,
            self.iName,
            self.toLatex(self._magnitude),
            self.toLatex(self._cpxValue),
            self.toLatex(re(self._cpxValue)),
            self.toLatex(im(self._cpxValue)),
            self.toLatex(phasor(self._cpxValue).phase.sympy * 180 / sympy.pi*deg),
            self.toLatex(self._value),
            self.toLatex(self._u.as_phasor().magnitude*self._u.units),
            self.toLatex(phasor(self._u).phase.sympy * 180 / sympy.pi*deg),
            self.toLatex(self._i.as_phasor().magnitude),
            self.toLatex(phasor(self._i).phase.sympy * 180 / sympy.pi * deg),
            self.hasConversion
        )

    def _toCptDict(self) -> 'ExportDict':
        """
        toComponentDictNonHomogenous
        :return: a self.exportDictCpt in a non-homogenous circuit (R, L, C in some combination) -> return results as
        they are calculated by lcapy
        """
        return self.exportDictCpt(
            self.name,
            self.uName,
            self.iName,
            self.latexWithPrefix(self._magnitude),
            self.latexWithPrefix(self._cpxValue),
            self.latexWithPrefix(re(self._cpxValue)),
            self.latexWithPrefix(im(self._cpxValue)),
            self.latexWithPrefix(phasor(self._cpxValue).phase.sympy * 180 / sympy.pi * deg),
            self.latexWithPrefix(self._value),
            self.latexWithPrefix(self._u.as_phasor().magnitude.sympy * self._u.units),
            self.latexWithPrefix(phasor(self._u).phase.sympy * 180 / sympy.pi * deg),
            self.latexWithPrefix(self._i.as_phasor().magnitude.sympy * self._i.units),
            self.latexWithPrefix(phasor(self._i).phase.sympy * 180 / sympy.pi * deg),
            self.hasConversion
        )

    def toCptDict(self) -> 'ExportDict':
        # dynamically assigned at runtime see __init__
        pass

    @staticmethod
    def _returnExpr(value) -> Union[sympy.Mul, str]:
        return value

    def toSourceDict(self):
        return self.step0ExportDictSource(self.compType, self.omega_0, self.toCptDict())

    def _convertValue(self, cpxVal) -> tuple:
        convValue, convCompType = ValueToComponent(cpxVal, self.omega_0)
        return cpxVal, uwa.addUnit(convValue, convCompType), convCompType

    @property
    def value(self):
        return self._returnFkt(self._value)

    @property
    def cpxVal(self):
        return self._returnFkt(self._cpxValue)

    @property
    def i(self):
        return self._returnFkt(self._i)

    @property
    def u(self):
        return self._returnFkt(self._u)

    @property
    def hasConversion(self) -> bool:
        return not self.compType == "Z"

    @property
    def magnitude(self):
        return self._returnFkt(self._magnitude)
