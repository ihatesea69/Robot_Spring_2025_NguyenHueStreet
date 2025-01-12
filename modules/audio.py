import pygame
import random
import time
import threading

class AudioManager:
    def __init__(self, init_mixer=True):
        self.loop_max = 3
        self.audio_lock = threading.Lock()
        if init_mixer:  # Only initialize if needed
            self.init_mixer()
        
    def init_mixer(self):
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(8)
            print("Audio system initialized")
        except Exception as e:
            print(f"Audio initialization error: {e}")
            
    def play_greeting(self):
        with self.audio_lock:
            greeting_sounds = ['EN', 'CHINA', 'FR', 'JP', 'KR', 'RUS']
            selected_sound = random.choice(greeting_sounds)
            audio_path = f'resources/sound_greeting/HPNewYear_{selected_sound}.mp3'
            
            try:
                sound = pygame.mixer.Sound(audio_path)
                channel = pygame.mixer.find_channel()
                if channel:
                    channel.play(sound)
                    pygame.time.wait(3000)  # Use pygame's wait instead of time.sleep
                    channel.stop()
            except Exception as e:
                print(f"Audio error: {e}")
            
    def play_audio(self, audio_path):
        with self.audio_lock:
            try:
                sound = pygame.mixer.Sound(audio_path)
                channel = pygame.mixer.find_channel()
                if channel:
                    for _ in range(self.loop_max):
                        channel.play(sound)
                        pygame.time.wait(2500)  # Use pygame's wait instead of time.sleep
                        channel.stop()
            except Exception as e:
                print(f"Audio error: {e}") 