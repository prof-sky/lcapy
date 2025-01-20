from sympy.printing import print_latex
from sympy.printing import latex
from sympy import Float
from typing import Union
from sympy import Mul
from lcapy import Expr
from lcapy.unitPrefixer import SIUnitPrefixer
from lcapy.componentRelation import ComponentRelation
import os
from json import dump as jdump
from lcapy.langSymbols import LangSymbols


class ExportDict(dict):
    save_path = None
    file_name = None

    @classmethod
    def set_paths(cls, savePath, fileName):
        cls.save_path = savePath
        cls.file_name = fileName

    def _errorHandling(self):
        if not self["step"] or not self["svgData"]:
            raise RuntimeError(f"To file only works when svgData and a step name is available:"
                               f" stepVal: {self['step']}"
                               f" svgData: {self['svgData']}")

    def toFiles(self, savePath=None, fileName=None):

        return True, self.toJSON(), self.toSVG()

    def toSVG(self, savePath=None, fileName=None) -> str:
        savePath = savePath if savePath else self.save_path
        fileName = fileName if fileName else self.file_name
        self._errorHandling()

        step = self["step"]
        svgFilePath = os.path.join(savePath, fileName) + "_" + step + ".svg"
        svgFile = open(svgFilePath, "w", encoding="utf8")
        svgFile.write(self["svgData"])
        svgFile.close()

        return svgFilePath

    def toJSON(self, savePath=None, fileName=None) -> str:
        savePath = savePath if savePath else self.save_path
        fileName = fileName if fileName else self.file_name

        step = self["step"]
        jsonFilePath = os.path.join(savePath, fileName) + "_" + step + ".json"
        with open(jsonFilePath, "w", encoding="utf-8") as f:
            jdump(self, f, ensure_ascii=False, indent=4)

        return jsonFilePath


class DictExportBase:
    def __init__(self, precision: int, langSymbol: LangSymbols):
        self.precision = precision
        self.prefixer = SIUnitPrefixer()
        self.ls = langSymbol

    def _latexRealNumber(self, value: Union[Mul, Expr], prec=None, addPrefix: bool = True) -> str:
        if prec is None:
            prec = self.precision

        if addPrefix:
            toPrint = 1.0 * self.prefixer.getSIPrefixedMul(value)
        else:
            if isinstance(value, Expr):
                toPrint = 1.0 * value.expr_with_units
            else:
                toPrint = 1.0 * value

        for val in list(toPrint.atoms(Float)):
            toPrint = toPrint.evalf(subs={val: str(round(val, prec))})
        latexString = latex(toPrint, imaginary_unit="j")
        return latexString

    @staticmethod
    def _latexComplexNumber(value: Union[Mul, Expr]):

        test = latex(value.evalf(n=3, chop=True))
        return test

    def latexWithPrefix(self, value: Union[Mul, Expr], prec=None, addPrefix: bool = True) -> str:
        if value.is_Add:
            return self._latexComplexNumber(value)
        else:
            return self._latexRealNumber(value, prec, addPrefix)

    def latexWithoutPrefix(self, value: Expr, prec=None) -> str:
        if value.is_Add:
            return self._latexComplexNumber(value)
        else:
            return self._latexRealNumber(value, prec, addPrefix=False)

    def _getValueFieldKeys(self, *args: str) -> list[str]:
        """
        finds fields that include the strings of args in their name to automatically convert them to a latex string
        on export. All fields are converted to lowercase so this functino is not case-sensitive.
        :return: list of keys<str> that have the name of the fields that match the criteria
        """

        keys = list(self.__dict__.keys())
        valueFiledKeys = []
        for key in keys:
            lcKey = key.lower()
            if any(arg.lower() in lcKey for arg in args):
                valueFiledKeys.append(key)

        return valueFiledKeys

    def getDictForStep(self, step, solution: 'lcapy.Solution'):
        raise NotImplementedError("Implement in Child class")

    @property
    def emptyExportDict(self) -> ExportDict:
        return ExportDict({
                "step": None,
                "canBeSimplified": False,
                "simplifiedTo": {
                    "Z": {"name": None, "complexVal": None, "val": None},
                    "U": {"name": None, "val": None},
                    "I": {"name": None, "val": None},
                    "hasConversion": None,
                },
                "componentsRelation": ComponentRelation.none.to_string(),
                "components": [],
                "allComponents": [],
                "svgData": None
            })

    @staticmethod
    def exportDict(step: str, canBeSimplified: bool, simplifiedTo: dict,
                   componentsRelation: ComponentRelation, svgData: str,
                   cpts: list[ExportDict], allCpts: list[ExportDict]) -> ExportDict:
        """
        :param step: step of simplification step1 step2 step3...
        :param canBeSimplified: True, False if the selected cpts can be simplified
        :param simplifiedTo: components which results from simplifying cpts a,b,c...
        :param componentsRelation: if the cpts where in series or in parallel
        :param svgData: svg data string of the circuit
        :param cpts: the components which where simplified to simplifiedTo
        :param allCpts: all cpts in the circuit (excepts sources)
        :return: Dictionary with the information
        cpts and allCpts dicts are self.exportDictCpt
        """
        return ExportDict({
            "step": step,
            "canBeSimplified": canBeSimplified,  # bool
            "simplifiedTo": simplifiedTo,
            "componentsRelation": componentsRelation.to_string(),
            "components": cpts,
            "allComponents": allCpts,
            "svgData": svgData
        })

    @staticmethod
    def exportDictCpt(rName: str, uName: str, iName: str, zComplexVal, zVal, uVal, iVal,
                      hasConversion: bool) -> ExportDict:
        return ExportDict({
            "Z": {"name": rName, "complexVal": zComplexVal, "val": zVal},
            "U": {"name": uName, "val": uVal},
            "I": {"name": iName, "val": iVal},
            "hasConversion": hasConversion
        })

    def step0ExportDictSource(self, sourceType: str, omega_0, val):
        return ExportDict({
            "Type": sourceType,  # V,I
            "omega_0": self.latexWithPrefix(omega_0),
            "val": self.latexWithPrefix(val)
        })

    @staticmethod
    def step0ExportDict(step, sources: list[ExportDict], cpts: list[ExportDict], circuitType: str, svgData: str):
        return ExportDict({
            "step": step,
            "source": sources,
            "components": cpts,
            "componentTypes": circuitType,
            "svgData": svgData
        })
    # compTypes.add(compType)

    # if len(compTypes) == 1:
    #    if "R" in compTypes:
    #        as_dict["componentTypes"] = "R"
    #    elif "L" in compTypes:
    #        as_dict["componentTypes"] = "L"
    #    elif "C" in compTypes:
    #        as_dict["componentTypes"] = "C"
    #    else:
    #        raise ValueError("Unexpected type in set types")
    #else:
    #    as_dict["componentTypes"] = "RLC"

