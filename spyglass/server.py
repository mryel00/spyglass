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


def run_server(bind_address, port, output, stream_url='/stream', snapshot_url='/snapshot', orientation_exif = 0):
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
                    if orientation_exif <= 0:
                        self.send_jpeg_content_headers(frame)
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
                    else:
                        exif_header = self.get_orientation_exif_header(orientation_exif)
                        self.send_jpeg_content_headers(frame, len(exif_header)-2)
                        self.end_headers()
                        self.wfile.write(exif_header)
                        self.wfile.write(frame[2:])
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
                if orientation_exif <= 0:
                    self.send_jpeg_content_headers(frame)
                    self.end_headers()
                    self.wfile.write(frame)
                else:
                    exif_header = self.get_orientation_exif_header(orientation_exif)
                    self.send_jpeg_content_headers(frame, len(exif_header)-2)
                    self.end_headers()
                    self.wfile.write(exif_header)
                    self.wfile.write(frame[2:])
            except Exception as e:
                logging.warning(
                    'Removed client %s: %s',
                    self.client_address, str(e))

        def send_default_headers(self):
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')

        def send_jpeg_content_headers(self, frame, extra_len=0):
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', len(frame)+extra_len)

        def get_orientation_exif_header(self, orientation_exif):
            return b''.join([
                    b'\xFF\xD8\xFF\xE1\x00\x62\x45\x78\x69\x66\x00\x00\x4D\x4D\x00\x2A',
                    b'\x00\x00\x00\x08\x00\x05\x01\x12\x00\x03\x00\x00\x00\x01\x00',
                    (orientation_exif).to_bytes(1, 'big'),
                    b'\x00\x00\x01\x1A\x00\x05\x00\x00\x00\x01\x00\x00\x00\x4A\x01\x1B',
                    b'\x00\x05\x00\x00\x00\x01\x00\x00\x00\x52\x01\x28\x00\x03\x00\x00',
                    b'\x00\x01\x00\x02\x00\x00\x02\x13\x00\x03\x00\x00\x00\x01\x00\x01',
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x48\x00\x00\x00\x01\x00\x00',
                    b'\x00\x48\x00\x00\x00\x01'])

    logger.info('Server listening on %s:%d', bind_address, port)
    logger.info('Streaming endpoint: %s', stream_url)
    logger.info('Snapshot endpoint: %s', snapshot_url)
    address = (bind_address, port)
    current_server = StreamingServer(address, StreamingHandler)
    current_server.serve_forever()
