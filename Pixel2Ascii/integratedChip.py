import numpy as np
import time
import threading

class PXL2ASCII:
    def __init__(self, asciiMask: str | list[str] | dict | None = None) -> None:
        if asciiMask is None:
            self.converter = {0.667: "#", 0.334: ".", 0.0: " "}
        else:
            self.converter = self._getAsciiConverter(asciiMask)

    def convertBrightnessToAscii(self, brightnessArray: list[list[int]]) -> None:
        self.asciiImage = ""
        for i in range(len(brightnessArray)):
            for j in range(len(brightnessArray[0])):
                for cap in self.converter:
                    if brightnessArray[i][j] >= cap:
                        self.asciiImage += f"{self.converter[cap]} "
                        break
            self.asciiImage += "\n"

    @staticmethod
    def rgbText(r: int, g: int, b: int, text: str = "\u2588"):
        return f"\x1b[38;2;{r};{g};{b}m{text}{text}\x1b[0m"

    def convertRGBToAscii(self, rgbArray: list[list[list[int]]]) -> None:
        self.asciiImage = ""
        for i in range(len(rgbArray)):
            for j in range(len(rgbArray[0])):
                r, g, b = rgbArray[i,j,:3]
                self.asciiImage += self.rgbText(int(r), int(g), int(b))
            self.asciiImage += "\n"
        
    def _getAsciiConverter(self, asciiMask: str | list[str] | dict) -> dict:
        if isinstance(asciiMask, str) or isinstance(asciiMask, list):
            return dict([(1 - (i + 1) / len(asciiMask), char) for i, char in enumerate(asciiMask)])

        elif isinstance(asciiMask, dict):
            return dict(reversed(sorted(asciiMask.items())))
    
    @staticmethod
    def clearLines(n: int = 0):
        LINE_UP = "\033[1A"
        LINE_CLEAR = "\x1b[2K"
        for _ in range(n):
            print(LINE_UP, end=LINE_CLEAR)

    def show(self, prefix: str = "", end: str = "\n") -> None:
        print(f"{prefix}{self.asciiImage}", end=end)

