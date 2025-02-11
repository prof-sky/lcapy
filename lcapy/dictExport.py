import lcapy
from lcapy.componentRelation import ComponentRelation
from lcapy.impedanceConverter import getSourcesFromCircuit, getOmegaFromCircuit
from lcapy.solutionStep import SolutionStep
from lcapy.dictExportBase import DictExportBase
from lcapy.dictExportElement import DictExportElement
from lcapy.dictExportBase import ExportDict
from lcapy.langSymbols import LangSymbols


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

    def __init__(self, langSymbol: LangSymbols(), circuitType="RLC", isSymbolic=False, precision=3):
        super().__init__(precision, langSymbol, circuitType, isSymbolic)
        # this class automatically prefixes every field that includes val or Val in the name and transforms it to
        # a latex string before exporting the dictionary
        self.circuit: 'lcapy.Circuit' = None
        self.simpCircuit: 'lcapy.Circuit' = None
        self.omega_0 = 0
        self.imageData = None

        self.vcElements: list[DictExportElement] = []
        self.allVcElements: list[DictExportElement] = []
        self.relation: ComponentRelation = ComponentRelation.none
        self.valueFieldKeys = self._getValueFieldKeys("val")

    def getDictForStep(self, step: str, solution: 'lcapy.Solution') -> ExportDict:
        self._updateObjectValues(step, solution)

        if self.vcElements:
            resElem = self.vcElements[-1]

            cpts = []
            for elm in self.vcElements[:-1]:
                cpts.append(elm.toCptDict())

            allCpts = []
            for elm in self.allVcElements:
                allCpts.append(elm.toCptDict())

            stepData = self.exportDict(
                step, True, resElem.toCptDict(), self.relation, self.imageData, cpts, allCpts
            )

            return stepData

        elif step == "step0":
            return solution.exportCircuitInfo(step)

        else:
            return self.emptyExportDict

    def _updateObjectValues(self, step: str, solution: 'lcapy.Solution'):
        self.solStep: 'lcapy.solutionStep' = solution[step]
        self.simpCircuit: 'lcapy.Circuit' = solution[step].circuit  # circuit with less elements (n elements)
        self.omega_0 = getOmegaFromCircuit(self.simpCircuit, getSourcesFromCircuit(self.simpCircuit))
        self.imageData = solution[step].getImageData(langSymbols=self.ls)

        if not self._isInitialStep():
            self.circuit: 'lcapy.Circuit' = solution[step].lastStep.circuit  # circuit with more elements (n+m elements)

            for name in solution[step].cpts:
                self.vcElements.append(DictExportElement(self.solStep, self.circuit, self.omega_0, name, self.ls,
                                                         self.isHomCir, prefAndUnit=(not self.isSymbolic)))
            self.vcElements.append(
                DictExportElement(self.solStep, self.simpCircuit, self.omega_0, solution[step].newCptName, self.ls,
                                  self.isHomCir, prefAndUnit=(not self.isSymbolic)))
            self._updateCompRel()

            for name in solution[step].circuit.reactances:
                self.allVcElements.append(DictExportElement(self.solStep, solution[step].circuit, self.omega_0, name,
                                                            self.ls, self.isHomCir, prefAndUnit=(not self.isSymbolic)))

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
