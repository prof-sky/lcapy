import os

import solve
import time
from datetime import datetime

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
             "Circuit_resistors_I_ac"  # 10
             ]
#  clear Solutions directory
clearPath = "./Solutions"
files = os.listdir(clearPath)
for file in files:
    os.remove(os.path.join(clearPath, file))

st = time.time()
# solve.solve_circuit(filenames[8], filePath="StandardCircuits")
a = solve.SolveInUserOrder(filenames[1], filePath="StandardCircuits", voltSym="V", savePath="Solutions")
a.createInitialStep()
a.simplifyTwoCpts(["R1", "R2"])
et = time.time()

print(f"Execution time was: {et-st:.2f} s, DateTime: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
