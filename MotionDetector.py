import numpy as np

import board
import neopixel

from time import sleep
from picamera import PiCamera, array


NUM_PIXELS = 200
MAX_BRIGHTNESS = 0.04


class DetectMotion(array.PiMotionAnalysis):
    def __init__(self, pixels, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pixels = pixels

    def update_pixels(self, *fill_value, show=True):
        self.pixels.fill(fill_value)
        if show: pixels.show()

    def analyze(self, a):
        x = a['x'].astype(np.float)
        y = a['y'].astype(np.float)

        a = x**2 + y**2
        np.sqrt(a, out=a)

        active_pixels = (a > 10).sum()
        print("active pixels", active_pixels, a.max())
        if active_pixels > 2:
            self.update_pixels(255, 0, 0)
        else:
            self.update_pixels(0, 0, 64)


if __name__ == "__main__":
    pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=MAX_BRIGHTNESS, auto_write=False)
    print(pixels.n)
    print(pixels.brightness)
    print(dir(pixels))
    pixels[0] = (255, 0, 0)
    pixels.show()

    with PiCamera() as camera:
        with DetectMotion(pixels, camera) as output:
            try:
                print(camera.resolution)
                camera.resolution = (228, 128)
                print(camera.resolution)
                camera.start_recording('/dev/null', format='h264', motion_output=output)
                camera.wait_recording(90)
            finally:
                camera.stop_recording()
                pixels.fill((0, 0, 0))
                pixels.show()
                sleep(.5)

