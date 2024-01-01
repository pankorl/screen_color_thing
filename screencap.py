import win32gui
import win32ui
import win32con
import numpy as np
from PIL import Image
import cv2

def capture_screen(window_name, w, h, scale_factor=0.05):
    hwnd = win32gui.GetDesktopWindow()
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (w, h), dcObj, (0, 0), win32con.SRCCOPY)
    
    bmpinfo = dataBitMap.GetInfo()
    bmpstr = dataBitMap.GetBitmapBits(True)

    img = np.frombuffer(bmpstr, dtype='uint8')
    img.shape = (h, w, 4)

    # Scale down the image using the scale factor
    # It's more efficient to do this on the numpy array before converting to a PIL Image
    scaled_h = int(h * scale_factor)
    scaled_w = int(w * scale_factor)
    img = cv2.resize(img, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)

    # Flip the image vertically with [::-1]
    # Convert BGR to RGB by using img[:, :, (2, 1, 0)]
    screenshot = Image.fromarray(img[::-1, :, (2, 1, 0)], 'RGB')

    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

    return screenshot

# Usage example:
# screenshot = capture_screen("Your Window Name", 1920, 1080, scale_factor=0.1)
# screenshot.show()  # Or save it with screenshot.save("s
