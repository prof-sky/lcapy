import solve
import time

filenames = ["Circuit_inductors.txt",  # 0
             "Circuit_resistors.txt",  # 1
             "Circuit_capacitors.txt",  # 2
             "Circuit_mixed_2pi30.txt",  # 3
             "Circuit_mixed_omega0.txt",  # 4
             "Circuit_mixed_30.txt",  # 5
             "Circuit_mixed.txt",  # 6
             "Circuit_resistor_task1.txt",  # 7
             "Circuit_resistor_task2.txt"]  # 8

st = time.time()
solve.solve_circuit(filenames[7], filePath="StandardCircuits")
et = time.time()

print(f"Execution time was: {et-st} s")