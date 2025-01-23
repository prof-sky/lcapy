import os

import solve
import time
from datetime import datetime
from lcapy.validateCircuitFile import ValidateCircuitFile
from lcapy.dictExportBase import ExportDict


filenames = ["Inductors.txt",  # 0
             "Resistors.txt",  # 1
             "Capacitors.txt",  # 2
             "Mixed_2pi30.txt",  # 3
             "Mixed_omega0.txt",  # 4
             "Mixed_30.txt",  # 5
             "Mixed.txt",  # 6
             "Resistor_task1.txt",  # 7
             "Resistor_task2.txt",  # 8
             "Resistors_I",  # 9
             "Resistors_I_ac",  # 10
             "VlCircuit.txt",  # 11
             "Resistor_Hetznecker.txt",  # 12
             "C_parallel_dc",  # 13
             "Parallel3.txt",  # 14
             "Mixed_RC_series.txt",  # 15
             "Resistors_row3.txt"  # 16
             ]
#  clear Solutions directory
clearPath = "./Solutions"
files = os.listdir(clearPath)
for file in files:
    os.remove(os.path.join(clearPath, file))

filename = filenames[2]

if not ValidateCircuitFile(["StandardCircuits/"+filename]).isValid():
    exit("File not valid")

st = time.time()
# solve.solve_circuit(filename, filePath="StandardCircuits")
a = solve.SolveInUserOrder(filename, filePath="StandardCircuits", savePath="Solutions", langSymbols={"volt": "U", "total": "ges"})
ExportDict.set_paths(a.savePath, a.filename)

a.createInitialStep().toFiles()
a.simplifyNCpts(["Z1", "Z2", "Z3"]).toFiles()
# a.simplifyNCpts(["Zs1", "Z3"]).toFiles()
# a.simplifyNCpts(["Zs2", "Z1"]).toFiles()
et = time.time()

print(f"Execution time was: {et-st:.2f} s, DateTime: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
