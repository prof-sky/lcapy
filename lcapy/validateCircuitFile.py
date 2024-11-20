from lcapy.parser import Parser
from os.path import join
from lcapy.netlistLine import NetlistLine


class ValidateCircuitFile:
    def __init__(self, fileName: list[str], filePath: str):
        self.files: list[str] = []

        self.listHasError = True
        self.validSyntax = True
        self.validSemantic = True

        for name in fileName:
            self.files.append(join(filePath, name))

    def validateSyntax(self):
        for file in self.files:
            f = open(file, "r").read()
            for idx, line in enumerate(f.splitlines()):
                try:
                    NetlistLine(line)
                except:
                    print(f"Syntax error on line {idx+1} in {file}: {line}")
                    self.validSyntax = False

    def validateSematic(self):
        if self.validSyntax:
            for file in self.files:
                f = open(file, "r").read()
                nodeCount = {}
                for line in f.splitlines():
                    netLine = NetlistLine(line)
                    nodeCount[netLine.startNode] = nodeCount.get(netLine.startNode, 0) + 1
                    nodeCount[netLine.endNode] = nodeCount.get(netLine.endNode, 0) + 1

                for key in nodeCount.keys():
                    if nodeCount[key] < 2:
                        print(f"Semantic error node {key} only appears once")
                        self.validSemantic = False

        else:
            self.validSemantic = False


