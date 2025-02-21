import lcapy
import networkx as nx
from lcapy import NetlistLine
from maxWidth import MaxWidth
from widestPath import WidestPath

class NetlistGraph:
    def __init__(self, lcapyCircuit: lcapy.Circuit):
        self.cct = lcapyCircuit
        self.graphStart: int
        self.graphEnd: int
        self.cleandUpNetlist: list[NetlistLine] = self._cleanUpNetlist()
        self.graph: nx.DiGraph = self._createGraph()
        self.spanningWidth = self._findSpanningWidth(self.graph, self.graphStart, self.graphEnd)
        print(f"branchWidth: {self.spanningWidth.width}, nodes: {self.graph.nodes}")
        print("------------------------")
        self.paths = self._findPaths()
        for path in self.paths:
            nodesList = list(path)
            branchWidth = self._findBranchWidth(self.graph.subgraph(nodesList), nodesList[0], nodesList[-1])
            print(f"branchWidth: {branchWidth.width}, path: {nodesList}")
        self.longestPath = self._findLongestPath()


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

                if str(self.graphStart) in shallBeReplaced:
                    self.graphStart = int(replaceNodeWith)
                if str(self.graphEnd) in shallBeReplaced:
                    self.graphEnd = int(replaceNodeWith)

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

    def _findMaxSpanningWidth(self):
        self._findSpanningWidth(self.graph, self.graphStart, self.graphEnd)

    def _findBranchWidth(self, branch: nx.DiGraph, startNode, endNode) -> MaxWidth:
        return self._findSpanningWidth(branch, startNode, endNode)

    def _findWidestBranch(self) -> WidestPath:
        maxWidth = MaxWidth(0, 0)
        index = 0
        for idx, path in iter(self.paths):
            nodesList = list(path)
            width = self._findBranchWidth(self.graph.subgraph(nodesList), nodesList[0], nodesList[-1])
            if width.width > maxWidth.width:
                maxWidth = width
                index = idx
        return WidestPath(maxWidth.width, maxWidth.depth, index, self.graph)

    @staticmethod
    def _findSpanningWidth(graph: nx.DiGraph, startNode, endNode) -> MaxWidth:
        """
        calculate the maximum count of concurrent branches to determine the needed raster width to draw netlist
        :return: MaxWidth object -> maxWidth and depth
        """

        # there has to be one branch and
        # instead of removing the endNode increase by one, the endNode has no outgoing edges therefore its result is -1
        checkNodes = list(graph.successors(startNode))
        maxWidth = MaxWidth(0, 0)
        iteration = 1

        while True:
            width = len(checkNodes)
            if width > maxWidth.width:
                maxWidth = MaxWidth(width, iteration)
            nextNodes = []
            for node in checkNodes:
                nextNodes.extend(list(graph.successors(node)))
            if len(nextNodes) == 1 and nextNodes[0] == endNode:
                break
            checkNodes = nextNodes
            iteration += 1

        return maxWidth

    def _findPaths(self) -> list[list]:
        return list(nx.all_simple_paths(self.graph, self.graphStart, self.graphEnd))

    def _findLongestPath(self):
        maxPathLen = 0
        foundPath = None
        for path in self.paths:
            curPathLen = len(path)
            if curPathLen > maxPathLen:
                foundPath = path
                maxPathLen = curPathLen

        return foundPath or list(self.paths)[0]

    @property
    def maxPathLength(self):
        return len(self.longestPath)