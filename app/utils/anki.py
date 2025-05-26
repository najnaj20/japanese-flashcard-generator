import genanki
import random
import os
from gtts import gTTS

class AnkiDeckGenerator:
    def __init__(self, temp_dir="data/temp"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    def create_audio_files(self, df):
        audio_files = []
        for i, row in df.iterrows():
            word = row['word']
            audio_path = os.path.join(self.temp_dir, f"word_{i}_{word}.mp3")
            
            tts = gTTS(text=word, lang='ja')
            tts.save(audio_path)
            audio_files.append(audio_path)
            
        return audio_files

    def generate_deck(self, df, audio_files):
        model = genanki.Model(
            random.randrange(1 << 30, 1 << 31),
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
                    'qfmt': '{{Word}}',
                    'afmt': '{{FrontSide}}<hr id="answer">Translation: {{Translation}}<br><br>Context: {{Context}}<br>{{Audio}}',
                },
            ])

        deck = genanki.Deck(
            random.randrange(1 << 30, 1 << 31),
            'Japanese Vocabulary from Text'
        )

        for i, (row, audio_path) in enumerate(zip(df.iterrows(), audio_files)):
            audio_filename = os.path.basename(audio_path)
            note = genanki.Note(
                model=model,
                fields=[
                    row[1]['word'],
                    row[1]['translation'],
                    row[1]['context'],
                    f'[sound:{audio_filename}]'
                ])
            deck.add_note(note)

        package = genanki.Package(deck)
        package.media_files = audio_files
        output_path = os.path.join(self.temp_dir, 'japanese_vocabulary.apkg')
        package.write_to_file(output_path)
        
        return output_path
