from abc import ABC, abstractmethod
from picamera2 import Picamera2
from .. import logger
from .. server import StreamingServer, StreamingHandler

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
        controls = {'FrameRate': self.fps}

        if 'AfMode' in self.picam2.camera_controls:
            controls['AfMode'] = self.autofocus
            controls['AfSpeed'] = self.autofocus_speed
            if self.autofocus == self.libcamera.controls.AfModeEnum.Manual:
                controls['LensPosition'] = self.lens_position
        else:
            print('Attached camera does not support autofocus')

        return controls

    def _run_server(self,
            bind_address,
            port,
            output,
            streaming_handler: StreamingHandler,
            stream_url='/stream',
            snapshot_url='/snapshot'):
        logger.info('Server listening on %s:%d', bind_address, port)
        logger.info('Streaming endpoint: %s', stream_url)
        logger.info('Snapshot endpoint: %s', snapshot_url)
        address = (bind_address, port)
        streaming_handler.output = output
        streaming_handler.stream_url = stream_url
        streaming_handler.snapshot_url = snapshot_url
        current_server = StreamingServer(address, streaming_handler)
        current_server.serve_forever()

    @abstractmethod
    def configure(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def start_and_run_server(self,
            bind_address,
            port,
            stream_url='/stream',
            snapshot_url='/snapshot'):
        pass
