import io
import libcamera

from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
from threading import Condition

from . import camera
from ..server import StreamingHandler
from ..camera_options import process_controls

class CSI(camera.Camera):
    def configure(self,
                  control_list: list[list[str]]=[],
                  flip_horizontal=False,
                  flip_vertical=False,
                  upsidedown=False):
        controls = self.create_controls()
        c = process_controls(self.picam2, [tuple(ctrl) for ctrl in control_list])
        controls.update(c)

        transform = libcamera.Transform(
            hflip=int(flip_horizontal or upsidedown),
            vflip=int(flip_vertical or upsidedown)
        )

        self.picam2.configure(
            self.picam2.create_video_configuration(
                main={'size': (self.width, self.height)},
                controls=controls,
                transform=transform
            )
        )

    def start_and_run_server(self,
            bind_address,
            port,
            stream_url='/stream',
            snapshot_url='/snapshot',
            orientation_exif=0):
        
        class StreamingOutput(io.BufferedIOBase):
            def __init__(self):
                self.frame = None
                self.condition = Condition()

            def write(self, buf):
                with self.condition:
                    self.frame = buf
                    self.condition.notify_all()
        output = StreamingOutput()
        self.picam2.start_recording(MJPEGEncoder(), FileOutput(output))
        self._run_server(
            bind_address,
            port,
            output,
            StreamingHandler(),
            stream_url=stream_url,
            snapshot_url=snapshot_url,
            orientation_exif=orientation_exif
        )

    def stop(self):
        self.picam2.stop_recording()
