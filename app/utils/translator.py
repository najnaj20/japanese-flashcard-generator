from googletrans import Translator
import time

class JapaneseTranslator:
    def __init__(self):
        self.translator = Translator()

    def translate_text(self, text, src='ja', dest='id', max_retries=3):
        for attempt in range(max_retries):
            try:
                translation = self.translator.translate(text, src=src, dest=dest)
                return translation.text
            except Exception as e:
                print(f"Error pada percobaan {attempt+1}: {e}")
                time.sleep(2)
        return ""
