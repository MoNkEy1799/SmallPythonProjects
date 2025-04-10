from Circuit import Circuit
from Components import *

circuit = Circuit(10)
circuit.setModeNames([str(i) if i not in [3, 8] else f"({i})" for i in range(1, 11)])
circuit.addGratingCouplers()

circuit.add(MZI(twoPhases=True, phaseLabel=["21", "22"]), 0)
circuit.add(MZI(twoPhases=True, phaseLabel=["51", "52"]), 3)
circuit.add(MZI(twoPhases=True, phaseLabel=["71", "72"]), 5)
circuit.add(MZI(twoPhases=True, phaseLabel=["101", "102"]), 8)

circuit.add(Barrier(label="State-Prep", visual=True, extent=True))

circuit.add(Crossing(), 2)
circuit.add(Crossing(), 1)
circuit.add(Crossing(), 6)
circuit.add(Crossing(), 7)

circuit.add(Barrier(label="Crossings", visual=True, extent=True))

circuit.add(MZI(phaseLabel="43"), 2)
circuit.add(MZI(phaseLabel="63"), 4)
circuit.add(MZI(phaseLabel="73", phasePos=0), 6)

circuit.add(Barrier(label="Reconfiguration", visual=True, extent=True))

circuit.add(MZI(twoPhases=True, phaseLabel=["24", "25"], reverse=True), 0)
circuit.add(MZI(twoPhases=True, phaseLabel=["54", "55"], reverse=True), 3)
circuit.add(MZI(twoPhases=True, phaseLabel=["74", "75"], reverse=True), 5)
circuit.add(MZI(twoPhases=True, phaseLabel=["104", "105"], reverse=True), 8)

circuit.add(Barrier(label="Tomography"))

circuit.show()
