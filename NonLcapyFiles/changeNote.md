## 1.24+inskale.0.36
- fix undefined circuitType in export
- fix wrong cpt type when symbols are used
- fix svg file generation
- fix svg file generation error in pipeline
- add frequency to source export
- add test for svg file generation

## 1.24+inskale.0.35
- fixed resubstitution from value to component (if complex addition defaulted to inductance - error
 in if evaluation)
- fix value error in solution.py
- restructure Circuits folder
- adapt tests to new structure

## 1.24+inskale.0.34
- fixed phase for Z
- fix unrounded val for imaginary part of Z

## 1.24+inskale.0.33
- differenciate between symbolic calculation and "normal" calculation
- fix rounding errors (values not rounded)
- new values in export, magnitude and phase
- circuits with symbol for omega can not be solved anymore

## 1.24+inskale.0.32
- replace labels with max width text (123.456 mA -> ###.### ##) to adjust view box in svg when
labels are replaced with values in frontend
- return impedance instead of complex value in solution dict
- only remove sin cos in homogenous circuit
- correct negative current for capacitors in homogenous ac circuit

## 1.24+inskale.0.31
- enable calculation with symbolic values for dc resistor circuits
- remove sin cos from homogenous circuits

## 1.24+inskale.0.30
- wrong convertion for values in step0 in ac circuits fixed
- fixed wrong convertion value for F < 1 in ac circuits
- return source info and all components in step0

## 1.24+inskale.0.29
- label for horizontal elements adjusted
- corrected error in uges element name in svg
- change voltage abbreviation with language
- add all components to return dict

## 1.24+inskale.0.28
- step0 returns different object
- changed label positions
- new element class names in svg file

## 1.24+inskale.0.27
- return circuit info in step0

## 1.24+inskale.0.26
- return dict not files
- accept n elements for simplification

## 1.24+inskale.0.25
- remove solution text from solution (may brake from changes not used anymore)
- remove latexEquation (equation is build in the ui as needed)

## 1.24+inskale.0.24
- transparent fill for resistors to make them clickable in firefox
- resolve solve.solve_circuit issue for Hetznecker circuit

## 1.24+inskale.0.23
- reduce distance between element and voltage arrow, collision when elements are drawn around
a corner e.g. right and then down


## 1.24+inskale.0.22
- subscript suffix of voltage source current label and voltage label
- support language dependend suffixes for current and voltage label of voltage source

## 1.24+inskale.0.21
- fix symbol for voltage drop in initial step always 'U'
- exported names for voltage drop now depend on language and the used voltage symbol in the svg-File

## 1.24+inskale.0.20
- use changed interface of schemdraw 0.19+inskale.0.5

## 1.24+inskale.0.19
- String that is shown for voltage drops is a parameter, so it can be
e.g. U1 in german and V1 in english that is shown next to elements

## 1.24+inskale.0.18
- add current and voltage arrows
- current and voltage arrows (including their labels) have the class "arrow" in the svg element

## 1.24+inskale.0.17
- fix modern art, some circuits where drawn incorrect
- voltages and currents always negative

## 1.24+inskale.0.16
- step0 returns same json template as step(n)
- circuitInfo with element values and angular frequency can be exported out of jsonExportCircuitInfo class with
solve.SolveInUserOrder.createCircuitInfo()
- 

## 1.24+inskale.0.15
- shorten decimal places in complex expressions with ten to the power of x 0.00000001234567 -> 1.234 * 10^-8

## 1.24+inskale.0.14
- equation for parallel was: $$\frac{1}{R_1} + \frac{1}{R_2} = R_{ges}$$ now corrected to: $$\frac{1}{\frac{1}{R_1} + \frac{1}{R_2}} = R_{ges}$$
- change multiplikation dot to \cdot
- round values in json export (evalf makes fixed number of digits e.g. evalf(n=4)): 123.45678 -> 123.4; 1.2345678 -> 1.234
I guess that is because of the prefixes
- 
## 1.24+inskale.0.13
- add current sources

## 1.24+inskale.0.12
- integrate lcapy test (except those which rely on scipy) and implement lcapy-inskale test
- buildPackeg.ps1 supports python interpreter path and pyTest suit
- increase speed of componentnamer.py

## 1.24+inskale.0.11
- fixed component types in svg and calculation, now display the same component type

## 1.24+InskaLE.0.10
- updated base lcapy version to 1.24
- implemented export of branch voltages and currents
- expressions that are only real or only imaginary get a prefix
- using base class lcapy.Expr for typecheck instead of listing each subclass

## 1.22+InskaLE.0.9
- Internal class NetlistLine uses lcapy parser instead of own implementation to be more robust

## 1.22+InskaLE.0.8
- write the value of a component (its resistance, capacitance ...) with its unit and unit prefix in latex
format into the svg under the tag value

## 1.22+InskaLE.0.7
- The step0-json now contains all components of the circuit in its initial state (without) simplifications
and the frequency omega_0 in Hz if it is an AC circuit. If it is a DC circuit omega_0 is equal to 0.
- simplification is done in impedance in all cases if the result can be transformed to R, L or C
the calculation and the saved values are transformed accordingly. If components are R, L or C and the
result is a component which is a mixture of those tree the calculation is displayed in impedance to the
user and the transformation of the components as well. Therefore, there are tree new values in the
export-Jason convVal1 convVal2 and convRes these are populated if on of the values value1 value2 or 
result values can be transformed. Also, there is an omega_0 value for AC analysis.
- Prefixes for values are added when the calculation is not in impedance. The Prefixes available are
available by importing: from sympy.physics.units.prefixes import PREFIXES
Values are round to max. 3 decimal places.

## 1.22+InskaLE.0.6
- show dots on branch knots, when there are more than two occurrences of the same node in the circuit.

## 1.22+InskaLE.0.5
- Fix error that the inverse sum is not used when needed.

## 1.22+InskaLE.0.4
- return filenames from draw and export functions. Add function to draw a standalone step.

## 1.22+InskaLE.0.3
- removed unnecessary print of latex expression

## 1.22+InskaLE.0.2
- The json-File is extended by latexEquation. The calculation from the simplification of two
elements. The expression is converted from sympy to a latex string

## V1.22+inskale.0.1
- Creates a step-by-step Solution where only to Elements are simplified
in one step and exports the Steps into a json-File. The Circuits
(more specific the Netlists) can be drawn with the additional package
Schemdraw and don't need LaTeX installation. Only Supported Elements are
Resistors, Inductors, Wires, Voltage Sources, Impedances (special form of Resistors)