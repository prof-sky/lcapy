import os.path
from enum import Enum

import sympy

import json
from lcapy import ConstantDomainExpression
from .solutionStep import SolutionStep
from ordered_set import OrderedSet
from typing import Iterable
from warnings import warn
from lcapy import state
from lcapy.mnacpts import R, L, C, Z
from lcapy import DrawWithSchemdraw
from lcapy.jsonExportCompValue import JsonCompValueExport
from lcapy.jsonExportVCValues import JsonVCValueExport
from lcapy.jsonExportCircuitInfo import JsonExportCircuitInfo
from lcapy.unitWorkAround import UnitWorkAround as uwa
from typing import Union
from lcapy.langSymbols import LangSymbols


class Solution:
    def __init__(self, steps: list[SolutionStep], langSymbols: LangSymbols = LangSymbols()):
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
        # import
        solSteps = steps

        if not solSteps:
            raise AttributeError('can`t create Solution from empty list\n'
                                 'make sure parameter steps isn`t an empty list')

        # name and add first Circuit
        self.available_steps.append("step0")
        self.__setitem__("step0", solSteps[0])
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

    def exportCircuitInfo(self, step, path: str = None, filename: str ="circuit", debug: bool = False,
                         simpStep: bool = True, cvStep: bool = True) -> str:
        if path is None:
            path = ""

        self.check_path(path)
        filename = os.path.splitext(filename)[0]

        jsonExport = JsonExportCircuitInfo()
        as_dict = jsonExport.getDictForStep(step, self)

        if debug:
            print(as_dict)

        fullPathName = os.path.join(path, filename) + "_" + "circuitInfo" + ".json"
        with open(fullPathName, "w", encoding="utf-8") as f:
            json.dump(as_dict, f, ensure_ascii=False, indent=4)

        return fullPathName

    def exportStepAsJson(self, step, path: str = None, filename: str ="circuit", debug: bool = False,
                         simpStep: bool = True, cvStep: bool = True) -> tuple[str, str]:
        """
        saves a step as a .json File with the following information:
        name1 and name2 -> names of the simplified components
        newName -> name of the simplified component/ new component
        relation -> if the simplification was parallel or in series
        value1 and value2 -> the value of the component e.g. 10 ohm or 10 F ...
        result -> the value of the new Component
        hasConversion -> if a value is transformed to or from impedance
        convVal1, convVal2, convResult -> the value that was transformed from


        raises a value Error if information is missing in a step use try/except or when Path does not point to a file
        :param debug: if ture print the dictionary that is used for creating the json file
        :param step: a step name e.g. step0, step1, step2, ..., step<n>
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

        if not simpStep and not cvStep:
            raise AssertionError("simpStep or cvStep have to be True")

        Solution.check_path(path)
        filename = os.path.splitext(filename)[0]

        if simpStep:
            jsonExport = JsonCompValueExport()
            as_dict = jsonExport.getDictForStep(step, self)

            if debug:
                print(as_dict)

            fullPathName = os.path.join(path, filename) + "_" + step + ".json"
            with open(fullPathName, "w", encoding="utf-8") as f:
                json.dump(as_dict, f, ensure_ascii=False, indent=4)
        else:
            fullPathName = ""

        if cvStep:
            jsonExport = JsonVCValueExport(voltSym=self.langSymbols.volt)
            as_dict = jsonExport.getDictForStep(step, self)

            if debug:
                print(as_dict)

            fullPathNameCV = os.path.join(path, filename) + "_" + step + "_VC" + ".json"
            with open(fullPathNameCV, "w", encoding="utf-8") as f:
                json.dump(as_dict, f, ensure_ascii=False, indent=4)
        else:
            fullPathNameCV = ""

        return fullPathName, fullPathNameCV

    def export(self, path: str = None, filename: str = "circuit", debug: bool = False,
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
            self.exportStepAsJson(step, path=path, filename=filename, debug=debug)
