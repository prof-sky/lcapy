import os

import solve
import time
from datetime import datetime
from lcapy.validateCircuitFile import ValidateCircuitFile
from lcapy.dictExportBase import ExportDict
import cProfile

def work():
    a.createInitialStep().toFiles()
    a.simplifyNCpts(["Z2", "Z3"]).toFiles()

#  clear Solutions directory
clearPath = "./Solutions"
files = os.listdir(clearPath)
for file in files:
    os.remove(os.path.join(clearPath, file))

fixFile = True
if fixFile:
    filePath = "Circuits/mixed"
    filename = "01_mixed_RCL_parallel.txt"
else:
    from tkinter import filedialog
    curPath = os.getcwd()
    absFilePath = filedialog.askopenfilename(initialdir=os.path.join(curPath, "Circuits"),
                                             filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")])
    filePath = os.path.dirname(absFilePath)
    filename = os.path.basename(absFilePath)

if not ValidateCircuitFile([os.path.join(filePath, filename)]).isValid():
    exit("File not valid")

st = time.time()
# solve.solve_circuit(filename, filePath="StandardCircuits")
a = solve.SolveInUserOrder(filename, filePath=filePath, savePath="Solutions", langSymbols={"volt": "V", "total": "tot"})
ExportDict.set_paths(a.savePath, a.filename)
cProfile.run("work()",sort="tottime")
et = time.time()

print(f"Execution time was: {et-st:.2f} s, DateTime: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