class LayoutVisualizer:
    def __init__(self, chipLayout: dict, mode: str = "ascii", chipSize: tuple[int] = (45, 30), structSize: int = 2, border: int = 1, padding: int = 2) -> None:
        self.chipLayout = chipLayout
        self.chipSize = chipSize
        self.structSize = structSize
        self.border = border
        self.padding = padding
        self.setColorMode(mode)

        self.array = self.emptyArray()
        self.visualizer = PXL2ASCII(self.asciiMask())

    def setColorMode(self, mode: str):
        self.colors = dict()

        if mode == "color":
            self.dim = 3

            self.colors["struct"] = [186, 186, 186]
            self.colors["hexapod"] = [78, 100, 173]
            self.colors["hexapod_blink"] = [132, 78, 173]
            self.colors["border"] = [242, 242, 242]
            self.colors["background"] = [36, 36, 36]
            for i, c in enumerate(["A", "B", "C", "D", "E", "F", "G", "H", "I"]):
                self.colors[c] = [87, 145, 58]
            for i, c in enumerate(["1", "2", "3", "4", "5", "6", "7", "8", "9"]):
                self.colors[c] = [87, 145, 58]
            for i, c in enumerate("hexapod"):
                self.colors[c] = [26, 77, 196]
            for i, c in enumerate("<>^ˇ"):
                self.colors[c] = [12, 32, 77]

        elif mode == "ascii":
            self.dim = 1

            self.colors["struct"] = 1.0
            self.colors["hexapod"] = 0.95
            self.colors["hexapod_blink"] = 0.9
            self.colors["border"] = 0.1
            self.colors["background"] = 0.0
            for i, c in enumerate(["A", "B", "C", "D", "E", "F", "G", "H", "I"]):
                self.colors[c] = 0.8 + 0.01 * (i + 1)
            for i, c in enumerate(["1", "2", "3", "4", "5", "6", "7", "8", "9"]):
                self.colors[c] = 0.7 + 0.01 * (i + 1)
            for i, c in enumerate("hexapod"):
                self.colors[c] = 0.6 + 0.01 * (i + 1)
            for i, c in enumerate("<>^ˇ"):
                self.colors[c] = 0.5 + 0.01 * (i + 1)

        else:
            raise ValueError("Mode can either be color or ascii")

    def asciiMask(self) -> dict:
        asciiMask = {1.0: "#", 0.95: "O", 0.9: "+", 0.1: ":", 0.0: " "} # 1.0 = structure, 0.9/0.95 = hexapod, 0.1 = border, 0.0 = background
        for i, c in enumerate(["A", "B", "C", "D", "E", "F", "G", "H", "I"]):
            asciiMask[0.8 + 0.01 * (i + 1)] = c # 0.81 - 0.89 = ABCDEFGHI axis label
        for i, c in enumerate(["1", "2", "3", "4", "5", "6", "7", "8", "9"]):
            asciiMask[0.7 + 0.01 * (i + 1)] = c # 0.71 - 0.79 = 123456789 axis label
        for i, c in enumerate("Hexapod"):
            asciiMask[0.6 + 0.01 * (i + 1)] = c # 0.61 - 0.67 = Hexapod axis label
        for i, c in enumerate("<>^ˇ"):
            asciiMask[0.5 + 0.01 * (i + 1)] = c # 0.51 - 0.54 = <>^ˇ arrow axis label

        return asciiMask

    def emptyArray(self) -> np.ndarray:
        if self.dim == 1:
            array = np.zeros((self.chipSize[1] + 2 * self.border + 2 * self.padding + 3, self.chipSize[0] + 2 * self.border + 2 * self.padding + 1))
        elif self.dim == 3:
            array = np.zeros((self.chipSize[1] + 2 * self.border + 2 * self.padding + 3, self.chipSize[0] + 2 * self.border + 2 * self.padding + 1, self.dim))
        array[2:-1, :self.border] = self.colors["border"]
        array[2:-1, -self.border-1:-1] = self.colors["border"]
        array[2:self.border+2, :-1] = self.colors["border"]
        array[-self.border-1:-1, :-1] = self.colors["border"]

        return array

    def xyScaling(self, padding: int):
        maxDistX, maxDistY = 0.0, 0.0
        for structX, structY in self.chipLayout.values():
            for otherX, otherY in self.chipLayout.values():
                if abs(structX - otherX) > maxDistX:
                    maxDistX = abs(structX - otherX)
                if abs(structY - otherY) > maxDistY:
                    maxDistY = abs(structY - otherY)
        scalingX = (self.chipSize[0] - padding - 1) / maxDistX 
        scalingY = (self.chipSize[1] - padding - 1) / maxDistY

        return scalingX, scalingY

    def rotatedArray(self, rotCW90:int = 0) -> np.ndarray:
        c = self.colors
        if rotCW90 == 0:
            rot = 0
            arrow = c["ˇ"]
            hexapod = [c["background"], c["h"], c["e"], c["x"], c["a"], c["p"], c["o"], c["d"], c["background"]]
        elif rotCW90 == 1:
            rot = 3
            arrow = c["<"]
            hexapod = [c["background"], c["h"], c["e"], c["x"], c["a"], c["p"], c["o"], c["d"], c["background"]]
        elif rotCW90 == 2:
            rot = 2
            arrow = c["^"]
            hexapod = list(reversed([c["background"], c["h"], c["e"], c["x"], c["a"], c["p"], c["o"], c["d"], c["background"]]))
        elif rotCW90 == 3:
            rot = 1
            arrow = c[">"]
            hexapod = list(reversed([c["background"], c["h"], c["e"], c["x"], c["a"], c["p"], c["o"], c["d"], c["background"]]))
        else:
            raise ValueError("can only rotate 0, 1, 2 or 3 times")
        
        arrowIndex = int((self.chipSize[0] + self.border + self.padding - 9) / 2)
        self.array[0, :arrowIndex] = arrow
        self.array[0, arrowIndex:arrowIndex+9] = hexapod
        self.array[0, arrowIndex+9:-1] = arrow

        return np.rot90(self.array, rot)

    def fillArray(self) -> None:
        chip = self.array[self.border+self.padding+2:-self.border-self.padding-1, self.border+self.padding:-self.border-self.padding-1]

        structExtend = list()
        for height in range(self.structSize):
            for width in range(self.structSize):
                structExtend.append((width, height))
        structPadding = int(np.max(structExtend))
        scalingX, scalingY = self.xyScaling(structPadding)

        self.structureCoords = dict()
        referencePoint = self.chipLayout[list(self.chipLayout)[0]]
        for struct, (x, y) in self.chipLayout.items():
            self.structureCoords[struct] = list()
            mainCoord = int((x - referencePoint[0]) * scalingX), int((y - referencePoint[1]) * scalingY)
            for se in structExtend:
                for c in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
                    if struct[0] == c:
                        self.array[self.border+self.padding+2+mainCoord[1]+se[1], -1] = self.colors[c]

                for c in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    if struct[1] == c:
                        self.array[-1, self.border+self.padding+mainCoord[0]+se[0]] = self.colors[c]
                
                self.structureCoords[struct].append((mainCoord[0]+se[0]+self.border+self.padding, mainCoord[1]+se[1]+self.border+self.padding+2))
                chip[mainCoord[1] + se[1], mainCoord[0] + se[0]] = self.colors["struct"]

    def showLayout(self, rotCW90: int = 0, clear: bool = True) -> None:
        if self.dim == 1:
            self.visualizer.convertBrightnessToAscii(self.rotatedArray(rotCW90))
        elif self.dim == 3:
            self.visualizer.convertRGBToAscii(self.rotatedArray(rotCW90))

        if clear:
            self.visualizer.clearLines(self.visualizer.asciiImage.count("\n") + 2)

        self.visualizer.show(prefix="\n")

    def changeHexapodPos(self, structure: str, blink: bool = False) -> None:
        for struct in self.structureCoords:
            for coords in self.structureCoords[struct]:
                if struct == structure:
                    if blink:
                        self.array[coords[1], coords[0]] = self.colors["hexapod_blink"]
                    else:
                        self.array[coords[1], coords[0]] = self.colors["hexapod"]
                else:
                    self.array[coords[1], coords[0]] = self.colors["struct"]

