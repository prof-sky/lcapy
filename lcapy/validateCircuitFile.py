from lcapy.parser import Parser
from os.path import join
from lcapy.netlistLine import NetlistLine
from typing import Self
from enum import Enum


class ValueType(Enum):
    any = "any"
    string = "string"
    float = "float"


class ValidateCircuitFile:
    def __init__(self, fileName: list[str], filePath: str = "", valueType: ValueType = ValueType.any):
        self.files: list[str] = []
        self.valueType: ValueType = valueType

        self.validSyntax = True
        self.validSemantic = True

        for name in fileName:
            self.files.append(join(filePath, name))

    def validateSyntax(self) -> Self:
        for file in self.files:
            f = open(file, "r").read()
            for idx, line in enumerate(f.splitlines()):
                try:
                    NetlistLine(line)
                except:
                    print(f"Syntax error on line {idx+1} in {file}: {line}")
                    self.validSyntax = False

        return self

    def validateSematic(self) -> Self:
        if self.validSyntax:
            self._checkNodeCount()
            self._checkValues()

        else:
            self.validSemantic = False

        return self

    def _checkValues(self):
        for file in self.files:
            f = open(file, "r").read()
            for idx, line in enumerate(f.splitlines()):
                netLine = NetlistLine(line)
                if not netLine.type == "W" and not self.valueType == ValueType.any:
                    try:
                        if self.valueType == ValueType.string:
                            str(netLine.value)
                        if self.valueType == ValueType.float:
                            float(netLine.value)
                    except:
                        print(f"Wrong Type of value on line: {idx+1} "
                              f"file: {file} value: {netLine.value} "
                              f"expected: {self.valueType}")

    def _checkNodeCount(self):
        for file in self.files:
            f = open(file, "r").read()
            nodeCount = {}
            for line in f.splitlines():
                netLine = NetlistLine(line)
                nodeCount[netLine.startNode] = nodeCount.get(netLine.startNode, 0) + 1
                nodeCount[netLine.endNode] = nodeCount.get(netLine.endNode, 0) + 1

            for key in nodeCount.keys():
                if nodeCount[key] < 2:
                    print(f"Semantic error, node {key} only appears once")
                    self.validSemantic = False
    def isValid(self):
        self.validateSyntax()
        self.validateSematic()
        return self.validSemantic and self.validSyntax
