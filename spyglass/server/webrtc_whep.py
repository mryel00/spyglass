import uuid
import asyncio

from requests import codes
from aiortc import RTCSessionDescription, RTCPeerConnection, sdp
from aiortc.rtcrtpsender import RTCRtpSender

from spyglass.url_parsing import check_urls_match

# Used for type hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from spyglass.server.http_server import StreamingHandler

pcs: dict[uuid.UUID, RTCPeerConnection] = {}

def send_default_headers(response_code: int, handler: 'StreamingHandler'):
    handler.send_response(response_code)
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Credentials', False)

def do_OPTIONS(handler: 'StreamingHandler'):
    # Adapted from MediaMTX http_server.go
    # https://github.com/bluenviron/mediamtx/blob/main/internal/servers/webrtc/http_server.go#L173-L189
    def response_headers():
        send_default_headers(codes.no_content, handler)
        handler.send_header('Access-Control-Allow-Methods', 'OPTIONS, GET, POST, PATCH, DELETE')
        handler.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, If-Match')

    if handler.headers.get("Access-Control-Request-Method") != None:
        response_headers()
        handler.end_headers()
    elif check_urls_match('/webrtc/whip', handler.path) \
    or check_urls_match('/webrtc/whep', handler.path):
        response_headers()
        handler.send_header('Access-Control-Expose-Headers', 'Link')
        handler.headers['Link'] = get_ICE_servers()
        handler.end_headers()

async def do_POST_async(handler: 'StreamingHandler'):
    # Adapted from MediaMTX http_server.go
    # https://github.com/bluenviron/mediamtx/blob/main/internal/servers/webrtc/http_server.go#L191-L246
    if handler.headers.get("Content-Type") != "application/sdp":
        handler.send_error(codes.bad)
        return
    content_length = int(handler.headers['Content-Length'])
    offer_text = handler.rfile.read(content_length).decode('utf-8')
    offer = RTCSessionDescription(sdp=offer_text, type='offer')

    pc = RTCPeerConnection()
    secret = uuid.uuid4()
    @pc.on('connectionstatechange')
    async def on_connectionstatechange():
        print(f'Connection state {pc.connectionState}')
        if pc.connectionState == 'failed':
            await pc.close()
        elif pc.connectionState == 'closed':
            pcs.pop(str(secret))
            print(f'{len(pcs)} connections still open.')
    pcs[str(secret)] = pc
    sender = pc.addTrack(handler.media_track)
    codecs = RTCRtpSender.getCapabilities('video').codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(
        [codec for codec in codecs if codec.mimeType == 'video/H264']
    )

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    while pc.iceGatheringState != "complete":
        await asyncio.sleep(1)

    send_default_headers(codes.created, handler)

    handler.send_header("Content-Type", "application/sdp")
    handler.send_header("ETag", "*")

    handler.send_header("ID", secret)
    handler.send_header("Access-Control-Expose-Headers", "ETag, ID, Accept-Patch, Link, Location")
    handler.send_header("Accept-Patch", "application/trickle-ice-sdpfrag")
    handler.headers['Link'] = get_ICE_servers()
    handler.send_header("Location", f'/whep/{secret}')
    handler.send_header('Content-Length', len(pc.localDescription.sdp))
    handler.end_headers()
    handler.wfile.write(bytes(pc.localDescription.sdp, 'utf-8'))

async def do_PATCH_async(streaming_handler: 'StreamingHandler'):
    # Adapted from MediaMTX http_server.go
    # https://github.com/bluenviron/mediamtx/blob/main/internal/servers/webrtc/http_server.go#L248-L287
    if len(streaming_handler.path.split('/')) < 3 \
    or streaming_handler.headers.get('Content-Type') != 'application/trickle-ice-sdpfrag':
        send_default_headers(codes.bad, streaming_handler)
        streaming_handler.end_headers()
        return
    content_length = int(streaming_handler.headers['Content-Length'])
    sdp_str = streaming_handler.rfile.read(content_length).decode('utf-8')
    candidates = parse_ice_candidates(sdp_str)
    secret = streaming_handler.path.split('/')[-1]
    pc = pcs[secret]
    for candidate in candidates:
        await pc.addIceCandidate(candidate)

    send_default_headers(codes.no_content, streaming_handler)
    streaming_handler.end_headers()

def get_ICE_servers():
    return None

def parse_ice_candidates(sdp_message):
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

import av

from aiortc import MediaStreamTrack
from picamera2.outputs import Output
from queue import Queue

from fractions import Fraction

class PicameraStreamTrack(MediaStreamTrack, Output):
    kind = "video"
    def __init__(self):
        super().__init__()
        self.img_queue = Queue()

    def outputframe(self, frame, keyframe=True, timestamp=None):
        self.img_queue.put((frame, keyframe, timestamp))

    async def recv(self):
        while self.img_queue.empty():
            await asyncio.sleep(0.02)
        img, keyframe, pts = self.img_queue.get()
        packet = av.packet.Packet(img)
        packet.pts = pts
        packet.time_base = Fraction(1,1000000)
        packet.is_keyframe = keyframe
        return packet
