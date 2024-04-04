from .camera import Camera
from .csi import CSI
from .usb import USB

from picamera2 import Picamera2

def init_camera(
        camera_num: int,
        width: int,
        height: int,
        fps: int,
        autofocus: str,
        lens_position: float,
        autofocus_speed: str,
        upsidedown=False,
        flip_horizontal=False,
        flip_vertical=False,
        control_list: list[list[str]]=[],
        tuning_filter=None,
        tuning_filter_dir=None
        ) -> Camera:
    tuning = None

    if tuning_filter:
        params = {'tuning_file': tuning_filter}
        if tuning_filter_dir:
            params['dir'] = tuning_filter_dir
        tuning = Picamera2.load_tuning_file(**params)

    picam2 = Picamera2(camera_num, tuning=tuning)
    if picam2._is_rpi_camera():
        cam = CSI(width, height, fps, autofocus, lens_position, autofocus_speed)
    else:
        cam = USB(width, height, fps, autofocus, lens_position, autofocus_speed)
    cam.configure(control_list, upsidedown, flip_horizontal, flip_vertical)
    return cam
