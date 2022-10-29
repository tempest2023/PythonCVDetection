import cv2
import numpy as np
from debugPrint import debug_print


class DisplayFrame(object):
    """
    a class to display the frames by opencv
    """
    def __init__(self, name, track):
        self.name = name
        self.track = track
    
    async def show(self, lis):
        """
        using cv2 to display the frames
        """
        if(self.track is None):
            debug_print('[DEBUG] track is None', 0)
            return
        # print('[DEBUG] Start to display')
        ticks = 0
        while True:
            # print('[DEBUG] Start to get frame')
            frame = None
            try:
                frame = await self.track.recv()
            except Exception:
                debug_print('[DEBUG] Exception when get frame: ', 0)
                break
            if(frame is None):
                debug_print('[DEBUG] can not get frame', 0)
                break
            ball = frame.to_ndarray(format="bgr24")
            debug_print(f'[DEBUG] put a ball to queue, {ball.shape}')
            
            ticks += 1
            lowBound = np.array([11, 43, 46])  # lower hsv bound for red
            upperBound = np.array([25, 255, 255])  # upper hsv bound to red
            hsv = cv2.cvtColor(ball, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lowBound, upperBound)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            max_contour = contours[0]
            contour = max_contour
            contours_poly = cv2.approxPolyDP(contour, 3, True)
            boundRect = cv2.boundingRect(contours_poly)
            x, y, w, h = boundRect
            cv2.rectangle(ball, (x, y), (x + w, y + h), (0, 255, 0), 4)
            cv2.rectangle(ball, (x, y), (x + w, y + h), (0, 255, 0), 4)
            lis.put(ball)
            # print('[DEBUG] put a ball to queue, ticks: ', ticks)
            cv2.imshow('ball', ball)
        
            key = cv2.waitKey(1) 
            if key == ord('q'):
                break
        cv2.destroyAllWindows()
        debug_print('[DEBUG] Exit displaying')


def display_task(loop, id, track, lis):
    """
    coroutine task to display the track
    """
    print('[DEBUG] display task: ', id)
    df = DisplayFrame(f'display task-{id}', track)
    coro = df.show(lis)
    
    try:
        loop.run_until_complete(coro)
    finally:
        print('[DEBUG] Exit display process: ', id)
    
    