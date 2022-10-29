import numpy as np
import cv2

height, width = 480, 640
# draw a ball
ball = np.zeros((height, width, 3), dtype='uint8')

# random start point
x, y = np.random.rand(2)
x = int(x * width)
y = int(y * height)
radius = 20
# orange ball BGR format
color = (1, 181, 255)
# move speed
moveX = 5
moveY = 5

while(True):
    cv2.imshow('ball', ball)
    ball = np.zeros((height, width, 3), dtype='uint8')
    x += moveX
    y += moveY
    cv2.circle(ball, (x, y), radius, color, -1)
    if y >= height - radius or y <= 0 + radius:
        moveY = -moveY
    if x >= width - radius or x <= 0 + radius:
        moveX = -moveX

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
