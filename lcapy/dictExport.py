import warnings
import lcapy
from lcapy.componentRelation import ComponentRelation
from lcapy.impedanceConverter import getSourcesFromCircuit, getOmegaFromCircuit
from lcapy.solutionStep import SolutionStep
from lcapy.dictExportBase import DictExportBase
from lcapy.DictExportElement import DictExportElement


class DictExport(DictExportBase):
    """
    Jason Volt Current Value Export
    Creates a json-File with information about the Voltage and Current values for one step
    The format is handy to display the simplification on the Web-UI.
    Takes a step <string> that is part of a Solution <lcapy.Solution> Object. The available steps can be accessed by
    <lcapy.Solution>.available_steps
    represents all information in the circuit in combination with lcapy.JsonCompValueExport. Has to be split up because
    in the user based mode not all information can be known when those files are generated
    """

    def __init__(self, precision=3, voltSym='U'):
        super().__init__(precision, voltSym=voltSym)
        # this class automatically prefixes every field that includes val or Val in the name and transforms it to
        # a latex string before exporting the dictionary
        self.circuit: 'lcapy.Circuit' = None
        self.simpCircuit: 'lcapy.Circuit' = None
        self.omega_0 = None

        self.vcElements: list[DictExportElement] = []
        self.relation: ComponentRelation = ComponentRelation.none
        self.valueFieldKeys = self._getValueFieldKeys("val")

    def getDictForStep(self, step: str, solution: 'lcapy.Solution') -> dict:
        self._updateObjectValues(step, solution)

        if self.vcElements:
            resElem = self.vcElements[-1]
            lwp = self.latexWithPrefix
            as_dict = {
                "canBeSimplified": True,
                "simplifiedTo": {
                    "Z": {"name": resElem.name, "complexVal": lwp(resElem.cpxVal), "val": lwp(resElem.value)},
                    "U": {"name": resElem.uName, "val": lwp(resElem.u)},
                    "I": {"name": resElem.iName, "val": lwp(resElem.i)},
                    "hasConversion": resElem.hasConversion,
                },
                "componentsRelation": self.relation.to_string(),
                "components": [],
                "svgData": resElem.solStep.getImageData()
            }

            for elm in self.vcElements[:-1]:
                as_dict["components"].append(
                    {
                        "Z": {"name": elm.name, "complexVal": lwp(elm.cpxVal), "val": lwp(elm.value)},
                        "U": {"name": elm.uName, "val": lwp(elm.u)},
                        "I": {"name": elm.iName, "val": lwp(elm.i)},
                        "hasConversion": elm.hasConversion,
                    }
                )
            return as_dict

        else:
            return {
                "canBeSimplified": False,
                "simplifiedTo": {
                    "Z": {"name": None, "complexVal": None, "val": None},
                    "U": {"name": None, "val": None},
                    "I": {"name": None, "val": None},
                    "hasConversion": None,
                },
                "componentsRelation": ComponentRelation.none.to_string(),
                "components": [{
                    "Z": {"name": None, "complexVal": None, "val": None},
                    "U": {"name": None, "val": None},
                    "I": {"name": None, "val": None},
                    "hasConversion": None,
                }],
                "svgData": None
            }

    def _updateObjectValues(self, step: str, solution: 'lcapy.Solution'):
        self.solStep: 'lcapy.solutionStep' = solution[step]
        self.simpCircuit: 'lcapy.Circuit' = solution[step].circuit  # circuit with less elements (n elements)
        self.omega_0 = getOmegaFromCircuit(self.simpCircuit, getSourcesFromCircuit(self.simpCircuit))

        if not self._isInitialStep():
            self.circuit: 'lcapy.Circuit' = solution[step].lastStep.circuit  # circuit with more elements (n+1 elements)

            for name in solution[step].cpts:
                self.vcElements.append(DictExportElement(self.solStep, self.circuit, self.omega_0, name, self.prefixer,
                                                         self.voltSym))
            self.vcElements.append(
                DictExportElement(self.solStep, self.simpCircuit, self.omega_0, solution[step].newCptName, self.prefixer,
                                  self.voltSym))
            self._updateCompRel()

    def _updateCompRel(self):
        if self.solStep.relation == ComponentRelation.parallel:
            self.relation = ComponentRelation.parallel
        elif self.solStep.relation == ComponentRelation.series:
            self.relation = ComponentRelation.series
        else:
            self.relation = ComponentRelation.none

    def _isInitialStep(self) -> bool:
        assert isinstance(self.solStep, SolutionStep)
        return not (self.solStep.cpts and self.solStep.newCptName and self.solStep.lastStep) and self.solStep
