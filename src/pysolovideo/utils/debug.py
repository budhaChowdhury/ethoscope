__author__ = 'quentin'

import cv2

def show(self,im,t=-1):
    cv2.imshow("debug",im)
    cv2.waitKey(t)
