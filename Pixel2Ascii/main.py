from pxl2ascii import PXL2ASCII
from downsampler import Downsampler

ds = Downsampler(filepath="test_pictures/forest.jpg", newWidth=500)
ds.downsampleImage(samplingMethode="box-sampling")
ds.show()

ds.newWidth = None
ds.newHeight = None
ds.loadImage(filepath="test_pictures/dino.png")
p2a = PXL2ASCII(asciiMask=" #._")
p2a.convertRGBToAscii(rgbArray=ds.getRGBArray())
p2a.show()
