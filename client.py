import argparse
import asyncio
import time
import multiprocessing as mp
from debugPrint import debug_print
from recognition import recognitionTask
from displayFrame import DisplayFrame
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import BYE, create_signaling


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


async def handle_signaling(pc, signaling):
    """
    handle the signaling message for client side
    """
    while True:
        obj = await signaling.receive()
        debug_print(f'[CLIENT] Receive obj RTCSessionDescription: {isinstance(obj, RTCSessionDescription)}, IceCandidate: {isinstance(obj, RTCIceCandidate)} ')
        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            # client repsonse to server
            debug_print(f'[CLIENT] obj type: {obj.type}')
            # reply to server
            if obj.type == 'offer':
                await pc.setLocalDescription(await pc.createAnswer())
                await signaling.send(pc.localDescription)
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        elif obj is BYE:
            debug_print('Exiting')
            break
        else:
            debug_print(f'Unexpected obj {obj}')
            break


async def print_pos(ballPosX, ballPosY):
    """
    For test
    Use coroutine to print the ball position
    """
    while(True):
        print('[DEBUG] Process value ball position: ', ballPosX.value, ballPosY.value)
        await asyncio.sleep(0.5)


async def answer_handler(pc, signaling, lis, ballPosX, ballPosY):
    '''
    answer the message from server and reply
    pc: peer connection
    signaling: TCP Socket Signaling
    lis: a multiprocessing queue to transfer the ball track
    ballPosX: a multiprocessing Value to transfer the ball position X
    ballPosY: a multiprocessing Value to transfer the ball position Y
    '''
    await signaling.connect()
    
    @pc.on('track')
    async def on_track(track):
        debug_print(f'[CLIENT] Receiving {track.kind}, {str(track)}')
        # init a display object to create display task
        df = DisplayFrame('display task-1', track)
        # using cv2 to display the images
        await df.show(lis)

    @pc.on('datachannel')
    def on_datachannel(channel):
        debug_print('[CHANNEL] Data Channel is created by remote server.')

        @channel.on('message')
        def on_message(message):
            debug_print(f'[CHANNEL] Received message: {message}')
            if isinstance(message, str) and message.startswith('image'):
                # reply
                msg = f'value {round(ballPosX.value, 2)} {round(ballPosY.value, 2)} time {current_stamp()}'
                debug_print(f'[CHANNEL] Send Message: {msg}', 1)
                channel.send(msg)
    
    await handle_signaling(pc, signaling)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='signaling parser')
    # set default value for arguments, which is what we need to setup TcpSignaling
    parser.add_argument('--signaling', type=str, default='tcp-socket', help='tcp socket')
    parser.add_argument('--signaling_host', type=str, default='127.0.0.1', help='host')
    parser.add_argument('--signaling_port', type=str, default='8080', help='port')
    
    args = parser.parse_args()
    
    # start a new thread to handle ball recognition
    mp.set_start_method('spawn')
    lis = mp.Queue(300)  # 10s of frames
    ballPosX = mp.Value('d', 0.0)
    ballPosY = mp.Value('d', 0.0)
    recognitionProcess = mp.Process(target=recognitionTask, args=(lis, ballPosX, ballPosY))
    recognitionProcess.start()
    
    sig = create_signaling(args)
    pc = RTCPeerConnection()
    # recorder = MediaRecorder('images/ball-%3d.png')
    server_task = answer_handler(pc, sig, lis, ballPosX, ballPosY)
    # print_task = print_pos(ballPosX, ballPosY)
    # main = asyncio.gather(server_task, print_task)
    main = asyncio.gather(server_task)
    # run event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main)
        recognitionProcess.join()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())
        loop.run_until_complete(sig.close())
        loop.close()