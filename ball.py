import numpy as np
import cv2
from av import VideoFrame
from aiortc import VideoStreamTrack
# test deps
import time
import asyncio
from aiortc.contrib.media import MediaRecorder


class BallVideoStreamTrack(VideoStreamTrack):
    """
    A video track that returns a bouncing ball.
    """

    def __init__(self):
        super().__init__()  # don't forget this!
        self.counter = 0
        
        if(not hasattr(self, 'ball')):
            self.initParams()
            # print(f'[DEBUG] init done, position: {(self.x, self.y)}')
        self.frames = []
        # continue to generate animation for 30 frames
        for _ in range(30):
            self.x += self.moveX
            self.y += self.moveY
            if self.y >= self.height - self.radius or self.y <= 0 + self.radius:
                self.moveY = -self.moveY
            if self.x >= self.width - self.radius or self.x <= 0 + self.radius:
                self.moveX = -self.moveX
            self.ball = np.zeros((self.height, self.width, 3), dtype='uint8')
            self.frames.append(
                VideoFrame.from_ndarray(
                    cv2.circle(self.ball, (self.x, self.y), self.radius, self.color, -1), format="bgr24"
                )
            )

    async def recv(self):
        """
        calculate the next frame
        """
        pts, time_base = await self.next_timestamp()
        self.x += self.moveX
        self.y += self.moveY
        if self.y >= self.height - self.radius or self.y <= 0 + self.radius:
            self.moveY = -self.moveY
        if self.x >= self.width - self.radius or self.x <= 0 + self.radius:
            self.moveX = -self.moveX
        self.ball = np.zeros((self.height, self.width, 3), dtype='uint8')
        frame = VideoFrame.from_ndarray(cv2.circle(self.ball, (self.x, self.y), self.radius, self.color, -1), format="bgr24")
        frame.pts = pts
        frame.time_base = time_base
        return frame
    
    def initParams(self):
        """
        init the params of the ball, screen height, screen width, initial position, radius, color, move speed
        """
        self.height, self.width = 480, 640
        self.ball = np.zeros((self.height, self.width, 3), dtype='uint8')
        self.radius = 20
        # random start point
        x, y = np.random.rand(2)
        x = int(x * (self.width - 2 * self.radius)) + self.radius
        y = int(y * (self.height - 2 * self.radius)) + self.radius
        self.x = x
        self.y = y
        
        # orange ball BGR format
        self.color = (1, 181, 255)
        # move speed
        self.moveX = 15
        self.moveY = 15


# test part
async def addTrackToRecord(recorder, duration):
    """
    record the video for duration seconds
    """
    recorder.addTrack(BallVideoStreamTrack())
    await recorder.start()
    await asyncio.sleep(duration)
    await recorder.stop()


if __name__ == "__main__":
    recorder = MediaRecorder('ball.mp4')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(addTrackToRecord(recorder, 10))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(recorder.stop())
