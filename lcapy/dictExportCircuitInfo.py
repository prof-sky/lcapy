from lcapy.dictExportBase import DictExportBase
from sympy.physics.units import Hz
from sympy import parse_expr, pi, Mul
from lcapy import omega0
from lcapy.impedanceConverter import ValueToComponent
from lcapy.unitWorkAround import UnitWorkAround as uwa
from lcapy.dictExport import ExportDict


class DictExportCircuitInfo(DictExportBase):
    def __init__(self, precision=3):
        super().__init__(precision)
        self.omega_0 = None

    def getDictForStep(self, step, solution: 'lcapy.Solution') -> ExportDict:
        stepData = self.emptyExportDict
        stepData["step"] = step
        stepData["svgData"] = solution[step].getImageData()
        stepData["components"] = []

        for cptName in solution[step].circuit.elements.keys():
            cpt = solution[step].circuit.elements[cptName]
            if cpt.type == "V" or cpt.type == "I":
                if cpt.type == "V":
                    stepData["source"] = self.exportDictCpt(cpt.name, self.voltSym + 'ges', None,
                                                            None, None,
                                                            self.latexWithPrefix(cpt.v.expr_with_units), None, False)
                else:
                    stepData["source"] = self.exportDictCpt(cptName, None, 'Iges',
                                                            None, None,
                                                            None, self.latexWithPrefix(cpt.i.expr_with_units), False)

                if cpt.has_ac:
                    if cpt.args[2] is not None:
                        stepData["omega_0"] = self.latexWithPrefix(
                            parse_expr(str(cpt.args[2]), local_dict={"pi": pi}) * Hz
                        )
                        try:
                            self.omega_0 = float(cpt.args[2])
                        except ValueError:
                            self.omega_0 = str(cpt.args[2])
                    else:
                        stepData["omega_0"] = self.latexWithPrefix(omega0)
                        self.omega_0 = "omega_0"
                elif cpt.has_dc:
                    stepData["omega_0"] = self.latexWithPrefix(Mul(0) * Hz)
                else:
                    raise AssertionError("Voltage Source is not ac or dc")

            elif not cpt.type == "W":
                value, compType = ValueToComponent(cpt.Z)
                val = self.latexWithPrefix(uwa.addUnit(value, compType))
                stepData["components"].append(self.exportDictCpt(compType + cpt.id, None, None,
                                                            None, val, None, None, False))

        return stepData
