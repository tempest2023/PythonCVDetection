import asyncio
import argparse
import time
from debugPrint import debug_print, pr_green
from ball import BallVideoStreamTrack

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling
from aiortc.contrib.media import MediaBlackhole


time_start = None


def current_stamp():
    """
    get current time stamp based on first request
    minus the first request tiem stamp
    """
    global time_start

    if time_start is None:
        time_start = time.time()
        return 0
    else:
        return int((time.time() - time_start) * 1000000)


async def handle_signaling(pc, signaling, recorder):
    """
    handle the signaling message for server side
    """
    while True:
        obj = await signaling.receive()
        debug_print(f'[SERVER] receive obj RTCSessionDescription: {isinstance(obj, RTCSessionDescription)}, IceCandidate: {isinstance(obj, RTCIceCandidate)} ')
        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            await recorder.start()
            debug_print(f'[SERVER] obj type: {obj.type}')
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        elif obj is BYE:
            debug_print('[SERVER] Exiting')
            break
        else:
            debug_print(f'[SERVER] unexcepted obj: {obj}')
            break


async def server_handler(pc, signaling, recorder):
    '''
    offer the image frames to client
    pc: peer connection
    signaling: TCP Socket Signaling
    recorder: a MediaBlackhole object
    '''
    await signaling.connect()
    ball_track = BallVideoStreamTrack()
    debug_print(ball_track)
    channel = pc.createDataChannel('compution')
    debug_print('[SERVER] Created data channel: compution', 2)
    
    @pc.on('track')
    def on_track(track):
        # discard video stream from client, if has
        recorder.addTrack(track)
        
        @track.on('ended')
        async def on_ended():
            recorder.stop()

    @channel.on('open')
    def on_open():
        msg = f'image {current_stamp()}'
        debug_print(f'[CHANNEL] Send Message: {msg}', 1)
        channel.send(msg)
    
    @channel.on('message')
    def on_message(message):
        debug_print(f'[CHANNEL] Received message: {message}')
        if isinstance(message, str) and message.startswith('value'):
            messageValues = message.strip().split(' ')
            predictedX = float(messageValues[1])
            predictedY = float(messageValues[2])
            # print result, not debug print, necessary
            pos_error = (round(abs(predictedX - ball_track.x), 2), round(abs(predictedY - ball_track.y), 2))
            pr_green(f'[RESULT] Prediction Position: ({predictedX}, {predictedY}), Real Position: ({ball_track.x}, {ball_track.y}), Error: ({pos_error[0]}, {pos_error[1]})')
            msg = f'image {current_stamp()}'
            debug_print(f'[CHANNEL] Send Message: {msg}', 1)
            channel.send(msg)

    # send media track
    pc.addTrack(ball_track)
    await pc.setLocalDescription(await pc.createOffer())
    await signaling.send(pc.localDescription)
    debug_print('[SERVER] send tracks to the client')

    await handle_signaling(pc, signaling, recorder)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='signaling parser')
    
    # set default value for arguments, which is what we need to setup TcpSignaling
    parser.add_argument('--signaling', type=str, default='tcp-socket', help='tcp socket')
    parser.add_argument('--signaling_host', type=str, default='127.0.0.1', help='host')
    parser.add_argument('--signaling_port', type=str, default='8080', help='port')
    
    args = parser.parse_args()
    
    # create tcp socket signaling
    sig = create_signaling(args)
    # create peer connection
    pc = RTCPeerConnection()
    # create a recorder to discard the media stream
    recorder = MediaBlackhole()
    
    debug_print(f'[SERVER] Setup Socket at {args.signaling_host}:{args.signaling_port}', 2)
    
    server_task = server_handler(pc, sig, recorder)
    
    # run event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(server_task)
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())
        loop.run_until_complete(sig.close())


    

