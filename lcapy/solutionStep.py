from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lcapy.circuit import Circuit
    from lcapy import DrawWithSchemdraw

from lcapy.componentRelation import ComponentRelation
from typing import Union


class SolutionStep:
    def __init__(self, circuit: Circuit, cpt1: str, cpt2: str, newCptName: str,
                 relation: ComponentRelation, solutionText: str, lastStep: Circuit, nextStep: Circuit,
                 ):
        self.circuit: Circuit = circuit
        self.cpt1 = cpt1
        self.cpt2 = cpt2
        self.cpts: list[str] = [cpt1, cpt2]
        self.newCptName: Union[str, None] = newCptName
        self.relation: ComponentRelation = relation
        self.isInitialStep: bool = not (self.cpts or self.newCptName or self.relation)
        self.solutionText: Union[str, None] = solutionText
        self.lastStep: Union[Circuit, None] = lastStep
        self.nextStep: Union[Circuit, None] = nextStep

    def draw(self):
        DrawWithSchemdraw(self.circuit).draw()
