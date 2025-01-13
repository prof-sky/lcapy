import os
import shutil

import NonLcapyFiles.solve as solve
import json
from lcapy import Circuit, FileToImpedance
from lcapy.solution import Solution


class TestJsonExport:

    @staticmethod
    def removeDir(folderName: str = "tempTest"):
        if os.path.isdir(folderName):
            shutil.rmtree(folderName)

    @staticmethod
    def makeTestDir(folderName: str = "tempTest"):
        if not os.path.isdir(".\\tempTest"):
            os.mkdir(folderName)

    @staticmethod
    def readJson(filePath):
        with open(filePath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    def helperJsonExportCircuitInfo(self, fileName: str, values: list[str], compType: str):
        sol = solve.SolveInUserOrder(fileName, filePath="Schematics", savePath="/tempTest")
        filePath = sol.createCircuitInfo()
        data = self.readJson(filePath)
        for key in values:
            assert key in data.keys()

        assert data["componentTypes"] == compType

    def test_JasonExportCircuitInfo(self):
        self.makeTestDir()

        self.helperJsonExportCircuitInfo("R_parallel_dc",
                                         ["R1", "R2", "V1", "componentTypes", "omega_0"],
                                         "R")

        self.helperJsonExportCircuitInfo("R_parallel_ac",
                                         ["R1", "R2", "V1", "componentTypes", "omega_0"],
                                         "R")

        self.helperJsonExportCircuitInfo("L_parallel_ac",
                                         ["L1", "L2", "V1", "componentTypes", "omega_0"],
                                         "L")

        self.helperJsonExportCircuitInfo("C_parallel_ac",
                                         ["C1", "C2", "V1", "componentTypes", "omega_0"],
                                         "C")

        self.helperJsonExportCircuitInfo("Circuit_resistors_I",
                                         ["R1", "R2", "R3", "R4", "R5", "I1"],
                                         "R")

        self.helperJsonExportCircuitInfo("RC_series_ac",
                                         ["R1", "C2", "V1", "componentTypes", "omega_0"],
                                         "RLC")
        self.removeDir()

    def helperJsonExport(self, fileName: str, filePath: str, savePath: str):
        cct = Circuit(FileToImpedance(os.path.join(filePath, fileName)))
        cct.namer.reset()
        steps = cct.simplify_stepwise()
        sol = Solution(steps)
        for step in sol.available_steps:
            jsonFileName = sol.exportStepAsJson(step, path=savePath, filename=fileName)
            data = self.readJson(jsonFileName)
            for key in ["step", "canBeSimplified", "simplifiedTo", "componentsRelation",
                        "components", "svgData"]:
                assert key in data.keys(), f"filename: {jsonFileName} dataKey {key} is missing"

    def test_JsonExport(self):
        self.makeTestDir()
        for filename in os.listdir(".\\Schematics"):
            self.helperJsonExport(filename, ".\\Schematics", ".\\tempTest")
        self.removeDir()
