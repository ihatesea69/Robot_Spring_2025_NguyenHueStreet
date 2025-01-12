import cv2
import pygame
import numpy as np

def init_screen():
    pygame.init()
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    print(f"Screen initialized: {screen_width} x {screen_height}")
    
    black_bg = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
    
    cv2.namedWindow("ALL", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("ALL", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("ALL", black_bg)
    
    return screen_width, screen_height 