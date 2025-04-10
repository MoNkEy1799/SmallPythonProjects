import matplotlib.image as mplim
import matplotlib.pyplot as plt
import numpy as np
import warnings

class Downsampler:
    def __init__(self, filepath: str | None=None, newWidth: int = None, newHeight: int = None) -> None:
        self.newWidth, self.newHeight = newWidth, newHeight
        if filepath is not None:
            self.loadImage(filepath)
            self.height, self.width, _ = self.image.shape
            self.scaling = self._checkParametersForScaling()

    def show(self) -> None:
        plt.imshow(self.downsampled)
        plt.show()

    def loadImage(self, filepath: str) -> None:
        self.image = mplim.imread(filepath)
        self.downsampled = self.image
        self.height, self.width, _ = self.image.shape
        self.scaling = self._checkParametersForScaling()

        if filepath.endswith(".png"):
            self.pixelvalues = 4
            self.normalize = 1
        elif filepath.endswith(".jpg"):
            self.pixelvalues = 3
            self.normalize = 255

    def downsampleImage(self, samplingMethode: str = "sub-sampling") -> None:
        if samplingMethode == "sub-sampling":
            print("Downsampling image with subsampling:")
            self.downsampled = self.subSampling(self.scaling)
        
        elif samplingMethode == "nearest-av":
            print("Downsampling image with nearest neighbour average:")
            self.downsampled = self.boxSampling(self.scaling, [(-1, -1), (-1, 1), (1, -1), (1, 1)])
        
        elif samplingMethode == "box-sampling":
            print("Downsampling image with box sampling:")
            self.downsampled = self.boxSampling(self.scaling)

    def subSampling(self, scaling: float) -> np.ndarray:
        newHeight, newWidth = round(self.height * scaling), round(self.width * scaling)
        newImage = np.zeros((newHeight, newWidth, self.pixelvalues))

        for i in range(newHeight):
            print(f"\rProgress: {i / (newHeight - 1) * 100:.1f}%", end="")
            for j in range(newWidth):
                newImage[i][j] = self.image[round(i / scaling)][round(j / scaling)] / self.normalize
        
        print()
        return newImage
    
    def boxSampling(self, scaling: float, box: list[tuple] | None = None) -> np.ndarray:
        newHeight, newWidth = round(self.height * scaling), round(self.width * scaling)
        newImage = np.zeros((newHeight, newWidth, self.pixelvalues))
        numSamples = int(np.floor(1 / scaling))

        if box is None:
            box = list()
            for nh in range(numSamples):
                for nw in range(numSamples):
                    box.append((int(np.floor(numSamples / 2 - nh)), int(np.floor(numSamples / 2 - nw))))

        for i in range(newHeight):
            print(f"\rProgress: {i / (newHeight - 1) * 100:.1f}%", end="")
            for j in range(newWidth):
                samples = list()
                mainPxl = round(i / scaling), round(j / scaling)
                for n in box:
                    try:
                        samples.append(self.image[mainPxl[0] + n[0]][mainPxl[1] + n[1]])
                    except IndexError:
                        continue
                newImage[i][j] = np.mean(samples, axis=0) / self.normalize
        
        print()
        return newImage
    
    def getBrightnessArray(self) -> np.ndarray:
        return np.mean(self.downsampled[:, :, :3], axis=2)
    
    def getRGBArray(self) -> np.ndarray:
        return self.downsampled[:, :, :3] * 255

    def _checkParametersForScaling(self) -> float:
        if self.newWidth is not None:
            if self.newHeight is not None:
                raise ValueError("Can't downsample image with both newWidth and newHeight given. Please choose 'one' of these options.")
            if self.newWidth > 100:
                warnings.warn("A newWidth of over 100 results in more than 200 characters per line. This might not fit into most default outputs.")
            if self.newWidth > self.width:
                raise ValueError("Can only downsample images: newWidth/newHeight has to be smaller than image width/height.")
            return self.newWidth / self.width

        elif self.newHeight is not None:
            if self.height / self.newHeight * self.width > 100:
                warnings.warn("A resulting width after downsampling of over 100 results in more than 200 characters per line. This might not fit into most default outputs.")
            if self.newHeight > self.height:
                raise ValueError("Can only downsample images: newWidth/newHeight has to be smaller than image width/height.")
            return self.newHeight / self.height

        else:
            if self.width > 100:
                warnings.warn("A image width of over 100 results in more than 200 characters per line. This might not fit into most default outputs.")
            return 1.0