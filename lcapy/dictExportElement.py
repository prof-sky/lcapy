import sympy
from sympy.physics.units import deg

import lcapy
from lcapy.impedanceConverter import ValueToComponent
from lcapy.unitWorkAround import UnitWorkAround as uwa
from lcapy import resistance, voltage, current, phasor, Expr
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

        key = list(self.circuit[compName].V(omega_0).keys())[0]

        iCpx = self.circuit[compName].I(omega_0)[key]
        imI = sympy.im(iCpx.expr)
        reI = sympy.re(iCpx.expr)
        self._i = current(sympy.sqrt(imI ** 2 + reI ** 2))
        self.iPhase = sympy.atan2(imI, reI) * 180 / sympy.pi * deg

        uCpx = self.circuit[compName].V(omega_0)[key]
        imU = sympy.im(uCpx.expr)
        reU = sympy.re(uCpx.expr)
        self._u = voltage(sympy.sqrt( imU ** 2 + reU ** 2))
        self.uPhase = sympy.atan2(imU, reU) * 180 / sympy.pi * deg

        self.name = self.compType + self.suffix
        self.imZ = sympy.im(self._cpxValue.expr)
        self.reZ = sympy.re(self._cpxValue.expr)
        self.zPhase = sympy.atan2(imU, reU) * 180 / sympy.pi * deg
        self.zPhase = sympy.atan2(self.imZ, self.reZ) * 180 / sympy.pi * deg
        self._magnitude = resistance(sympy.sqrt( self.imZ ** 2 + self.reZ ** 2))

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
            self.toLatex(self.reZ),
            self.toLatex(self.imZ),
            self.toLatex(self.zPhase),
            self.toLatex(self._value),
            self.toLatex(self._u),
            self.toLatex(self.uPhase),
            self.toLatex(self._i),
            self.toLatex(self.iPhase),
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
            self.latexWithPrefix(self.reZ.round(self.precision)),
            self.latexWithPrefix(self.imZ.round(self.precision)),
            self.latexWithPrefix(self.zPhase),
            self.latexWithPrefix(self._value),
            self.latexWithPrefix(self._u),
            self.latexWithPrefix(self.uPhase),
            self.latexWithPrefix(self._i),
            self.latexWithPrefix(self.iPhase),
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
