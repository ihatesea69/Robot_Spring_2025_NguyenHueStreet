import pygame
import random
import time
import threading

class AudioManager:
    def __init__(self):
        self.loop_max = 3
        self.init_mixer()
        
    def init_mixer(self):
        try:
            pygame.mixer.init()
            print("Audio system initialized")
        except Exception as e:
            print(f"Audio initialization error: {e}")
            
    def play_greeting(self):
        greeting_sounds = ['EN', 'CHINA', 'FR', 'JP', 'KR', 'RUS']
        selected_sound = random.choice(greeting_sounds)
        audio_path = f'resources/sound_greeting/HPNewYear_{selected_sound}.mp3'
        
        try:
            sound = pygame.mixer.Sound(audio_path)
            sound.play()
            time.sleep(3)
        except Exception as e:
            print(f"Audio error: {e}")
            
    def play_audio(self, audio_path):
        try:
            sound = pygame.mixer.Sound(audio_path)
            for _ in range(self.loop_max):
                sound.play()
                time.sleep(2.5)
        except Exception as e:
            print(f"Audio error: {e}") 