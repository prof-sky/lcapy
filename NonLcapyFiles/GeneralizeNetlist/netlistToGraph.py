import lcapy
import networkx as nx
from lcapy import NetlistLine

class NetlistGraph:
    def __init__(self, lcapyCircuit: lcapy.Circuit):
        self.cct = lcapyCircuit
        self.graphStart: int
        self.graphEnd: int
        self.cleandUpNetlist: list[NetlistLine] = self._cleanUpNetlist()
        self.graph: nx.DiGraph = self._createGraph()
        self.spanningWidth = self._findSpanningWidth()
    def _cleanUpNetlist(self) -> list[NetlistLine]:
        """
        Converts the netlist into an easy-to-use format and removes lines from netlist
        :returns list of NetlistLines
        """
        netLines = [NetlistLine(line) for line in self.cct.netlist().splitlines()]
        # todo remove print
        print("_cleanUpNetlist:")
        print(self.cct.netlist())
        print("------------------------")
        cleandUpNetlist = []
        for line in netLines:
            if line.type == "W":
                continue
            if line.type == "V" or line.type == "I":
                self.graphStart = line.startNode
                self.graphEnd = line.endNode
                continue

            nodesToReplaceWith = self.cct.equipotential_nodes.keys()
            for replaceNodeWith in nodesToReplaceWith:
                shallBeReplaced = self.cct.equipotential_nodes[replaceNodeWith]

                if str(line.startNode) in shallBeReplaced:
                    line.startNode = int(replaceNodeWith)
                if str(line.endNode) in shallBeReplaced:
                    line.endNode = int(replaceNodeWith)
            cleandUpNetlist.append(line)

        #todo remove print
        for newLine in cleandUpNetlist:
            newLine = newLine.reconstruct()
            newLine = newLine[:newLine.find(";")]
            print(newLine)

        return cleandUpNetlist

    def _createGraph(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        for line in self.cleandUpNetlist:
            graph.add_edge(line.startNode, line.endNode, name=line.label)

        return graph

    def _findSpanningWidth(self) -> int:
        """
        calculate the maximum count of concurrent branches to determine the needed raster width to draw netlist
        :return: int
        """
        # there has to be one branch and
        # instead of removing the endNode increase by one, the endNode has no outgoing edges therefore its result is -1
        width = 2
        for node in self.graph.nodes:
            width += len(self.graph.out_edges(node)) - 1

        return width
lcapyCir = lcapy.Circuit("..\\Circuits\\resistor\\00_Resistor_Hetznecker.txt")
a = NetlistGraph(lcapyCir)