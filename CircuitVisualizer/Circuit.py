import matplotlib.pyplot as plt
from typing import Self
from platform import system
# weird shit so I can have PyLance when working within the project and correct imports when importing the project from somewhere else
# this will probably not stay like this, since this should at some point be an installable package (as soon as there won't be major changes)
import sys, os
if os.path.dirname(__file__)[:os.path.dirname(__file__).rfind("\\")] in sys.path:
    from PyCirVis.Components import *
else:
    from Components import *

class Circuit():
    def __init__(self, modes: int = 1) -> None:
        self._modes: list[int] = [i for i in range(modes)]
        self._components: dict[int, list[Component]] = dict([(mode, list()) for mode in self._modes])
        self._modeNames: list[str] = [str(mode) for mode in self._modes]
        self._barrierCount: int = 0
        self._gratingCouplers: bool = False

    def add(self, component: Component, mode: int = 0) -> Self:
        if mode not in self._modes:
            raise ValueError(f"Mode {mode} is not in the circuit.")
        
        if type(component) is Barrier:
            self._barrierCount += 1
            self._evenOutComponents(self._modes)
            for mode in self._modes:
                self._components[mode].append(component)
            return self
        
        if type(component) is MZI and component.decompose:
            if component.twoPhases and component.reverse:
                self.add(PhaseShifter(component.phaseLabel[0]), mode+component.phasePos)
            self.add(BeamSplitter(), mode)
            self.add(PhaseShifter(component.phaseLabel[0+component.reverse]), mode+component.phasePos)
            self.add(BeamSplitter(), mode)
            if component.twoPhases and not component.reverse:
                self.add(PhaseShifter(component.phaseLabel[1]), mode+component.phasePos)
            return self

        if component._multimode:
            if mode+1 not in self._modes:
                raise ValueError(f"Cannot add multi-mode component since mode {mode+1} is not in the circuit.")
            
            self._evenOutComponents([mode, mode+1])
            self._components[mode+1].append(component)

        self._components[mode].append(component)
        return self
    
    def addGratingCouplers(self):
        self._gratingCouplers = True
        for mode in self._modes:
            self._components[mode].insert(0, GratingCoupler())

    def setModeNames(self, modeNames: list[str]) -> None:
        if len(modeNames) != len(self._modes):
            raise ValueError(f"Given length of modeNames ({len(modeNames)}) does not match number of modes in circuit ({len(self._modes)})")
        self._modeNames = modeNames

    def show(self) -> None:
        figure = plt.figure()
        figure.set_size_inches(10, 6)
        plt.axis("off")
        drawPos = dict([(mode, 0) for mode in self._modes])
        maxComp = self._maxComponents()
        skipIDs = list()
        lastBarrierPos = 0
        barriersDrawn = 0
        barrierAnnotated = False

        for mode in self._modes:
            plt.annotate(self._modeNames[mode], (-3, self._modeToY(mode)), ha="center", va="center", weight="bold")
            if not self._gratingCouplers:
                Component._straightLine(-1, self._modeToY(mode), 1, linewidth=1)

        for i in range(maxComp):
            for mode in self._modes:
                if i >= len(self._components[mode]):
                    continue

                currentComp = self._components[mode][i]
                if currentComp is None:
                    continue

                if type(currentComp) is Barrier:
                    barriersDrawn += 1
                    maxLength = max([drawPos[mode] for mode in self._modes])
                    for mode in self._modes:
                        Component._straightLine(drawPos[mode], self._modeToY(mode), maxLength-drawPos[mode], linewidth=1)
                        drawPos[mode] = maxLength
                        currentComp._draw(drawPos[mode], self._modeToY(mode))
                        drawPos[mode] += currentComp._width
                    
                    if currentComp.label != "":
                        barrierAnnotated = True
                        xmid = lastBarrierPos+(drawPos[0]-currentComp._width/2-lastBarrierPos)/2
                        if barriersDrawn == self._barrierCount:
                            xmid += 0.5
                        elif barriersDrawn != self._barrierCount and currentComp.visual:
                            plt.plot([drawPos[0]-currentComp._width/2, drawPos[0]-currentComp._width/2],
                                 [self._modeToY(self._modes[0])-1, self._modeToY(self._modes[-1])+1], linestyle=":", c="black")
                        plt.annotate(currentComp.label, (xmid, self._modeToY(self._modes[-1])+2), ha="center", va="center", weight="bold")
                    lastBarrierPos = drawPos[0]-currentComp._width/2
                    break

                if currentComp._multimode:
                    if currentComp._id not in skipIDs:
                        skipIDs.append(currentComp._id)
                        continue

                    xdist = drawPos[mode] - drawPos[mode-1]
                    if xdist < 0:
                        Component._straightLine(drawPos[mode], self._modeToY(mode), -xdist, linewidth=1)
                        drawPos[mode] += -xdist
                    elif xdist > 0:
                        Component._straightLine(drawPos[mode-1], self._modeToY(mode-1), xdist, linewidth=1)
                        drawPos[mode-1] += xdist

                    currentComp._draw(drawPos[mode], self._modeToY(mode))
                    drawPos[mode] += currentComp._width
                    drawPos[mode-1] += currentComp._width
                    continue
                
                currentComp._draw(drawPos[mode], self._modeToY(mode))
                drawPos[mode] += currentComp._width

            if i == maxComp - 1:
                maxLength = max([drawPos[mode] for mode in self._modes])
                for mode in self._modes:
                    if drawPos[mode] < maxLength:
                        Component._straightLine(drawPos[mode], self._modeToY(mode), maxLength-drawPos[mode], linewidth=1)

        for mode in self._modes:
            Component._straightLine(maxLength, self._modeToY(mode), 1, linewidth=1)
            plt.annotate(self._modeNames[mode], (maxLength+3, self._modeToY(mode)), ha="center", va="center", weight="bold")

        extraY = 3 if barrierAnnotated else 1
        plt.axis((-4, maxLength+4, -1, self._modeToY(self._modes[-1])+extraY))
        plt.tight_layout()
        plt.show()

    @staticmethod
    def _modeToY(mode: int) -> int:
        return 2 * mode
    
    def _maxComponents(self, modes: list[int] = []) -> int:
        modes = self._modes if len(modes) == 0 else modes
        return max([len(self._components[mode]) if mode in modes else 0 for mode in self._modes])
    
    def _evenOutComponents(self, modes: list[int]) -> None:
        maxComp = self._maxComponents(modes)
        for mode in modes:
            if len(self._components[mode]) < maxComp:
                [self._components[mode].append(None) for _ in range(maxComp - len(self._components[mode]))]

    def _DEBUG_PRINT_COMPS(self) -> None:
        for key, val in self._components.items():
            print(key, [c._id if c is not None else "|" for c in val])
    