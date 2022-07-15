import numpy as np

import board
import neopixel

from time import sleep, time
from picamera import PiCamera, array


NUM_PIXELS = 200
MAX_BRIGHTNESS = 0.08


class DetectMotion(array.PiMotionAnalysis):
    def __init__(self, pixels, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pixels = pixels
        self.timer = time()

    def update_pixels(self, array, show=True):
        n = array.shape[0]

        for i in range(NUM_PIXELS):
            if i % 2: continue  # only every other
            j = int(n * i/NUM_PIXELS)
            r, g, b = array[j]

            r = max(r, int(pixels[i][0] * .65))
            g = max(g, int(pixels[i][1] * .55))
            b = max(b, int(pixels[i][2] * .4))

            pixels[i] = r, g, b

        if show:
            pixels.show()

    def update(self, a):
        a = a['x'].astype(np.float)**2 + a['y'].astype(np.float)**2
        np.sqrt(a, out=a)

        a = a.sum(axis=0)

        a = np.convolve(a, np.full(4, .25))
        a[1:] *= a[:-1]
        a[:-1] *= a[1:]

        # normalize a, but if max(a) is small, let it stay small
        _max = a.max()
        _max = max(2048, _max)
        t = time()
        print(
            str(round(t - self.timer, 4)).ljust(6),
            str(int(_max)).rjust(16),
            end=' '
        )
        self.timer = t
        a /= _max

        return a

    def analyze(self, a):
        a = self.update(a)

        if 1:
            rgb = a * 255
            np.clip(rgb, 0, 255)
            rgb = rgb.astype(np.uint8)
            rgb = np.stack((rgb, rgb, rgb), axis=1)
            self.update_pixels(rgb)

        if 1:
            disp = map(str, (10*a - 1e-4).astype(int)) # 0-9 squeeze
            disp = ' '.join(disp).replace('0', ' ')  # leave 0's blank
            print(disp, '\t')


if __name__ == "__main__":
    pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=MAX_BRIGHTNESS, auto_write=False)
    print(pixels.n)
    print(pixels.brightness)
    print(dir(pixels))
    pixels[0] = (255, 0, 0)
    pixels.show()

    with PiCamera() as camera:
        camera.hflip = True
        with DetectMotion(pixels, camera) as output:
            try:
                #camera.resolution = (640, 480)
                camera.resolution = (228*2, 128*2)
                camera.start_recording(
                    '/dev/null', format='h264', motion_output=output,
                )
                camera.wait_recording(90)
                while True: camera.wait_recording()
            finally:
                camera.stop_recording()
                pixels.fill((0, 0, 0))
                pixels.show()
                sleep(.5)

