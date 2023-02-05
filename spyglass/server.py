import io
import logging
import socketserver
from http import server
from threading import Condition
from . import logger


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def run_server(bind_address, port, output, stream_url='/stream', snapshot_url='/snapshot'):
    class StreamingHandler(server.BaseHTTPRequestHandler):        
        def do_GET(self):
            if self.path == stream_url:
                self.start_streaming()
            elif self.path == snapshot_url:
                self.send_snapshot()
            else:
                self.send_error(404)
                self.end_headers()

        def start_streaming(self):
            try:
                self.send_response(200)
                self.send_default_headers()
                self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
                self.end_headers()
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_jpeg_content_headers(frame)
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))

        def send_snapshot(self):
            try:
                self.send_response(200)
                self.send_default_headers()
                with output.condition:
                    output.condition.wait()
                    frame = output.frame
                self.send_jpeg_content_headers(frame)
                self.end_headers()
                self.wfile.write(frame)
            except Exception as e:
                logging.warning(
                    'Removed client %s: %s',
                    self.client_address, str(e))

        def send_default_headers(self):
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')

        def send_jpeg_content_headers(self, frame):
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', len(frame))

    logger.info('Server listening on %s:%d', bind_address, port)
    logger.info('Streaming endpoint: %s', stream_url)
    logger.info('Snapshot endpoint: %s', snapshot_url)
    address = (bind_address, port)
    current_server = StreamingServer(address, StreamingHandler)
    current_server.serve_forever()
