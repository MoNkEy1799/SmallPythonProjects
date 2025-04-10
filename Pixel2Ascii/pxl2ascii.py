class PXL2ASCII:
    def __init__(self, asciiMask: str | list[str] | dict | None = None) -> None:
        if asciiMask is None:
            self.converter = {}
        else:
            self.converter = self.getAsciiConverter(asciiMask)

    def convertBrightnessToAscii(self, brightnessArray: list[list[int]]) -> str:
        asciiImage = ""
        for i in range(len(brightnessArray)):
            for j in range(len(brightnessArray[0])):
                for cap in self.converter:
                    if brightnessArray[i][j] >= cap:
                        asciiImage += f"{self.converter[cap]} "
                        break
            asciiImage += "\n"
        
        return asciiImage
    
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

    def getAsciiConverter(self, asciiMask: str | list[str] | dict) -> dict:
        if isinstance(asciiMask, str) or isinstance(asciiMask, list):
            return dict([(1 - (i + 1) / len(asciiMask), char) for i, char in enumerate(asciiMask)])

        elif isinstance(asciiMask, dict):
            return asciiMask
    
    @staticmethod
    def clearLines(n: int = 0):
        LINE_UP = "\033[1A"
        LINE_CLEAR = "\x1b[2K"
        for _ in range(n):
            print(LINE_UP, end=LINE_CLEAR)

    def show(self, prefix: str = "", end: str = "\n") -> None:
        #self.clearLines(len(self.asciiImage.split("\n")[0]))
        print(f"{prefix}{self.asciiImage}", end=end)