import fugashi
from typing import List
import pandas as pd

class VocabularyExtractor:
    def __init__(self):
        self.tagger = fugashi.Tagger()

    def extract_vocabulary(self, text: str) -> pd.DataFrame:
        # Tokenize the text
        words = self.tagger(text)
        
        # Extract relevant words (nouns, verbs, adjectives)
        vocabulary = []
        seen_words = set()
        
        for word in words:
            # Get base form and parts of speech
            base_form = word.feature.lemma if word.feature.lemma else word.surface
            pos = word.feature.pos1
            
            # Filter for content words and skip duplicates
            if (pos in ['名詞', '動詞', '形容詞'] and  # noun, verb, adjective
                base_form not in seen_words and
                len(base_form) > 1):  # skip single characters
                
                vocabulary.append({
                    'word': base_form,
                    'reading': word.feature.kana,
                    'pos': pos
                })
                seen_words.add(base_form)
        
        return pd.DataFrame(vocabulary)

    def get_readings(self, word: str) -> str:
        """Get reading for a Japanese word"""
        word_tokens = self.tagger(word)
        readings = []
        for token in word_tokens:
            reading = token.feature.kana if token.feature.kana else token.surface
            readings.append(reading)
        return ''.join(readings)
