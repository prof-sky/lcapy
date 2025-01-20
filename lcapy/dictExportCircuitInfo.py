from lcapy.dictExportBase import DictExportBase
from sympy.physics.units import Hz
from sympy import parse_expr, pi, Mul
from lcapy import omega0
from lcapy.impedanceConverter import ValueToComponent
from lcapy.unitWorkAround import UnitWorkAround as uwa
from lcapy.dictExport import ExportDict
from lcapy.langSymbols import LangSymbols
from lcapy.dictExportElement import DictExportElement
from lcapy import t


class DictExportCircuitInfo(DictExportBase):
    def __init__(self, langSymbols: LangSymbols(), precision=3):
        super().__init__(precision, langSymbols)
        self.omega_0 = None

    def getDictForStep(self, step, solution: 'lcapy.Solution') -> ExportDict:
        compTypes = set()
        cpts = []

        cirType = "RLC"

        sources = solution[step].circuit.sources
        if not len(sources) == 1:
            raise AssertionError(f"Number of sources has to be one, sources: {sources}")

        cpt = solution[step].circuit[sources[0]]

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

        source = self.step0ExportDictSource(sourceType, cirOmega_0,
                                            self.exportDictCpt(
                                                cpt.name, self.ls.volt + self.ls.total,
                                                "I"+self.ls.total,
                                                None, None,
                                                self.latexWithPrefix(cpt.V(t)),
                                                self.latexWithPrefix(cpt.I(t)),
                                                False
                                            ))

        allCpts: list[ExportDict] = []
        for name in solution[step].circuit.reactances:
            vcElm = DictExportElement(step, solution[step].circuit, self.omega_0, name, self.ls)
            allCpts.append(vcElm.toDict())
            compTypes.add(vcElm.compType)

        if len(compTypes) == 1:
            if "R" in compTypes:
                cirType = "R"
            elif "L" in compTypes:
                cirType = "L"
            elif "C" in compTypes:
                cirType = "C"
            else:
                raise ValueError("Unexpected type in set types")

        return self.step0ExportDict(step, source, allCpts, cirType, solution[step].getImageData(self.ls))