class ThreadHandler:
    def __init__(self, visualizer: LayoutVisualizer) -> None:
        self.visualizer = visualizer
        self.events = list()
        self.threads = list()
        self.currentID = 0
        self.first = True
        
    def blinkHexapod(self, struct: str, id: int) -> None:
        blink = False
        while True:
            if self.events[id].is_set():
                break

            self.visualizer.changeHexapodPos(struct, blink=blink)
            self.visualizer.showLayout(1)
            blink = not blink
            time.sleep(1)

    def moveHexapod(self, struct: str) -> None:
        if self.first:
            self.events.append(threading.Event())
            self.threads.append(threading.Thread(target=self.blinkHexapod, args=(struct, self.currentID, ), daemon=True))
            self.threads[self.currentID].start()
            self.first = False
            return
            
        self.events[self.currentID].set()
        self.currentID += 1
        self.events.append(threading.Event())
        self.threads.append(threading.Thread(target=self.blinkHexapod, args=(struct, self.currentID, ), daemon=True))
        self.threads[self.currentID].start()

    def endThreads(self) -> None:
        self.events[self.currentID].set()

def animateLayout(layout: dict, mode: str) -> None:
    vis = LayoutVisualizer(layout, mode=mode, chipSize=(30, 45), structSize=2, border=1, padding=2)
    vis.fillArray()
    TH = ThreadHandler(vis)
    for struct in list(layout_bs)[:4]:
        TH.moveHexapod(struct)
        time.sleep(6)
    TH.endThreads()

def simplePrint(layout: dict, mode: str) -> None:
    vis = LayoutVisualizer(layout, mode=mode, chipSize=(30, 45), structSize=2, border=1, padding=2)
    vis.fillArray()
    vis.showLayout(1)


if __name__ == "__main__":
    layout_bs = {'A1': (1025.0, 1935.0), 'A2': (2275.0, 1935.0), 'A3': (3525.0, 1935.0), 'A4': (4775.0, 1935.0),
                 'A5': (6025.0, 1935.0), 'A6': (7275.0, 1935.0), 'A7': (8525.0, 1935.0), 'A8': (9775.0, 1935.0),
                 'B1': (1025.0, 3826.0), 'B2': (2275.0, 3826.0), 'B3': (3525.0, 3826.0), 'B4': (4775.0, 3826.0),
                 'B5': (6025.0, 3826.0), 'B6': (7275.0, 3826.0), 'B7': (8525.0, 3826.0), 'B8': (9775.0, 3826.0),
                 'C1': (1025.0, 5717.0), 'C2': (2275.0, 5717.0), 'C3': (3525.0, 5717.0), 'C4': (4775.0, 5717.0),
                 'C5': (6025.0, 5717.0), 'C6': (7275.0, 5717.0), 'C7': (8525.0, 5717.0), 'C8': (9775.0, 5717.0),
                 'D1': (1025.0, 7608.0), 'D2': (2275.0, 7608.0), 'D3': (3525.0, 7608.0), 'D4': (4775.0, 7608.0),
                 'D5': (6025.0, 7608.0), 'D6': (7275.0, 7608.0), 'D7': (8525.0, 7608.0), 'D8': (9775.0, 7608.0),
                 'E1': (1025.0, 9499.0), 'E2': (2275.0, 9499.0), 'E3': (3525.0, 9499.0), 'E4': (4775.0, 9499.0),
                 'E5': (6025.0, 9499.0), 'E6': (7275.0, 9499.0), 'E7': (8525.0, 9499.0)}

    #simplePrint(layout_bs, mode="color")
    animateLayout(layout_bs, mode="ascii")
