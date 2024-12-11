import lcapy
from lcapy.componentRelation import ComponentRelation
from lcapy.impedanceConverter import getSourcesFromCircuit, getOmegaFromCircuit
from lcapy.solutionStep import SolutionStep
from lcapy.jsonExportBase import JsonExportBase
from lcapy.jsonExportVCElement import VCElement


class JsonVCValueExport(JsonExportBase):
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

        self.vcElements: list[VCElement] = []
        self.relation: ComponentRelation = ComponentRelation.none
        self.valueFieldKeys = self._getValueFieldKeys("val")

    def getDictForStep(self, step: str, solution: 'lcapy.Solution') -> dict:
        self._updateObjectValues(step, solution)

        if self.vcElements:
            elm0 = self.vcElements[0]
            elm1 = self.vcElements[1]
            elm2 = self.vcElements[2]

            as_dict = {
                'oldNames': [elm2.name, elm2.uName, elm2.iName],
                'names1': [elm0.name, elm0.uName, elm0.iName],
                'names2': [elm1.name, elm1.uName, elm1.iName],
                'oldValues': [elm2.value, elm2.u, elm2.i],
                'values1': [elm0.value, elm0.u, elm0.i],
                'values2': [elm1.value, elm1.u, elm1.i],
                'convOldValue': [elm2.convVal],
                'convValue1': [elm0.convVal],
                'convValue2': [elm1.convVal],
                'relation': [self.relation.to_string()],
                'equation': [None, None]
            }

            try:
                for key in ['oldValues', 'values1', 'values2', 'convOldValue', 'convValue1', 'convValue2']:
                    assert isinstance(as_dict[key], list)
                    for idx, val in enumerate(as_dict[key]):
                        if as_dict[key][idx] is not None:
                            as_dict[key][idx] = self.latexWithPrefix(val)
            except KeyError:
                raise AssertionError(f"A filed which name includes val or Val is not in the export dict. Key: {key}")
        else:
            as_dict = {
                'oldNames': [None, None, None],
                'names1': [None, None, None],
                'names2': [None, None, None],
                'oldValues': [None, None, None],
                'values1': [None, None, None],
                'values2': [None, None, None],
                'convOldValue': [None],
                'convValue1': [None],
                'convValue2': [None],
                'relation': [None],
                'equation': [None, None]
            }

        return as_dict

    def _updateObjectValues(self, step: str, solution: 'lcapy.Solution'):
        self.solStep: 'lcapy.solutionStep' = solution[step]
        self.simpCircuit: 'lcapy.Circuit' = solution[step].circuit  # circuit with less elements (n elements)
        self.omega_0 = getOmegaFromCircuit(self.simpCircuit, getSourcesFromCircuit(self.simpCircuit))

        if not self._isInitialStep():
            self.circuit: 'lcapy.Circuit' = solution[step].lastStep.circuit  # circuit with more elements (n+1 elements)

            for name in solution[step].cpts:
                self.vcElements.append(VCElement(self.solStep, self.circuit, self.omega_0, name, self.prefixer,
                                                 self.voltSym))
            self.vcElements.append(
                VCElement(self.solStep, self.simpCircuit, self.omega_0, solution[step].newCptName, self.prefixer,
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
        return not (self.solStep.cpt1 and self.solStep.cpt2
                    and self.solStep.newCptName and self.solStep.lastStep) and self.solStep
