from time import sleep

import mss
import mss.tools


with mss.mss() as sct:
    # The screen part to capture
    i = 100
    while(True):
        sleep(5)
        monitor = {"top": 130, "left": 175, "width": 1620, "height": 890,"numer":i}
        output = "sct-{top}x{left}_{width}x{height}{numer}.png".format(**monitor)
        i += 1
        # Grab the data
        sct_img = sct.grab(monitor)

        # Save to the picture file
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
        print(output)