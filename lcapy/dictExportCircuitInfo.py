from lcapy.dictExportBase import DictExportBase
from sympy.physics.units import Hz
from sympy import parse_expr, pi, Mul
from lcapy import omega0
from lcapy.impedanceConverter import ValueToComponent
from lcapy.unitWorkAround import UnitWorkAround as uwa
from lcapy.dictExport import ExportDict
from lcapy.langSymbols import LangSymbols


class DictExportCircuitInfo(DictExportBase):
    def __init__(self, langSymbols: LangSymbols(), precision=3):
        super().__init__(precision, langSymbols)
        self.omega_0 = None

    def getDictForStep(self, step, solution: 'lcapy.Solution') -> ExportDict:
        compTypes = set()
        sources = []
        cpts = []

        sourceType = None
        cirOmega_0 = None
        sourceVal = None
        cirType = "RLC"

        for cptName in solution[step].circuit.elements.keys():
            cpt = solution[step].circuit.elements[cptName]
            if cpt.type == "V" or cpt.type == "I":
                if cpt.type == "V":
                    sourceType = cpt.type
                    sourceVal = cpt.v.expr_with_units
                else:
                    sourceType = cpt.type
                    sourceVal = cpt.i.expr_with_units

                if cpt.has_ac:
                    if cpt.args[2] is not None:
                        cirOmega_0 = parse_expr(str(cpt.args[2]), local_dict={"pi": pi}) * Hz
                        try:
                            self.omega_0 = float(cpt.args[2])
                        except ValueError:
                            self.omega_0 = str(cpt.args[2])
                    else:
                        cirOmega_0 = omega0
                        self.omega_0 = "omega_0"
                elif cpt.has_dc:
                    cirOmega_0 = Mul(0) * Hz
                else:
                    raise AssertionError("Voltage Source is not ac or dc")

                sources.append(self.step0ExportDictSource(sourceType, cirOmega_0, sourceVal))

            elif not cpt.type == "W":
                value, compType = ValueToComponent(cpt.Z)
                compTypes.add(compType)
                val = self.latexWithPrefix(uwa.addUnit(value, compType))
                cpts.append(self.exportDictCpt(compType + cpt.id, None, None,
                                                            None, val, None, None, False))

        if len(compTypes) == 1:
            if "R" in compTypes:
                compType = "R"
            elif "L" in compTypes:
                compType = "L"
            elif "C" in compTypes:
                compType = "C"
            else:
                raise ValueError("Unexpected type in set types")

        return self.step0ExportDict(step, sources, cpts, compType, solution[step].getImageData(self.ls))
