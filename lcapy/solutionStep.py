from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lcapy.circuit import Circuit

from lcapy.componentRelation import ComponentRelation
from typing import Union


class SolutionStep:
    def __init__(self, circuit: Circuit, cpts: list[str], newCptName: str,
                 relation: ComponentRelation, solutionText: str, lastStep: Circuit, nextStep: Circuit,
                 ):
        self.circuit: Circuit = circuit
        self.cpts: list[str] = cpts
        self.newCptName: Union[str, None] = newCptName
        self.relation: ComponentRelation = relation
        self.isInitialStep: bool = not (self.cpts or self.newCptName or self.relation)
        self.solutionText: Union[str, None] = solutionText
        self.lastStep: Union[Circuit, None] = lastStep
        self.nextStep: Union[Circuit, None] = nextStep

    def draw(self):
        from lcapy.drawWithSchemdraw import DrawWithSchemdraw
        DrawWithSchemdraw(self.circuit).draw()

    def getImageData(self) -> str:
        from lcapy.drawWithSchemdraw import DrawWithSchemdraw
        return DrawWithSchemdraw(self.circuit).getImageData()
