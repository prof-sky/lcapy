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
    def __init__(self, precision: int, voltSym='U'):
        self.precision = precision
        self.prefixer = SIUnitPrefixer()
        self.voltSym = voltSym

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
                "components": [{
                    "Z": {"name": None, "complexVal": None, "val": None},
                    "U": {"name": None, "val": None},
                    "I": {"name": None, "val": None},
                    "hasConversion": None,
                }],
                "svgData": None
            })

    @staticmethod
    def exportDict(step: str, canBeSimplified: bool, simplifiedTo: dict, componentsRelation: ComponentRelation,
                   svgData: str, cpts: list[dict]) -> ExportDict:

        return ExportDict({
            "step": step,
            "canBeSimplified": canBeSimplified,  # bool
            "simplifiedTo": simplifiedTo,
            "componentsRelation": componentsRelation.to_string(),
            "components": cpts,
            "svgData": svgData
        })

    @staticmethod
    def exportDictCpt(rName: str, uName: str, iName: str, zComplexVal, zVal, uVal, iVal, hasConversion: bool) -> ExportDict:
        return ExportDict({
            "Z": {"name": rName, "complexVal": zComplexVal, "val": zVal},
            "U": {"name": uName, "val": uVal},
            "I": {"name": iName, "val": iVal},
            "hasConversion": hasConversion
        })

