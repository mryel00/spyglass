from .camera import Camera
from .csi import CSI
from .usb import USB

from picamera2 import Picamera2

def init_camera(
        width: int,
        height: int,
        fps: int,
        autofocus: str,
        lens_position: float,
        autofocus_speed: str,
        camera_num: int) -> Camera:

    picam2 = Picamera2(camera_num)
    if picam2._is_rpi_camera():
        cam = CSI(width, height, fps, autofocus, lens_position, autofocus_speed)
    else:
        cam = USB(width, height, fps, autofocus, lens_position, autofocus_speed)
    cam.configure()
    return cam
