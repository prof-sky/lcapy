import os
import shutil

import NonLcapyFiles.solve as solve
import json
from lcapy import Circuit, FileToImpedance
from lcapy.solution import Solution
from lcapy.langSymbols import LangSymbols


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

    def helperJsonExportCircuitInfo(self, fileName: str):
        sol = solve.SolveInUserOrder(fileName, filePath="Schematics", savePath="/tempTest")
        data = sol.createInitialStep()
        for key in ["step", "source", "allComponents", "componentTypes", "svgData"]:
            assert key in data.keys(), f"filename: {fileName} dataKey {key} is missing"

        sol.createInitialStep()

    def test_JasonExportCircuitInfo(self):
        self.makeTestDir()

        self.helperJsonExportCircuitInfo("R_parallel_dc")

        self.helperJsonExportCircuitInfo("R_parallel_ac")

        self.helperJsonExportCircuitInfo("L_parallel_ac")

        self.helperJsonExportCircuitInfo("C_parallel_ac")

        self.helperJsonExportCircuitInfo("Circuit_resistors_I")

        self.helperJsonExportCircuitInfo("RC_series_ac")
        self.removeDir()

    def helperJsonExport(self, fileName: str, filePath: str, savePath: str):
        cct = Circuit(FileToImpedance(os.path.join(filePath, fileName)))
        cct.namer.reset()
        steps = cct.simplify_stepwise()
        sol = Solution(steps, LangSymbols())

        for step in sol.available_steps[1::]:
            jsonFileName = sol.exportStepAsJson(step, path=savePath, filename=fileName)
            data = self.readJson(jsonFileName)
            for key in ["step", "canBeSimplified", "simplifiedTo", "componentsRelation",
                        "components", "svgData"]:
                assert key in data.keys(), f"filename: {jsonFileName} dataKey {key} is missing"

    def test_JsonExport(self):
        self.makeTestDir()
        self.helperJsonExport("C_parallel_ac", ".\\Schematics", ".\\tempTest")
        self.helperJsonExport("R_parallel_ac", ".\\Schematics", ".\\tempTest")
        self.helperJsonExport("L_parallel_ac", ".\\Schematics", ".\\tempTest")
        self.helperJsonExport("CL_parallel_ac", ".\\Schematics", ".\\tempTest")
        self.helperJsonExport("RL_parallel_ac", ".\\Schematics", ".\\tempTest")
        self.helperJsonExport("C_series_ac", ".\\Schematics", ".\\tempTest")
        self.helperJsonExport("R_series_ac", ".\\Schematics", ".\\tempTest")
        self.helperJsonExport("L_series_ac", ".\\Schematics", ".\\tempTest")
        self.helperJsonExport("CL_series_ac", ".\\Schematics", ".\\tempTest")
        self.helperJsonExport("RL_series_ac", ".\\Schematics", ".\\tempTest")
        self.removeDir()
