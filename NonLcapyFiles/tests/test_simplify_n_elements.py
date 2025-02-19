from NonLcapyFiles import solve
import os


class TestSimplifyNElements:
    @staticmethod
    def clearDir(path):
        if os.path.exists(path) and os.path.isdir(path):
            toRemove = os.listdir(path)
            for remove in toRemove:
                os.remove(os.path.join(path, remove))

    def test_three_in_row(self):
        savePath = "../Solutions"
        self.clearDir(savePath)
        solObj = solve.SolveInUserOrder("07_resistor_row3.txt", filePath="../Circuits/resistor", savePath=savePath)
        solObj.simplifyNCpts(["R1", "R2", "R3"])
        val1 = solObj.steps[0].circuit.Z1.Z
        val2 = solObj.steps[0].circuit.Z2.Z
        val3 = solObj.steps[0].circuit.Z3.Z
        result = solObj.steps[1].circuit.Zs1.Z
        assert val1 + val2 + val3 == result

    def test_three_parallel(self):
        savePath = "../Solutions"
        self.clearDir(savePath)
        solObj = solve.SolveInUserOrder("08_resistor_parallel3.txt", filePath="../Circuits/resistor", savePath=savePath)
        solObj.simplifyNCpts(["R1", "R2", "R3"])
        val1 = solObj.steps[0].circuit.Z1.Z
        val2 = solObj.steps[0].circuit.Z2.Z
        val3 = solObj.steps[0].circuit.Z3.Z
        result = solObj.steps[1].circuit.Zs1.Z
        assert 1/(1/val1 + 1/val2 + 1/val3) == result
