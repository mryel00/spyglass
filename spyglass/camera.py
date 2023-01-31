import libcamera
from picamera2 import Picamera2


def init_camera(
        width: int,
        height: int,
        fps: int,
        autofocus: str,
        lens_position: float,
        autofocus_speed: str,
        flip=False):
    picam2 = Picamera2()

    controls = {'FrameRate': fps}

    if 'AfMode' in picam2.camera_controls:
        controls['AfMode'] = autofocus
        controls['AfSpeed'] = autofocus_speed
        if autofocus == libcamera.controls.AfModeEnum.Manual:
            controls['LensPosition'] = lens_position
    else:
        print('Attached camera does not support autofocus')

    transform = libcamera.Transform(hflip=1, vflip=1) if flip else libcamera.Transform()

    picam2.configure(picam2.create_video_configuration(main={'size': (width, height)}, controls=controls, transform=transform))

    return picam2
