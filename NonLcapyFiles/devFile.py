import os

import solve
import time
from datetime import datetime
from lcapy.validateCircuitFile import ValidateCircuitFile
from lcapy.langSymbols import LangSymbols

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
             "00_vlCircuit.txt"  # 11
             ]
#  clear Solutions directory
clearPath = "./Solutions"
files = os.listdir(clearPath)
for file in files:
    os.remove(os.path.join(clearPath, file))

filename = filenames[11]

if not ValidateCircuitFile(["StandardCircuits/"+filename]).isValid():
    exit("File not valid")

st = time.time()
solve.solve_circuit(filename, filePath="StandardCircuits")
# a = solve.SolveInUserOrder(filenames[1], filePath="StandardCircuits", langSymbols=langSymbols, savePath="Solutions")
# a.createInitialStep()
# a.simplifyTwoCpts(["R2", "R1"])
# a.simplifyTwoCpts(["R3", "Rs1"])
et = time.time()

print(f"Execution time was: {et-st:.2f} s, DateTime: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
