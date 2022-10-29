import cv2
import numpy as np
import asyncio
from debugPrint import debug_print


def getBallContours(ball):
    """
    recognize the position of the ball using cv2.findContours
    """
    lowBound = np.array([11, 43, 46])  # lower hsv bound for red
    upperBound = np.array([25, 255, 255])  # upper hsv bound to red
    hsv = cv2.cvtColor(ball, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lowBound, upperBound)
    # get the contours[0]
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = contours[0]
    contour = max_contour
    contours_poly = cv2.approxPolyDP(contour, 3, True)
    # boundRect = cv2.boundingRect(contours_poly)
    # x, y, w, h = boundRect
    # cv2.rectangle(ball, (x, y), (x + w, y + h), (0, 255, 0), 4)
    centers, radius = cv2.minEnclosingCircle(contours_poly)
    # print('[DEBUG] recognize: ', centers, radius)
    return centers


async def findBall(q, ballPosX, ballPosY):
    """
    coroutine task to find the position of the ball, and update it to the multiprocess Value
    """
    ticks = 0
    while(True):
        # print('[DEBUG] handle the recognition task')
        ticks += 1
        ball = q.get(True)
        # np.save(f'images/{ticks}.txt', ball, allow_pickle=True)
        # print('[DEBUG] get a ball from queue', ticks)
        pos = getBallContours(ball)
        # recognize the position of the ball
        ballPosX.value = pos[0]
        ballPosY.value = pos[1]
        debug_print(f'[DEBUG] predicted position of the ball: ({ballPosX.value}, {ballPosY.value})', 2)


def recognitionTask(q, ballPosX, ballPosY):
    """
    main function to start the recognition task
    """
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(findBall(q, ballPosX, ballPosY))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()