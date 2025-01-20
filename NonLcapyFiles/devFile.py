import os

import solve
import time
from datetime import datetime
from lcapy.validateCircuitFile import ValidateCircuitFile
from lcapy.dictExportBase import ExportDict


filenames = ["Circuit_inductors.txt",  # 0
             "Circuit_resistors.txt",  # 1
             "Circuit_capacitors.txt",  # 2
             "Circuit_mixed_2pi30.txt",  # 3
             "Circuit_mixed_omega0.txt",  # 4
             "Circuit_mixed_30.txt",  # 5
             "Circuit_mixed.txt",  # 6
             "Circuit_resistor_task1.txt",  # 7
             "Circuit_resistor_task2.txt",  # 8
             "Circuit_resistors_I",  # 9
             "Circuit_resistors_I_ac",  # 10
             "00_vlCircuit.txt",  # 11
             "Resistor_Hetznecker.txt",  # 12
             "C_parallel_dc",  # 13
             "03_resistor_parallel3.txt",  # 14
             "00_mixed_RC_series.txt"  # 15
             ]
#  clear Solutions directory
clearPath = "./Solutions"
files = os.listdir(clearPath)
for file in files:
    os.remove(os.path.join(clearPath, file))

filename = filenames[15]

if not ValidateCircuitFile(["StandardCircuits/"+filename]).isValid():
    exit("File not valid")

st = time.time()
# solve.solve_circuit(filename, filePath="StandardCircuits")
a = solve.SolveInUserOrder(filename, filePath="StandardCircuits", savePath="Solutions", langSymbols={"volt": "V", "total": "tot"})
ExportDict.set_paths(a.savePath, a.filename)

a.createInitialStep().toFiles()
a.simplifyNCpts(["Z1", "Z2"]).toFiles()
# a.simplifyNCpts(["Z3", "Zs1"]).toFiles()
# a.simplifyNCpts(["Zs2", "Z1"]).toFiles()
et = time.time()

print(f"Execution time was: {et-st:.2f} s, DateTime: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
