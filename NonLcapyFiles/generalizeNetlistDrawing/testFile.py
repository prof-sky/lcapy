import lcapy
from lcapy.validateCircuitFile import ValidateCircuitFile
from lcapy import Circuit
from lcapy import DrawWithSchemdraw
from lcapy.langSymbols import LangSymbols
from netlistGraph import NetlistGraph
from netlistToGraph import NetlistToGraph

if not ValidateCircuitFile(["test1.txt"]):
    exit("File not valid")

cct = Circuit("test1.txt")
DrawWithSchemdraw(cct, LangSymbols()).draw()
graph = NetlistToGraph(cct)
b = NetlistGraph(graph.MultiDiGraph(), graph.startNode, graph.endNode)

# lcapyCir = lcapy.Circuit("..\\Circuits\\resistor\\00_Resistor_Hetznecker.txt")
# a = NetlistGraph(lcapyCir)