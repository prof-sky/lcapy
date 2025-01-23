from NonLcapyFiles.solve import solve_circuit, SolveInUserOrder
import os
from lcapy.dictExport import ExportDict
import random

# string is filename, integer is number of steps that shall be created
# the initial step has to be included
filenames = [("Inductors.txt", 5),
             ("Resistors.txt", 5),
             ("Capacitors.txt", 5),
             ("Mixed_2pi30.txt", 5),
             ("Mixed_omega0.txt", 5),
             ("Mixed_30.txt", 5),
             ("Mixed.txt", 5),
             ("Resistors_I", 5),
             ("Resistors_I_ac", 5)]


def clearDir(path):
    if os.path.exists(path) and os.path.isdir(path):
        toRemove = os.listdir(path)
        for remove in toRemove:
            os.remove(os.path.join(path, remove))


def check_for_solutions(solSteps: int, filename: str, path: str = "../Solutions", filesPerStep: int = 2):
    # each step produces 2 json files and 1 svg file
    assert len(os.listdir(path)) == solSteps*filesPerStep, f"{filename} didn't produce as many files as expected"


def solveInUserOrder(filename):
    clearDir("../Solutions")

    test = SolveInUserOrder(filename=filename, filePath="../StandardCircuits/")
    ExportDict.set_paths(savePath="../Solutions/", fileName=filename)

    test.createInitialStep().toFiles()
    test.simplifyNCpts(["Z4", "Z5"]).toFiles()
    test.simplifyNCpts(["Z1", "Zs1"]).toFiles()
    test.simplifyNCpts(["Z2", "Z3"]).toFiles()
    test.simplifyNCpts(["Zs2", "Zs3"]).toFiles()


def test_solve_circuits():
    for filename in filenames:
        clearDir("../Solutions")
        solve_circuit(filename[0], filePath="../StandardCircuits/", savePath="../Solutions")
        check_for_solutions(filename=filename[0], solSteps=filename[1])
        print(f"{filename[0]+'...':40s}success")


def test_SolveInUserOrder():
    for filename in filenames:
        clearDir("../Solutions")
        solveInUserOrder(filename[0])
        check_for_solutions(filename=filename[0], solSteps=filename[1])
        print(f"{filename[0]+'...':40s}success")