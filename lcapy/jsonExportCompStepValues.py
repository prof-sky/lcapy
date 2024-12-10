
class JsonExportStepValues:
    def __init__(self, name1, name2, newName,
                 relation,
                 value1, value2, result,
                 latexEquation,
                 convVal1, convVal2, convResult):

        self.name1: str = name1
        self.name2: str = name2
        self.newName: str = newName
        self.relation: str = relation
        self.value1 = value1
        self.value2 = value2
        self.result = result
        self.latexEquation: str = latexEquation

        if convVal1:
            self.convVal1 = convVal1
        else:
            self.convVal1 = None
        if convVal2:
            self.convVal2 = convVal2
        else:
            self.convVal2 = None
        if convResult:
            self.convResult = convResult
        else:
            self.convResult = None

        self.hasConversion: bool = bool(bool(convVal1) or bool(convVal2) or bool(convResult))

    def toDict(self) -> dict:
        return {
            "cptNames": [self.name1, self.name2],
            "newCptName": self.newName,
            "relation": self.relation,
            "cptValues": [self.value1, self.value2],
            "newCptVal": self.result,
            "hasConversion": self.hasConversion,
            "convCptVals": [self.convVal1, self.convVal2],
            "convNewCptVal": self.convResult
        }

