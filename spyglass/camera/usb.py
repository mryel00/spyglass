from . import camera

from spyglass.server import StreamingHandler, StreamingServer
from .. import logger

class USB(camera.Camera):
    def configure(self):
        controls = self.create_controls()

        self.picam2.configure(
            self.picam2.create_preview_configuration(
                main={'size': (self.width, self.height), 'format': 'MJPEG'},
                controls=controls
            )
        )

    def start_and_run_server(self,
            bind_address,
            port,
            stream_url='/stream',
            snapshot_url='/snapshot'):
        class StreamingHandlerUSB(StreamingHandler):
            def get_frame(self):
                #TODO: Cuts framerate in 1/n with n streams open, add some kind of buffer
                return self.output.capture_buffer()
        self.picam2.start()
        self._run_server(
            bind_address,
            port,
            self.picam2,
            StreamingHandlerUSB(),
            stream_url=stream_url,
            snapshot_url=snapshot_url
        )
    
    def stop(self):
        self.picam2.stop()
