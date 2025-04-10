import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

class Component:
    def __init__(self, width: float, color: str, id: str, multimode: bool = False) -> None:
        self._width: float = width
        self._color: str = color
        self._id: str = id
        self._multimode: bool = multimode
        self._linewidth: float = 1.0

    def _draw(self, x: float, y: float) -> None:
        raise NotImplementedError(f"draw method not implemented for component {self.__class__.__name__}")
    
    @staticmethod
    def _straightLine(x: float, y: float, length: float, color: str = "black", **kwargs) -> None:
        plt.plot([x, x+length], [y, y], c=color, zorder=0, **kwargs)

    @staticmethod
    def _cos(x: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
        return a * np.cos(b * (x - c)) + d

    @staticmethod
    def _connector(x: float, y1: float, y2: float, width: float = 1, color: str = "black", **kwargs) -> None:
        amp = (y1 - y2) / 2
        xrange = np.linspace(x, x+width, 1000)
        plt.plot(xrange, Component._cos(xrange, amp, np.pi/width, x, y1-amp), c=color, zorder=0, **kwargs)

    @staticmethod
    def _rotate(x: list or np.ndarray, y: list or np.ndarray, deg: float) -> tuple[np.ndarray, np.ndarray]:
        theta = np.deg2rad(deg)
        x = x if type(x) is np.ndarray else np.array(x)
        y = y if type(y) is np.ndarray else np.array(y)
        return x * np.cos(theta) - y * np.sin(theta), x * np.sin(theta) + y * np.cos(theta)

    @staticmethod
    def _translate(x: list or np.ndarray, y: list or np.ndarray, xOff: float, yOff: float) -> tuple[np.ndarray, np.ndarray]:
        x = x if type(x) is np.ndarray else np.array(x)
        y = y if type(y) is np.ndarray else np.array(y)
        return x + xOff, y + yOff
       
    @staticmethod 
    def _box(centerX: float, centerY: float, width: float, height: float, color: str, angle: float = 0, **kwargs) -> None:
        xCorners = [centerX-width/2, centerX-width/2, centerX+width/2, centerX+width/2, centerX-width/2]
        yCorners = [centerY-height/2, centerY+height/2, centerY+height/2, centerY-height/2, centerY-height/2]
        rotX, rotY = Component._translate(*Component._rotate(*Component._translate(xCorners, yCorners, -centerX, -centerY), angle), centerX, centerY)
        plt.plot(rotX, rotY, c=color, zorder=2, **kwargs)
        alphaCol = tuple([c * 0.3 + 0.7 for c in colors.to_rgba(color)])
        plt.fill(rotX, rotY, c=alphaCol, zorder=1)

    def _cross(self, center: tuple[float], size: tuple[float], coords: tuple[float], color: str, **kwargs) -> None:
        amp = (coords[0] - coords[1]) / 2
        p1 = (center[0]-0.3, self._cos(center[0]-0.3, amp, np.pi/size[0], coords[2], coords[0]-amp))
        p2 = (center[0], center[1]+0.1)
        p3 = (center[0]+0.3, self._cos(center[0]+0.3, -amp, np.pi/size[0], coords[2], coords[1]+amp))
        p4 = (center[0]+0.1, center[1])
        p5 = (center[0]+0.3, self._cos(center[0]+0.3, amp, np.pi/size[0], coords[2], coords[0]-amp))
        p6 = (center[0], center[1]-0.1)
        p7 = (center[0]-0.3, self._cos(center[0]-0.3, -amp, np.pi/size[0], coords[2], coords[1]+amp))
        p8 = (center[0]-0.1, center[1])
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], c=color, zorder=2, **kwargs)
        plt.plot([p2[0], p3[0]], [p2[1], p3[1]], c=color, zorder=2, **kwargs)
        plt.plot([p3[0], p4[0]], [p3[1], p4[1]], c=color, zorder=2, **kwargs)
        plt.plot([p4[0], p5[0]], [p4[1], p5[1]], c=color, zorder=2, **kwargs)
        plt.plot([p5[0], p6[0]], [p5[1], p6[1]], c=color, zorder=2, **kwargs)
        plt.plot([p6[0], p7[0]], [p6[1], p7[1]], c=color, zorder=2, **kwargs)
        plt.plot([p7[0], p8[0]], [p7[1], p8[1]], c=color, zorder=2, **kwargs)
        plt.plot([p8[0], p1[0]], [p8[1], p1[1]], c=color, zorder=2, **kwargs)
        alphaCol = tuple([c * 0.3 + 0.7 for c in colors.to_rgba(color)])
        plt.fill([p1[0], p2[0], p3[0], p4[0], p5[0], p6[0], p7[0], p8[0], p1[0]],
                 [p1[1], p2[1], p3[1], p4[1], p5[1], p6[1], p7[1], p8[1], p1[1]], c=alphaCol)

class PhaseShifter(Component):
    COUNT = -1
    def __init__(self, label: str = "") -> None:
        PhaseShifter.COUNT += 1
        super().__init__(1.5, "tab:blue", f"PS{PhaseShifter.COUNT}")
        self.label: str = label

    def _draw(self, x: float, y: float) -> None:
        self._straightLine(x, y, self._width, linewidth=self._linewidth)
        self._box(x+self._width/2, y, 0.6, 0.4, self._color, linewidth=self._linewidth)
        plt.annotate(self.label, (x+self._width/2, y+0.4), ha="center", va="center")

