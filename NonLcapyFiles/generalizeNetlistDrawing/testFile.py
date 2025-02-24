import lcapy
from lcapy.validateCircuitFile import ValidateCircuitFile
from lcapy import Circuit
from lcapy import DrawWithSchemdraw
from lcapy.langSymbols import LangSymbols
from netlistToGraph import NetlistGraph

if not ValidateCircuitFile(["test1.txt"]):
    exit("File not valid")

cct = Circuit("test1.txt")
DrawWithSchemdraw(cct, LangSymbols()).draw()
b = NetlistGraph(cct)

# lcapyCir = lcapy.Circuit("..\\Circuits\\resistor\\00_Resistor_Hetznecker.txt")
# a = NetlistGraph(lcapyCir)