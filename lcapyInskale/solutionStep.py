from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lcapyInskale.circuit import Circuit

from lcapyInskale.componentRelation import ComponentRelation
from typing import Union
from simplipfy.SimplifyInUserOrder.simplifierStates import SimplifierStates

class SolutionStep:
    def __init__(self, circuit: Circuit, cpts: list[str], newCptName: str,
                 relation: ComponentRelation, lastStep: Circuit, nextStep: Circuit
                 ):
        self.circuit: Circuit = circuit
        self.cpts: list[str] = cpts
        self.newCptName: Union[str, None] = newCptName
        self.relation: ComponentRelation = relation
        self.simplifierSate: SimplifierStates = SimplifierStates.fromCptRelation(relation)
        self.isInitialStep: bool = not (self.cpts or self.newCptName or self.relation)
        self.lastStep: Union[Circuit, None] = lastStep
        self.nextStep: Union[Circuit, None] = nextStep

    def draw(self, langSymbols):
        from simplipfy.Svg.drawWithSchemdraw import DrawWithSchemdraw
        DrawWithSchemdraw(self.circuit, langSymbols=langSymbols).draw()

    def getImageData(self, langSymbols) -> str:
        from simplipfy.Svg.drawWithSchemdraw import DrawWithSchemdraw
        return DrawWithSchemdraw(self.circuit, langSymbols=langSymbols).getImageData()

    def generalizedImageData(self, langSymbols) -> str:
        from simplipfy.Svg.drawWithSchemdraw import DrawWithSchemdraw
        from simplipfy.Svg.drawingConfig import drawing_config_instance as dci
        dci.lock(on="--generalize-true --optimize-mobile")
        svgString = DrawWithSchemdraw(self.circuit, langSymbols=langSymbols).getImageData()
        dci.unlock()
        return svgString