import os
from warnings import warn
import pytest

generateSVGFilesPath = "generateSVGFiles.py"
circuitsFolderPath = "Circuits"


def sortFilesInLists(files, path, list1, cond1, list2, cond2, skipCond):
    for file in files:
        filePath = os.path.join(path, file)
        if cond1(file):
            list1.append(filePath.replace(".txt", ""))
        elif cond2(file):
            list2.append(filePath.replace(".svg", ""))
        elif skipCond(file):
            continue
        else:
            warn("File that nighter satisfies cond1 or cond2 in files")

def getFilesRecursive():
    fileList = []
    return fileList


class TestSVGGeneration:
    @staticmethod
    def updateSvgAndTxtList(svgFiles, txtFiles):
        for path, _, files in os.walk(circuitsFolderPath):
            sortFilesInLists(files, path,
                             svgFiles, lambda x: x.endswith(".svg"),
                             txtFiles, lambda x: x.endswith(".txt"),
                             lambda x: x.endswith(".stepSol")
                                  )

    def test_svgFileGeneration(self):
        # change into the NonLcapyFiles folder
        os.chdir("..\\")

        svgFiles = []
        txtFiles = []
        self.updateSvgAndTxtList(svgFiles, txtFiles)

        # check if there are svg-files that have no txt file -> indicates that might be deleted a circuit file by accident
        missingTxtFiles = self.MissingTxtFiles(svgFiles, txtFiles)
        if missingTxtFiles:
            raise AssertionError(
                f"Missing txt Files: {[missingFile + '.txt' for missingFile in missingTxtFiles]}")

        for file in svgFiles:
            os.remove(file)

        # assert that all svg files are deleted and later regenerated
        self.updateSvgAndTxtList(svgFiles, txtFiles)
        assert len(svgFiles) == 0, "Removing svg files failed, check test"

        # generate the svg-files with the script that runs in the ci/cd
        exec(open(generateSVGFilesPath).read())

        # check if all svg-files got regenerated
        self.updateSvgAndTxtList(svgFiles, txtFiles)
        missingSvgFiles = self.MissingSvgFiles(svgFiles, txtFiles)
        if missingSvgFiles:
            raise AssertionError(
                f"Missing svg Files: {[missingFile + '_step0.svg' for missingFile in missingSvgFiles]}")

    @staticmethod
    def setDiff(set1, set2) -> list:
        return list(set1-set2)

    def MissingTxtFiles(self, svgFiles, txtFiles) -> list:
        svgSet = set(svgFile.replace("_step0.svg", "") for svgFile in svgFiles)
        txtSet = set(txtFile.replace(".txt", "") for txtFile in txtFiles)
        return self.setDiff(svgSet, txtSet)

    def MissingSvgFiles(self, svgFiles, txtFiles) -> list:
        svgSet = set(svgFile.replace("_step0.svg", "") for svgFile in svgFiles)
        txtSet = set(txtFile.replace(".txt", "") for txtFile in txtFiles)
        return self.setDiff(txtSet, svgSet)







