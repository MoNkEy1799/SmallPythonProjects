import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

def _cos(x: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
        return a * np.cos(b * (x - c)) + d

def _connector(x: float, y1: float, y2: float, width: float = 1, color: str = "black") -> None:
    amp = (y1 - y2) / 2
    xrange = np.linspace(x, x+width, 1000)
    plt.plot(xrange, _cos(xrange, amp, np.pi/width, x, y1-amp), c=color, zorder=0)

def _linear(x, a, b):
      return a * x + b

x, y1, y2, width = 0, 2, 0, 3.5
midx, midy = x+width/2, y1-1
xspace = np.array([midx-0.3, midx+0.3])
amp = (y1 - y2) / 2

class Point:
    def __init__(self, x, y) -> None:
          self.x = x
          self.y = y

p1 = Point(midx-0.3, _cos(midx-0.3, amp, np.pi/width, x, y1-amp))
p2 = Point(midx, midy+0.1)
p3 = Point(midx+0.3, _cos(midx+0.3, -amp, np.pi/width, x, y2+amp))
p4 = Point(midx+0.1, midy)
p5 = Point(midx+0.3, _cos(midx+0.3, amp, np.pi/width, x, y1-amp))
p6 = Point(midx, midy-0.1)
p7 = Point(midx-0.3, _cos(midx-0.3, -amp, np.pi/width, x, y2+amp))
p8 = Point(midx-0.1, midy)

_connector(x, y1, y2, width)
_connector(x, y2, y1, width)
plt.plot([p1.x, p2.x], [p1.y, p2.y], c="tab:gray")
plt.plot([p2.x, p3.x], [p2.y, p3.y], c="tab:gray")
plt.plot([p3.x, p4.x], [p3.y, p4.y], c="tab:gray")
plt.plot([p4.x, p5.x], [p4.y, p5.y], c="tab:gray")
plt.plot([p5.x, p6.x], [p5.y, p6.y], c="tab:gray")
plt.plot([p6.x, p7.x], [p6.y, p7.y], c="tab:gray")
plt.plot([p7.x, p8.x], [p7.y, p8.y], c="tab:gray")
plt.plot([p8.x, p1.x], [p8.y, p1.y], c="tab:gray")
alphaCol = tuple([c * 0.3 + 0.7 for c in colors.to_rgba("tab:gray")])
plt.fill([p1.x, p2.x, p3.x, p4.x, p5.x, p6.x, p7.x, p8.x, p1.x], [p1.y, p2.y, p3.y, p4.y, p5.y, p6.y, p7.y, p8.y, p1.y], c=alphaCol)
plt.show()
