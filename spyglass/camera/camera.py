from abc import ABC, abstractmethod
from picamera2 import Picamera2
import libcamera
from .. import logger
from ..exif import create_exif_header
from ..server import StreamingServer, StreamingHandler

class Camera(ABC):
    def __init__(self,
            picam2: Picamera2,
            width: int,
            height: int,
            fps: int,
            autofocus: str,
            lens_position: float,
            autofocus_speed: str):

        self.picam2 = picam2
        self.width = width
        self.height = height
        self.fps = fps
        self.autofocus = autofocus
        self.lens_position = lens_position
        self.autofocus_speed = autofocus_speed

    def create_controls(self):
        controls = {}

        if 'FrameRate' in self.picam2.camera_controls:
            controls['FrameRate'] = self.fps

        if 'AfMode' in self.picam2.camera_controls:
            controls['AfMode'] = self.autofocus
            controls['AfSpeed'] = self.autofocus_speed
            if self.autofocus == libcamera.controls.AfModeEnum.Manual:
                controls['LensPosition'] = self.lens_position
        else:
            print('Attached camera does not support autofocus')

        return controls

    def _run_server(self,
            bind_address,
            port,
            streaming_handler: StreamingHandler,
            get_frame,
            stream_url='/stream',
            snapshot_url='/snapshot',
            orientation_exif=0):
        logger.info('Server listening on %s:%d', bind_address, port)
        logger.info('Streaming endpoint: %s', stream_url)
        logger.info('Snapshot endpoint: %s', snapshot_url)
        logger.info('Controls endpoint: %s', '/controls')
        address = (bind_address, port)
        streaming_handler.picam2 = self.picam2
        streaming_handler.get_frame = get_frame
        streaming_handler.stream_url = stream_url
        streaming_handler.snapshot_url = snapshot_url
        if orientation_exif > 0:
            streaming_handler.exif_header = create_exif_header(orientation_exif)
        else:
            streaming_handler.exif_header = None
        current_server = StreamingServer(address, streaming_handler)
        current_server.serve_forever()

    @abstractmethod
    def configure(self,
                  control_list: list[list[str]]=[],
                  upsidedown=False,
                  flip_horizontal=False,
                  flip_vertical=False):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def start_and_run_server(self,
            bind_address,
            port,
            stream_url='/stream',
            snapshot_url='/snapshot',
            orientation_exif=0):
        pass
