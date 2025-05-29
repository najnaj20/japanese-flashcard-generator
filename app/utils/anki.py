import genanki
import random
import os
import logging
from gtts import gTTS
from pathlib import Path
from typing import List, Tuple
import pandas as pd

class AnkiDeckGenerator:
    def __init__(self, temp_dir="app/data/temp"):
        """
        Inisialisasi AnkiDeckGenerator
        
        Args:
            temp_dir (str): Path ke direktori temporary untuk menyimpan file audio
        """
        self.logger = logging.getLogger(__name__)
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Model ID dan Deck ID yang konsisten
        self.model_id = random.randrange(1 << 30, 1 << 31)
        self.deck_id = random.randrange(1 << 30, 1 << 31)
        
        self.model = self._create_model()

    def _create_model(self):
        """
        Buat model Anki dengan styling yang lebih baik
        
        Returns:
            genanki.Model: Model untuk kartu Anki
        """
        return genanki.Model(
            self.model_id,
            'Japanese Vocabulary Model',
            fields=[
                {'name': 'Word'},
                {'name': 'Translation'},
                {'name': 'Context'},
                {'name': 'Audio'}
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '''
                        <div class="word">{{Word}}</div>
                    ''',
                    'afmt': '''
                        <div class="word">{{Word}}</div>
                        <hr>
                        <div class="translation">{{Translation}}</div>
                        {{#Context}}
                        <div class="context">
                            <div class="context-label">Context:</div>
                            {{Context}}
                        </div>
                        {{/Context}}
                        <div class="audio">{{Audio}}</div>
                    ''',
                },
            ],
            css='''
                .card {
                    font-family: arial;
                    font-size: 20px;
                    text-align: center;
                    color: black;
                    background-color: white;
                    padding: 20px;
                }
                .word {
                    font-size: 40px;
                    color: #333;
                    margin-bottom: 20px;
                }
                .translation {
                    font-size: 25px;
                    color: #666;
                    margin: 15px 0;
                }
                .context {
                    font-size: 18px;
                    color: #888;
                    margin-top: 15px;
                    padding: 10px;
                    background-color: #f5f5f5;
                    border-radius: 5px;
                }
                .context-label {
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .audio {
                    margin-top: 15px;
                }
            '''
        )

    def create_audio_files(self, df: pd.DataFrame) -> List[str]:
        """
        Buat file audio untuk setiap kata
        
        Args:
            df (pd.DataFrame): DataFrame dengan kolom 'word'
            
        Returns:
            List[str]: List path file audio yang dibuat
        """
        audio_files = []
        try:
            for i, row in df.iterrows():
                word = row['word']
                # Buat filename yang aman
                safe_word = "".join(x for x in word if x.isalnum() or x in (' ', '-', '_'))
                audio_path = self.temp_dir / f"word_{i}_{safe_word}.mp3"
                
                try:
                    tts = gTTS(text=word, lang='ja')
                    tts.save(str(audio_path))
                    audio_files.append(str(audio_path))
                    self.logger.info(f"Created audio file for: {word}")
                except Exception as e:
                    self.logger.warning(f"Failed to create audio for word '{word}': {str(e)}")
                    audio_files.append("")  # Tambahkan string kosong jika gagal
                    
            return audio_files
            
        except Exception as e:
            self.logger.error(f"Error creating audio files: {str(e)}")
            raise

    def generate_deck(self, df: pd.DataFrame, audio_files: List[str]) -> str:
        """
        Generate deck Anki dari DataFrame dan file audio
        
        Args:
            df (pd.DataFrame): DataFrame dengan kolom 'word', 'translation', dan 'context'
            audio_files (List[str]): List path file audio
            
        Returns:
            str: Path ke file .apkg yang dihasilkan
        """
        try:
            # Buat deck
            deck = genanki.Deck(self.deck_id, 'Japanese Vocabulary from Text')
            
            # Tambahkan notes
            valid_audio_files = []
            for i, (_, row) in enumerate(df.iterrows()):
                audio_path = audio_files[i] if i < len(audio_files) else ""
                
                if audio_path and os.path.exists(audio_path):
                    audio_filename = os.path.basename(audio_path)
                    audio_field = f'[sound:{audio_filename}]'
                    valid_audio_files.append(audio_path)
                else:
                    audio_field = ''

                note = genanki.Note(
                    model=self.model,
                    fields=[
                        row['word'],
                        row.get('translation', ''),
                        row.get('context', ''),
                        audio_field
                    ]
                )
                deck.add_note(note)
                self.logger.info(f"Added note for word: {row['word']}")

            # Buat dan simpan package
            package = genanki.Package(deck)
            if valid_audio_files:
                package.media_files = valid_audio_files
            
            output_path = self.temp_dir / 'japanese_vocabulary.apkg'
            package.write_to_file(str(output_path))
            self.logger.info(f"Successfully generated Anki deck at: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error generating deck: {str(e)}")
            raise

    def cleanup(self):
        """Bersihkan file audio temporary"""
        try:
            for file in self.temp_dir.glob("word_*.mp3"):
                try:
                    file.unlink()
                    self.logger.info(f"Removed temporary file: {file}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove file {file}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    def __del__(self):
        """Destructor untuk membersihkan file temporary"""
        self.cleanup()