class BeamSplitter(Component):
    COUNT = -1
    def __init__(self, type: str = "mmi", label: str = "") -> None:
        BeamSplitter.COUNT += 1
        super().__init__(3.5, "tab:orange", f"BS{BeamSplitter.COUNT}", multimode=True)
        self.label: str = label

    def _draw(self, x: float, y: float) -> None:
        self._connector(x, y, y-0.9, linewidth=self._linewidth)
        self._connector(x, y-2, y-1.1, linewidth=self._linewidth)
        self._connector(x+2.5, y-0.9, y, linewidth=self._linewidth)
        self._connector(x+2.5, y-1.1, y-2, linewidth=self._linewidth)
        self._box(x+1.75, y-1, 1.5, .5, self._color, linewidth=self._linewidth)

class Crossing(Component):
    COUNT = -1
    def __init__(self, label: str = "") -> None:
        Crossing.COUNT += 1
        super().__init__(3.5, "tab:gray", f"CR{Crossing.COUNT}", multimode=True)
        self.label: str = label

    def _draw(self, x: float, y: float) -> None:
        self._connector(x, y, y-2, self._width, linewidth=self._linewidth)
        self._connector(x, y-2, y, self._width, linewidth=self._linewidth)
        self._cross((x+self._width/2, y-1), (self._width, 2), (y, y-2, x), self._color, linewidth=self._linewidth)

class Barrier(Component):
    COUNT = -1
    def __init__(self, label: str = "", visual: bool = False, extent: bool = False) -> None:
        Barrier.COUNT += 1
        super().__init__(2 if extent else 0, "", f"BRR{Barrier.COUNT}")
        self.label: str = label
        self.extent: bool = extent
        self.visual: bool = visual
        self._width *= extent

    def _draw(self, x: float, y: float) -> None:
        if self.extent:
            self._straightLine(x, y, self._width, linewidth=self._linewidth)

class MZI(Component):
    COUNT = -1
    def __init__(self, decomp: bool = True, twoPhases: bool = False, phasePos: int = 1, reverse: bool = False, phaseLabel: str or list[str] = "", label: str = "") -> None:
        MZI.COUNT += 1
        super().__init__(4.4, "tab:purple", f"MZI{MZI.COUNT}", multimode=True)
        self.label: str = label if label != "" else "MZI$_{\phi, \\theta}$"
        self.decompose: bool = decomp
        self.twoPhases: bool = twoPhases
        self.phasePos: int = 1 if phasePos >= 1 else 0
        self.reverse: bool = reverse
        self.phaseLabel = [phaseLabel]
        if twoPhases:
            if type(phaseLabel) == list and len(phaseLabel) == 1:
                self.phaseLabel = [phaseLabel[0], ""]
            elif type(phaseLabel) == str:
                self.phaseLabel = [phaseLabel, ""]
            else:
                self.phaseLabel = phaseLabel

    def _draw(self, x: float, y: float) -> None:
        self._straightLine(x, y, self._width, linewidth=self._linewidth)
        self._straightLine(x, y-2, self._width, linewidth=self._linewidth)
        self._box(x+(self._width-2*0.2)/2, y-1, self._width-2*0.2, 3, self._color, linewidth=self._linewidth)
        plt.annotate("MZI$_{\phi, \\theta}$", (x+2.2, y-1), ha="center", va="center")
        
class GratingCoupler(Component):
    COUNT = -1
    def __init__(self, twoDimensional: bool = False, label: str = "") -> None:
        GratingCoupler.COUNT += 1
        super().__init__(3.5, "tab:red" if twoDimensional else "tab:green", f"GC{GratingCoupler.COUNT}")
        self.label: str = label
        self.twoD = twoDimensional
        
    def _drawDim1(self, x: float, y: float) -> None:
        self._straightLine(x+2.5, y, 1, linewidth=self._linewidth)
        self._box(x+0.2, y, 0.4, 0.4, self._color, linewidth=self._linewidth)
        plt.plot([x+0.4, x+2.5, x+0.4], [y+0.2, y, y-0.2], c=self._color, linewidth=self._linewidth)
        alphaCol = tuple([c * 0.3 + 0.7 for c in colors.to_rgba(self._color)])
        plt.fill([x+0.4, x+2.5, x+0.4], [y+0.2, y, y-0.2], c=alphaCol, zorder=1)
        
    def _drawDim2(self, x: float, y: float) -> None:
        plt.plot([x, x+1], [y, y], c="black", zorder=0)
        plt.plot([x, x+1], [y-2, y-2], c="black", zorder=0)
        plt.plot([x+1, x+1.5], [y-2, y-1.5], c="black", zorder=0)
        plt.plot([x+1, x+1.5], [y, y-0.5], c="black", zorder=0)
        self._box(x+2, y-1, 0.5, 0.5, "tab:red", angle=45)
        xTriangleUpper = [x+1.75, x+2, x+2.25]
        xTriangleLower = [x+1.75, x+0.9, x+1.75]
        yTriangleUpper = [y-0.75, y+0.1, y-0.75]
        yTriangleLower = [y-1.25, y-1, y-0.75]
        rotXUpper, rotYUpper = self._translate(*self._rotate(*self._translate(xTriangleUpper, yTriangleUpper, -(x+2), -(y-1)), 45), x+2, y-1)
        rotXLower, rotYLower = self._translate(*self._rotate(*self._translate(xTriangleLower, yTriangleLower, -(x+2), -(y-1)), 45), x+2, y-1)
        plt.plot(rotXUpper, rotYUpper, c="tab:red", zorder=2)
        plt.plot(rotXLower, rotYLower, c="tab:red", zorder=2)
        alphaCol = tuple([c * 0.3 + 0.7 for c in colors.to_rgba("tab:red")])
        plt.fill(rotXUpper, rotYUpper, c=alphaCol, zorder=1)
        plt.fill(rotXLower, rotYLower, c=alphaCol, zorder=1)

    def _draw(self, x: float, y: float) -> None:
        if self.twoD:
            self._drawDim2(x, y)
        else:
            self._drawDim1(x, y)
        