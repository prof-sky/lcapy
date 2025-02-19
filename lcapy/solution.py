import os.path
import json

import sympy

from lcapy import ConstantDomainExpression
from .solutionStep import SolutionStep
from ordered_set import OrderedSet
from typing import Iterable
from warnings import warn
from lcapy import state
from lcapy.mnacpts import R, L, C, Z
from lcapy import DrawWithSchemdraw
from lcapy.dictExport import DictExport
from lcapy.dictExportCircuitInfo import DictExportCircuitInfo
from lcapy.unitWorkAround import UnitWorkAround as uwa
from typing import Union
from lcapy.langSymbols import LangSymbols
from lcapy.dictExportBase import ExportDict
from lcapy.impedanceConverter import ImpedanceToComponent

class Solution:
    def __init__(self, steps: list[SolutionStep], langSymbols: LangSymbols):
        """
        This class simplifies the Solution and handles the access to all data that is necessary to create a step-by-step
        solution to a circuit. The input is of this class is the output of simplify_Stepwise
        :param steps:
        """
        self._attributes = {}
        self.available_steps = []

        self.langSymbols = langSymbols
        self.mapKey = dict([("initialCircuit", "step0")])

        # convert the steps returned from simplify_stepwise to SolutionSteps
        # the simplify function cant return SolutionSteps because it imports lcapy and therefor results in a circular
        solSteps = steps

        if not solSteps:
            raise AttributeError('can`t create Solution from empty list\n'
                                 'make sure parameter steps isn`t an empty list')

        # name and add first Circuit
        self.available_steps.append("step0")
        self.__setitem__("step0", solSteps[0])
        self.circuitType = self._getCircuitType()
        self.isSymbolic = self._isSymbolic()

        if len(solSteps) >= 2:
            self["step0"].nextStep = solSteps[1]
        else:
            warn("Solution only contains initial circuit and no simplification Steps")
            return

        for i in range(1, len(solSteps)):
            curStep = "step" + str(i)
            self.available_steps.append(curStep)

            self.__setitem__(curStep, solSteps[i])
            self[curStep].lastStep = solSteps[i - 1]

            # the list index is only to len(list) -1 accessible
            if i + 1 <= len(solSteps) - 1:
                self[curStep].nextStep = solSteps[i + 1]

    def __getitem__(self, key):
        try:
            return self._attributes[key]
        except KeyError:
            if key in self.mapKey.keys():
                return self._attributes[self.mapKey[key]]
            else:
                raise KeyError

    def __setitem__(self, key, value):
        self._attributes[key] = value

    def __getattr__(self, key):
        try:
            return self._attributes[key]
        except KeyError:
            if key in self.mapKey.keys():
                return self._attributes[self.mapKey[key]]
            else:
                raise KeyError

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self.__setitem__(key, value)

    def addKeyMapping(self, accessKey, realKey: str):
        """
        If a KeyError is thrown a dictionary is searched. If it is in the dictionary the __getItem__ or __getAttr__
        it is tried again with the specified key in the Dictionary
        :param accessKey: key that you want to use
        :param realKey: key name from this class step0, step1, step2, ...
        :return: nothing / void
        """
        if realKey not in self.available_steps:
            raise KeyError("realKey doesn't exist")

        self.mapKey[accessKey] = realKey

    def removeKeyMapping(self, accessKey):
        if accessKey in self.mapKey.keys():
            self.mapKey.pop(accessKey)
        else:
            warn("accessKey not in mapKey")

    def getAvailableSteps(self, skip: set) -> OrderedSet[str]:
        """
        Returns all available steps
        :param skip: steps to skip
        :return: OrderedSet[str]
        """
        if skip:
            return OrderedSet(self.available_steps) - skip
        else:
            return OrderedSet(self.available_steps)

    @staticmethod
    def getElementSpecificValue(element: Union[R, C, L, Z], unit=False) -> ConstantDomainExpression:
        """
        accesses the value resistance, capacitance, inductance, or impedance of an element based on its type
        :param element: mnacpts.R | mnacpts.C | mnacpts.L | mnacpts.Z
        :param unit: if True the Unit (ohm, F, H) are added to the str
        :return: lcapy.ConstantDomainExpression
        """
        if unit:
            return uwa.addUnit(Solution.getElementSpecificValue(element), element.type)

        state.show_units = False
        if isinstance(element, R):
            returnVal = element.R
        elif isinstance(element, C):
            returnVal = element.C
        elif isinstance(element, L):
            returnVal = element.L
        elif isinstance(element, Z):
            returnVal = element.Z
        else:
            raise NotImplementedError(f"{type(element)} "
                                      f"not supported edit Solution.getElementSpecificValue() to support")

        return returnVal

    def steps(self, skip: set = None) -> Iterable[SolutionStep]:
        """
        yields the steps from the simplification. They can be iterated in a for loop e.g.:
        for step in sol.Steps():
            print(step.solutionText)
            step.circuit.draw()
        :param skip: define a set of steps that should be skipped e.g. the step0 every other step is
        named as follows: step1, step2, ..., step<n>
        :return:
        """
        for step in self.getAvailableSteps(skip=skip):
            yield self[step]

    @staticmethod
    def check_path(path: str):
        if not os.path.isdir(path) and os.path.isfile(path):
            raise ValueError(f"{path} is a file not a directory")
        elif not os.path.isdir(path) and not path == "":
            os.mkdir(path)

    def draw(self, filename: str = "circuit", path: str = None):
        """
        saves a svg-File for each step in the Solution.
        can raise a value error if path is not a directory
        :param filename: optional filename, files will be named filename_step<n>.svg n = 0,1 ..., len(availableSteps)
        :param path: directory in which to save the json-File in, if None save in current directory
        :return: nothing
        """

        if path is None:
            path = ""

        Solution.check_path(path)

        for step in self.available_steps:
            self.drawStep(step, filename=filename, path=path)

    def drawStep(self, step, filename=None, path: str = None) -> str:
        """
        draws the circuit for a specific step
        :param step: step0, step1, step2, ..., step<n> ..., self.getAvailableSteps returns all valid steps
        :param filename: optional filename, files will be named filename_step<n>.svg n = 0,1 ..., len(availableSteps)
        :param path: directory in which to save the json-File in, if None path is current directory
        :return: nothing
        """
        if path is None:
            path = ""

        if filename is None:
            filename = self.filename
        filename = os.path.splitext(filename)[0]

        DrawWithSchemdraw(self[step].circuit, fileName=filename + f"_{step}.svg", langSymbols=self.langSymbols).draw(path=path)

        return os.path.join(path, filename + f"_{step}.svg")

    def exportCircuitInfo(self, step) -> ExportDict:

        export = DictExportCircuitInfo(self.langSymbols, self.circuitType, self.isSymbolic)
        stepData = export.getDictForStep(step, self)

        return stepData

    def exportStepAsDict(self, step) -> ExportDict:
        """
        {
            "canBeSimplified": "True/False",  # bool
            "simplifiedTo": {
                "Z": {"name": "Rs1", "complexVal": "cplxVal", "val": "bslVal"},  # val = null if not convertible
                "U": {"name": "Us1", "val": "voltageVal"},
                "I": {"name": "Is1", "val": "currentVal"},
                "hasConversion": True/False # bool
            },
            "componentsRelation": "series...",
            "components": [
                # cpt1
                {
                    "Z": {"name": "Rs1", "complexVal": "cplxVal", "val": "bslVal"},  # val = null if not convertible
                    "U": {"name": "Us1", "val": "voltageVal"},
                    "I": {"name": "Is1", "val": "currentVal"},
                    "hasConversion": True/False # bool
                },
                # cpt2
                {
                    "Z": {"name": "Rs1", "complexVal": "cplxVal", "val": "bslVal"},  # val = null if not convertible
                    "U": {"name": "Us1", "val": "voltageVal"},
                    "I": {"name": "Is1", "val": "currentVal"},
                    "hasConversion": True/False # bool
                }
            ],
            "svgData": "svgDataString"
        }
        :param step: the step that is exported as the jason
        :return:
        """
        return DictExport(self.langSymbols, self.circuitType, self.isSymbolic).getDictForStep(step, self)

    def exportStepAsJson(self, step: str, path: str = None, filename: str ="circuit", debug: bool = False,
                         ) -> str:
        """
            {
                "canBeSimplified": "True/False",  # bool
                "simplifiedTo": {
                    "Z": {"name": "Rs1", "complexVal": "cplxVal", "val": "bslVal"},  # val = null if not convertible
                    "U": {"name": "Us1", "val": "voltageVal"},
                    "I": {"name": "Is1", "val": "currentVal"},
                    "hasConversion": True/False # bool
                },
                "componentsRelation": "series...",
                "components": [
                    # cpt1
                    {
                        "Z": {"name": "Rs1", "complexVal": "cplxVal", "val": "bslVal"},  # val = null if not convertible
                        "U": {"name": "Us1", "val": "voltageVal"},
                        "I": {"name": "Is1", "val": "currentVal"},
                        "hasConversion": True/False # bool
                    },
                    # cpt2
                    {
                        "Z": {"name": "Rs1", "complexVal": "cplxVal", "val": "bslVal"},  # val = null if not convertible
                        "U": {"name": "Us1", "val": "voltageVal"},
                        "I": {"name": "Is1", "val": "currentVal"},
                        "hasConversion": True/False # bool
                    }
                ],
                "svgData": "svgDataString"
            }

        raises a value Error if information is missing in a step use try/except or when Path does not point to a file
        :param step: string with step name e.g. step0, step1 ...
        :param debug: if ture print the dictionary that is used for creating the json file
        :param stepData: the data from exportStepAsDict
        :param path:  path to save the json-File in if None save in current directory
        :param filename: svg-File will be named <filename>_step<n>.svg n = 0 | 1 | ...| len(availableSteps)
        :param simpStep: if true simplification step info is exported, which components got combined and
        what values result from that
        :param cvStep: if true the current and voltages for this step will be exported, for each component in the step
        voltage, current, impedance and a transformation to R, L, C if possible will be exported
        :return: nothing
        """

        if path is None:
            path = ""

        Solution.check_path(path)
        filename = os.path.splitext(filename)[0]

        stepData = self.exportStepAsDict(step)

        if debug:
            print(stepData)

        fullPathName = os.path.join(path, filename) + "_" + step + ".json"
        with open(fullPathName, "w", encoding="utf-8") as f:
            json.dump(stepData, f, ensure_ascii=False, indent=4)

        return fullPathName

    def exportAsJsonFiles(self, path: str = None, filename: str = "circuit", debug: bool = False,
                          simpStep: bool = True, cvStep: bool = True):
        """
        save a json-File for each step in available_steps.
        Files are named step<n> n = 0, 1 ..., len(availableSteps)
        can raise a value error, see exportStepAsJson for more information

        :param debug: print dictionary that is used to create the json-File
        :param path: directory in which to save the json-File in, if None save in current directory
        :param filename: svg-File will be named <filename>_step<n>.svg n = 0,1 ..., len(availableSteps)
        :param simpStep: if true simplification step info is exported, which components got combined and
        what values result from that
        :param cvStep: if true the current and voltages for this step will be exported, for each component in the step
        voltage, current, impedance and a transformation to R, L, C if possible will be exported
        :return:
        """

        for step in self.available_steps:
            stepData = self.exportStepAsDict(step)
            self.exportStepAsJson(step, path=path, filename=filename, debug=debug)

    def exportAsDicts(self) -> list[dict]:
        """
        :return: list of dictionaries, list contains each step as a dict for details of dict see exportStepAsDict
        """
        dicts = []
        for step in self.available_steps:
            dicts.append(self.exportStepAsDict(step))

        return dicts

    def _getCircuitType(self):

        types = set()
        for cptName in self['step0'].circuit.reactances:
            cptType = ImpedanceToComponent(str(self['step0'].circuit[cptName]))[0]
            types.add(cptType)

        if len(types) == 1:
            if "R" in types:
                return "R"
            elif "L" in types:
                return "L"
            elif "C" in types:
                return "C"
            elif "Z" in types:
                return "RLC"
            else:
                raise ValueError("Unexpected type in set types")
        else:
            return "RLC"

    def _isSymbolic(self):

        isSymbolic = True
        for cptName in self['step0'].circuit.reactances:
            if not self['step0'].circuit[cptName].impedance.symbols:
                isSymbolic = False
                break

        return isSymbolic

