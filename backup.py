import numpy as np

import board
import neopixel

from time import sleep
from picamera import PiCamera, array


NUM_PIXELS = 96
MAX_BRIGHTNESS = 0.02


class DetectMotion(array.PiMotionAnalysis):
    def __init__(self, pixels, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pixels = pixels

    def update_pixels(self, array, show=True):
        n = array.shape[0]

        for i in range(NUM_PIXELS):
            if i % 2: continue  # only every other
            j = int(n * i/NUM_PIXELS)
            rgb = array[j]
            pixels[i] = rgb

        if show:
            pixels.show()

    def update(self, a):
        a = np.sqrt(a['x'].astype(np.float)**2 + a['y'].astype(np.float)**2)
        #a = a['x'].astype(np.float)**2

        a = a.sum(axis=0)

        #a = a[1:] * a[:-1]
        a = np.convolve(a, np.ones(4))

        return a

    def analyze(self, a):
        a = self.update(a)

        _max = a.max()
        if _max: a /= _max

        if 1:
            rgb = a * 255
            np.clip(rgb, 0, 255)
            rgb = rgb.astype(np.uint8)
            z = np.zeros_like(rgb)
            rgb = np.stack((rgb, z, z), axis=1)
            self.update_pixels(rgb)
        if 1:
            disp = map(str, (10*a - 1e-4).astype(int)) # 0-9 squeeze
            disp = ' '.join(disp).replace('0', ' ')  # leave 0's blank
            print(disp)


if __name__ == "__main__":
    pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=MAX_BRIGHTNESS, auto_write=False)
    print(pixels.n)
    print(pixels.brightness)
    print(pixels.write)
    print(dir(pixels))
    pixels[0] = (255, 0, 0)
    pixels.show()
    sleep(2)

    with PiCamera() as camera:
        with DetectMotion(pixels, camera) as output:
            try:
                camera.resolution = (640, 480)
                camera.start_recording(
                      '/dev/null', format='h264', motion_output=output)
                camera.wait_recording(30)
            finally:
                camera.stop_recording()

