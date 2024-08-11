#!/usr/bin/python3

import logging
import socketserver
from http import server
import time
import uuid
import asyncio
import logging
import socketserver
from requests import codes
from http import server
from spyglass.url_parsing import check_urls_match, get_url_params
from spyglass.camera_options import parse_dictionary_to_html_page, process_controls
from aiortc import RTCSessionDescription, RTCPeerConnection, RTCIceCandidate, sdp

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

class StreamingHandler(server.BaseHTTPRequestHandler):
    pcs: dict[uuid.UUID, RTCPeerConnection] = {}
    loop = asyncio.new_event_loop()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.picam2 = None
        self.media_track = None
        self.exif_header = None
        self.stream_url = None
        self.snapshot_url = None
        self.get_frame = None

    def do_GET(self):
        if check_urls_match(self.stream_url, self.path):
            self.start_streaming()
        elif check_urls_match(self.snapshot_url, self.path):
            self.send_snapshot()
        elif check_urls_match('/controls', self.path):
            parsed_controls = get_url_params(self.path)
            parsed_controls = parsed_controls if parsed_controls else None
            processed_controls = process_controls(self.picam2, parsed_controls)
            self.picam2.set_controls(processed_controls)
            content = parse_dictionary_to_html_page(self.picam2, parsed_controls, processed_controls).encode('utf-8')
            self.send_response(codes.ok)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif check_urls_match('/webrtc', self.path):
            pass
        else:
            self.send_error(codes.not_found)
            self.end_headers()

    def do_OPTIONS(self):
        def response_headers():
            self.send_response(codes.no_content)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Credentials', False)
            self.send_header('Access-Control-Allow-Methods', 'OPTIONS, GET, POST, PATCH, DELETE')
            self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, If-Match')

        if self.headers.get("Access-Control-Request-Method") != None:
            response_headers()
            self.end_headers()
        elif check_urls_match('/whip', self.path) or check_urls_match('/whep', self.path):
            response_headers()
            self.send_header('Access-Control-Expose-Headers', 'Link')
            self.headers['Link'] = self.get_ICE_servers()
            self.end_headers()

    def do_POST(self):
        async def post():
            if self.headers.get("Content-Type") != "application/sdp":
                self.send_error(codes.bad)
                return
            content_length = int(self.headers['Content-Length'])
            offer_text = self.rfile.read(content_length).decode('utf-8')
            offer = RTCSessionDescription(sdp=offer_text, type='offer')

            pc = RTCPeerConnection()
            secret = uuid.uuid4()
            @pc.on('iceconnectionstatechange')
            async def on_iceconnectionstatechange():
                print(f'ICE connection state {pc.iceConnectionState}')
            @pc.on('connectionstatechange')
            async def on_connectionstatechange():
                print(f'Connection state {pc.connectionState}')
                if pc.connectionState == "failed":
                    await pc.close()
                    StreamingHandler.pcs.pop(str(secret))
            StreamingHandler.pcs[str(secret)] = pc
            pc.addTrack(self.media_track)

            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            while pc.iceGatheringState != "complete":
                await asyncio.sleep(1)

            self.send_response(codes.created)
            self.send_header("Content-Type", "application/sdp")
            self.send_header("ETag", "*")
            
            self.send_header("ID", secret)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Credentials', False)
            self.send_header("Access-Control-Expose-Headers", "ETag, ID, Accept-Patch, Link, Location")
            self.send_header("Accept-Patch", "application/trickle-ice-sdpfrag")
            self.headers['Link'] = self.get_ICE_servers()
            self.send_header("Location", f'/whep/{secret}')
            self.end_headers()
            self.wfile.write(bytes(answer.sdp, 'utf-8'))
            while pc.connectionState != 'connected' or pc.connectionState != 'closed':
                await asyncio.sleep(10)
                print(StreamingHandler.pcs)
        asyncio.run(post())
    
    def do_PATCH(self):
        async def patch():
            if len(self.path.split('/')) < 3 or self.headers.get('Content-Type') != 'application/trickle-ice-sdpfrag':
                self.send_response(codes.bad)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Credentials', False)
                self.end_headers()
                return
            content_length = int(self.headers['Content-Length'])
            sdp_str = self.rfile.read(content_length).decode('utf-8')
            candidates = self.parse_ice_candidates(sdp_str)
            secret = self.path.split('/')[-1]
            pc = StreamingHandler.pcs[secret]
            for candidate in candidates:
                await pc.addIceCandidate(candidate)

            self.send_response(codes.no_content)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Credentials', False)
            self.end_headers()
            while pc.connectionState != 'connected' or pc.connectionState != 'closed':
                await asyncio.sleep(10)
        asyncio.run(patch())

    def start_streaming(self):
        try:
            self.send_response(codes.ok)
            self.send_default_headers()
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            while True:
                frame = self.get_frame()
                self.wfile.write(b'--FRAME\r\n')
                if self.exif_header is None:
                    self.send_jpeg_content_headers(frame)
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
                else:
                    self.send_jpeg_content_headers(frame, len(self.exif_header) - 2)
                    self.end_headers()
                    self.wfile.write(self.exif_header)
                    self.wfile.write(frame[2:])
                    self.wfile.write(b'\r\n')
        except Exception as e:
            logging.warning('Removed streaming client %s: %s', self.client_address, str(e))

    def send_snapshot(self):
        try:
            self.send_response(codes.ok)
            self.send_default_headers()
            frame = self.get_frame()
            if self.exif_header is None:
                self.send_jpeg_content_headers(frame)
                self.end_headers()
                self.wfile.write(frame)
            else:
                self.send_jpeg_content_headers(frame, len(self.exif_header) - 2)
                self.end_headers()
                self.wfile.write(self.exif_header)
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
        self.send_header('Content-Length', str(len(frame) + extra_len))

    def get_ICE_servers(self):
        return None

    def parse_ice_candidates(self, sdp_message):
        sdp_message = sdp_message.replace('\\r\\n', '\r\n')

        lines = sdp_message.splitlines()

        candidates = []
        cand_str = 'a=candidate:'
        mid_str = 'a=mid:'
        mid = ''
        for line in lines:
            if line.startswith(mid_str):
                mid = line[len(mid_str):]
            elif line.startswith(cand_str):
                candidate_str = line[len(cand_str):]
                candidate = sdp.candidate_from_sdp(candidate_str)
                candidate.sdpMid = mid
                candidates.append(candidate)
        return candidates
