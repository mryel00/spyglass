#!/usr/bin/python3

import argparse
import io
import logging
import re
import socketserver
import libcamera
from http import server
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def split_resolution(res):
    parts = res.split('x')
    w = int(parts[0])
    h = int(parts[1])
    return w, h


def resolution_type(arg_value, pat=re.compile(r"^\d+x\d+$")):
    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("invalid value: <width>x<height> expected.")
    return arg_value


parser = argparse.ArgumentParser(
    prog='Spyglass',
    description='Start a webserver for Picamera2 videostreams.'
)
parser.add_argument('-b', '--bindaddress', type=str, default='', help='Bind to address for incoming connections')
parser.add_argument('-p', '--port', type=int, default=8080, help='Bind to port for incoming connections')
parser.add_argument('-r', '--resolution', type=resolution_type, default='640x480', help='Resolution of the images width x height')
parser.add_argument('-f', '--fps', type=int, default=15, help='Frames per second to capture')

args = parser.parse_args()
bind_address = args.bindaddress
port = args.port
width, height = split_resolution(args.resolution)
fps = args.fps

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (width, height)}, controls={"FrameRate": (fps, fps), "AfMode": libcamera.controls.AfModeEnum.Continuous}))
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    address = (bind_address, port)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()
