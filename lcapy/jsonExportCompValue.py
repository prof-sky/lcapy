import lcapy
from lcapy import state
from lcapy.impedanceConverter import ValueToComponent
from lcapy.impedanceConverter import getSourcesFromCircuit, getOmegaFromCircuit
from lcapy.jsonExportCompStepValues import JsonExportStepValues
from lcapy.unitWorkAround import UnitWorkAround as uwa
from lcapy.jsonExportBase import JsonExportBase


class JsonCompValueExport(JsonExportBase):
    """
    Jason Component Value Export
    Creates a json-File with information about the component values
    (resistance for resistor, inductance for inductor ...) and the simplification steps. That means which components got
    combined. The format is handy to display the simplification on the Web-UI.
    Takes a step <string> that is part of a Solution <lcapy.Solution> Object. The available steps can be accessed by
    <lcapy.Solution>.available_steps
    """
    def __init__(self, precision=3):
        self.names: list[str] = []
        self.newName = None
        self.thisStep = None
        self.lastStep = None
        self.step = None
        self.cpts: list = []  # components
        self.cptRes = None  # componentResult
        self.values: list = []  # valuesComponent
        self.result = None  # valueComponentResult
        self.convVals: list = []  # convertedValueComponent1 -> converted from Impedance to R,L or C if possible
        self.convResult = None  # convertedValueComponentResult -> converted from Impedance to R,L or C if possible
        self.cvcTypes: list = []  # convertedValueComponent1Type
        self.cvcrType = None  # convertedValueComponentResultType
        self.omega_0 = None

        super().__init__(precision)

        self.valueFieldKeys = self._getValueFieldKeys("val", "result")

    def _updateObjectValues(self, step, solution: 'lcapy.Solution'):
        # the values for name1 and name2 are not final if they are transformable they are adjusted later on
        # e.g. from Z1 to R1, L1, or C1
        for name in solution[step].cpts:
            self.names.append(name)

        self.newName = solution[step].newCptName
        self.thisStep = solution[step]
        self.lastStep = solution[step].lastStep
        self.omega_0 = getOmegaFromCircuit(solution[step].circuit, getSourcesFromCircuit(solution[step].circuit))

        if not self._isInitialStep():
            for name in self.names:
                self.cpts.append(self.lastStep.circuit[name])
            self.cptRes = self.thisStep.circuit[self.newName]

            for value in self.cpts:
                self.values.append(value.Z)
            self.result = self.cptRes.Z

            #  try to convert the value to an R, L, C component
            for value in self.values:
                convVal, cvcType = ValueToComponent(value.expr, omega_0=self.omega_0)
                self.convVals.append(uwa.addUnit(convVal, cvcType))
                self.cvcTypes.append(cvcType)

            self.convResult, self.cvcrType = ValueToComponent(self.result.expr, omega_0=self.omega_0)
            self.convResult = uwa.addUnit(self.convResult, self.cvcrType)

            #  create new names for the components e.g. Z1 to R1
            for idx in range(0, len(self.names)):
                self.names[idx] = self.cvcTypes[idx] + self.cpts[idx].id

            self.newName = self.cvcrType + self.cptRes.id

    def getDictForStep(self, step, solution: 'lcapy.Solution'):
        self._updateObjectValues(step, solution)

        if self._isInitialStep():
            return JsonExportStepValues(None, None, None, None,
                                        None, None, None, None,
                                        None, None, None).toDict()

        elif self._checkEssentialInformation():
            raise ValueError(f"missing information in {step}: "
                             f"{self.names}, {self.newName}, {self.thisStep}, {self.lastStep}")

        else:
            state.show_units = True

            if self._allValuesConvertableToComponent():
                if self._isSameType():
                    values = self._handleSameTypeAndConvertibleToComponent()
                else:
                    values = self._handleDifferentTypeAndConvertibleToComponent()

            elif self._resultConvertibleToComponent():
                values = self._handleResultConvertibleToComponent()

            else:
                values = self._handleNoConversionPossible()

            for key in ['newCptVal', 'convNewCptVal']:
                if values[key]:
                    values[key] = self.latexWithPrefix(values[key])

            for idx, val in enumerate(values['cptValues']):
                if val:
                    values['cptValues'][idx] = self.latexWithPrefix(val)

            for idx, val in enumerate(values['convCptVals']):
                if val:
                    values['convCptVals'][idx] = self.latexWithPrefix(val)

            return values

    def _isInitialStep(self) -> bool:
        return not (self.names and self.newName and self.lastStep) and self.thisStep

    def _checkEssentialInformation(self) -> bool:
        """
        this function makes sure that all information that is needed to compute a solution step is available,
        exception is the initial step that does acquire the information it needs.
        :returns: true if information is available, false otherwise
        """
        return not (self.names or self.newName or self.lastStep or self.thisStep or self.step)

    def _allValuesConvertableToComponent(self) -> bool:
        return all(types != 'Z' for types in self.cvcTypes + [self.cvcrType])

    def _isSameType(self) -> bool:
        return all(types == self.cvcTypes[0] for types in self.cvcTypes)

    def _handleSameTypeAndConvertibleToComponent(self) -> dict:
        # replace with for loop
        val1 = self.convVals[0]
        val2 = self.convVals[1]
        res = self.convResult
        assert self.cvcTypes[0] in ["R", "L", "C"]

        return JsonExportStepValues(self.names[0], self.names[1], self.newName, self.thisStep.relation,
                                    val1, val2, res, "NoLatexEquation",
                                    convVal1=None, convVal2=None, convResult=None).toDict()

    def _handleDifferentTypeAndConvertibleToComponent(self) -> dict:
        # replace with for loop
        val1 = self.values[0].expr_with_units
        val2 = self.values[1].expr_with_units
        res = self.result.expr_with_units

        assert self.cptRes.type == "Z"
        convValCptRes = self.convResult.expr_with_units

        return JsonExportStepValues(self.names[0], self.names[1], self.newName, self.thisStep.relation,
                                    val1, val2, res, "NoLatexEquation",
                                    convVal1=None, convVal2=None, convResult=convValCptRes).toDict()

    def _resultConvertibleToComponent(self) -> bool:
        return (all(x == 'Z' for x in self.cvcTypes)
                and not self.cvcrType == "Z")

    def _handleResultConvertibleToComponent(self) -> dict:
        # replace with for loop
        val1 = self.values[0].expr_with_units
        val2 = self.values[1].expr_with_units
        res = self.result.expr_with_units

        assert self.cpts[0].type == "Z"
        convValCptRes = self.convResult

        return JsonExportStepValues(self.names[0], self.names[1], self.newName, self.thisStep.relation,
                                    val1, val2, res, "NoLatexEquation",
                                    convVal1=None, convVal2=None, convResult=convValCptRes).toDict()

    def _handleNoConversionPossible(self) -> dict:
        # replace with for loop
        val1 = self.values[0].expr_with_units
        val2 = self.values[1].expr_with_units
        res = self.result.expr_with_units

        assert self.cpts[0].type == "Z"

        return JsonExportStepValues(self.names[0], self.names[1], self.newName, self.thisStep.relation,
                                    val1, val2, res, "NoLatexEquation",
                                    convVal1=None, convVal2=None, convResult=None).toDict()
