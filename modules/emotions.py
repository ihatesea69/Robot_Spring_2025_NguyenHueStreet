import random
from utils.logger import Logger

class EmotionManager:
    def __init__(self, audio_manager, display_manager):
        self.audio_manager = audio_manager
        self.display_manager = display_manager
        self.emotions = self._create_emotions()
        self.logger = Logger()
        self.logger.info("Emotion manager initialized")
        
    def _create_emotions(self):
        return {
            'happy': {"eye": "resources/happy/happy", "gesture": "Wave happily!"},
            'roll': {"eye": "resources/roll/roll", "gesture": "Roll eyes!"},
            'heart': {"eye": "resources/heart/heart", "gesture": "Make heart shape!"},
            'blink': {"eye": "resources/blink/blink", "gesture": "Blink continuously!"}
        }
        
    def one_emotion(self):
        emotions = ['blink', 'roll']
        selected = random.choice(emotions)
        emotion = self.emotions[selected]
        self.logger.info(f"Playing one emotion: {selected}")
        
        self.display_manager.display_eye_with_audio_no_greeting(
            f"{emotion['eye']}.mp4",
            f"{emotion['eye']}.MP3"
        )
        
    def show_emotion(self):
        emotions = ['happy', 'heart']
        selected = random.choice(emotions)
        emotion = self.emotions[selected]
        self.logger.info(f"Showing emotion: {selected}")
        
        self.display_manager.display_eye_with_audio(
            f"{emotion['eye']}.mp4",
            f"{emotion['eye']}.MP3"
        ) 