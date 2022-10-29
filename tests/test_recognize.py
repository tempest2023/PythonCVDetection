import numpy as np
import sys 
sys.path.append("..")

from recognition import getBallContours 


class TestRecognize:
    def test_ball_recognzie(self):
        ball = np.load('tests/ball.npy')
        pos = getBallContours(ball)
        assert pos == (201.0, 311.0)