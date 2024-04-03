import io

from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
from threading import Condition

from . import camera
from .. server import StreamingHandler

class CSI(camera.Camera):
    def configure(self):
        controls = self.create_controls()

        self.picam2.configure(
            self.picam2.create_video_configuration(
                main={'size': (self.width, self.height)},
                controls=controls
            )
        )

    def start_and_run_server(self,
            bind_address,
            port,
            stream_url='/stream',
            snapshot_url='/snapshot'):
        
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
            snapshot_url=snapshot_url
        )

    def stop(self):
        self.picam2.stop_recording()
