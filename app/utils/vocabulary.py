# app/utils/vocabulary.py

from sudachipy import dictionary, tokenizer
import logging
from typing import List, Dict

class VocabularyProcessor:
    def __init__(self):
        """
        Inisialisasi VocabularyProcessor dengan Sudachi tokenizer
        """
        self.logger = logging.getLogger(__name__)
        try:
            self.tokenizer_obj = dictionary.Dictionary().create()
            self.mode = tokenizer.Tokenizer.SplitMode.C  # Mode paling detail
        except Exception as e:
            self.logger.error(f"Error initializing Sudachi: {str(e)}")
            raise

    def extract_vocabulary(self, text: str) -> List[Dict[str, str]]:
        """
        Ekstrak kosakata dari teks Jepang menggunakan Sudachi
        
        Args:
            text (str): Teks Jepang yang akan diproses
            
        Returns:
            List[Dict[str, str]]: List dari dictionary berisi informasi kosakata
        """
        try:
            vocabulary = []
            tokens = self.tokenizer_obj.tokenize(text, self.mode)
            
            for token in tokens:
                # Skip token yang bukan kata bermakna
                if token.part_of_speech()[0] in ['補助記号', '助詞', '助動詞']:
                    continue
                
                word_info = {
                    'surface': token.surface(),  # Bentuk yang muncul di teks
                    'base': token.dictionary_form(),  # Bentuk dasar kata
                    'pos': token.part_of_speech()[0],  # Jenis kata
                    'reading': token.reading_form()  # Cara baca
                }
                
                # Hanya tambahkan kata yang memiliki bentuk dasar
                if word_info['base'] and word_info['surface']:
                    vocabulary.append(word_info)
            
            self.logger.info(f"Extracted {len(vocabulary)} vocabulary items")
            return vocabulary
            
        except Exception as e:
            self.logger.error(f"Error extracting vocabulary: {str(e)}")
            raise

    def get_word_details(self, word: str) -> Dict[str, str]:
        """
        Dapatkan informasi detail tentang sebuah kata
        
        Args:
            word (str): Kata yang akan dianalisis
            
        Returns:
            Dict[str, str]: Dictionary berisi informasi kata
        """
        try:
            tokens = self.tokenizer_obj.tokenize(word, self.mode)
            if tokens:
                token = tokens[0]
                return {
                    'word': token.surface(),
                    'reading': token.reading_form(),
                    'pos': token.part_of_speech()[0],
                    'base': token.dictionary_form()
                }
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting word details: {str(e)}")
            raise
