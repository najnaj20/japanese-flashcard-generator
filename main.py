import streamlit as st
import logging
from pathlib import Path
import os
import pandas as pd
from app.utils.audio import AudioProcessor
from app.utils.translator import Translator
from app.utils.vocabulary import VocabularyProcessor
from app.utils.anki import AnkiDeckGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_processors():
    """
    Inisialisasi semua processor yang dibutuhkan aplikasi
    """
    try:
        # Initialize processors dengan parameter yang sesuai
        audio_processor = AudioProcessor(model_type='base')
        translator = Translator()
        vocabulary_processor = VocabularyProcessor()
        anki_creator = AnkiDeckGenerator()

        return audio_processor, translator, vocabulary_processor, anki_creator

    except Exception as e:
        logger.error(f"Error initializing processors: {str(e)}")
        raise

def process_youtube_url(url, audio_processor):
    """
    Proses URL YouTube untuk mendapatkan transkripsi
    """
    try:
        segments = audio_processor.process_youtube_url(url)
        return segments
    except Exception as e:
        logger.error(f"Error processing YouTube URL: {str(e)}")
        st.error(f"Error processing YouTube URL: {str(e)}")
        return None

def process_audio_file(file, audio_processor):
    """
    Proses file audio yang diupload untuk mendapatkan transkripsi
    """
    try:
        # Simpan file yang diupload
        temp_dir = Path("/app/app/data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        temp_path = temp_dir / file.name
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())
        
        # Proses file audio
        segments = audio_processor.process_audio_file(str(temp_path))
        
        # Hapus file temporary
        os.remove(temp_path)
        
        return segments
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        st.error(f"Error processing audio file: {str(e)}")
        return None

def create_flashcard(segment, translation, vocabulary, anki_creator):
    """
    Buat flashcard dari segment
    """
    try:
        # Buat DataFrame untuk satu kartu
        data = {
            'word': [vocabulary],  # Asumsi vocabulary adalah string
            'translation': [translation],
            'context': [segment['text']]
        }
        df = pd.DataFrame(data)
        
        # Buat audio files
        audio_files = anki_creator.create_audio_files(df)
        
        # Generate deck
        output_path = anki_creator.generate_deck(df, audio_files)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating flashcard: {str(e)}")
        raise

def main():
    try:
        st.title("Japanese Flashcard Generator")
        
        # Initialize processors
        audio_processor, translator, vocabulary_processor, anki_creator = initialize_processors()
        
        # Input section
        st.header("Input")
        input_type = st.radio(
            "Choose input type:",
            ["YouTube URL", "Audio File"]
        )
        
        segments = None
        
        if input_type == "YouTube URL":
            url = st.text_input("Enter YouTube URL:")
            if url:
                with st.spinner("Processing YouTube video..."):
                    segments = process_youtube_url(url, audio_processor)
                    
        else:  # Audio File
            uploaded_file = st.file_uploader("Upload audio file", type=['mp3', 'wav', 'm4a'])
            if uploaded_file:
                with st.spinner("Processing audio file..."):
                    segments = process_audio_file(uploaded_file, audio_processor)
        
        # Display results
        if segments:
            st.header("Transcription Results")
            
            # Untuk menyimpan semua kartu yang akan dibuat
            all_cards_data = []
            
            # Display segments
            for i, segment in enumerate(segments):
                with st.expander(f"Segment {i+1}"):
                    st.write(f"Time: {segment['start']:.2f}s - {segment['end']:.2f}s")
                    st.write(f"Text: {segment['text']}")
                    
                    # Translation
                    translation = None
                    if st.button(f"Translate {i+1}"):
                        translation = translator.translate(segment['text'])
                        st.write(f"Translation: {translation}")
                    
                    # Create Anki card
                    if st.button(f"Create Flashcard {i+1}"):
                        if not translation:
                            translation = translator.translate(segment['text'])
                        
                        vocabulary = vocabulary_processor.extract_vocabulary(segment['text'])
                        try:
                            output_path = create_flashcard(
                                segment=segment,
                                translation=translation,
                                vocabulary=vocabulary,
                                anki_creator=anki_creator
                            )
                            st.success(f"Flashcard created successfully! Saved to: {output_path}")
                            
                            # Tambahkan ke list kartu
                            all_cards_data.append({
                                'text': segment['text'],
                                'translation': translation,
                                'vocabulary': vocabulary
                            })
                            
                        except Exception as e:
                            st.error(f"Error creating flashcard: {str(e)}")
            
            # Tombol untuk membuat deck dengan semua kartu
            if all_cards_data and st.button("Create Deck with All Cards"):
                try:
                    # Buat DataFrame untuk semua kartu
                    df = pd.DataFrame([{
                        'word': card['vocabulary'],
                        'translation': card['translation'],
                        'context': card['text']
                    } for card in all_cards_data])
                    
                    # Buat audio files
                    audio_files = anki_creator.create_audio_files(df)
                    
                    # Generate deck
                    output_path = anki_creator.generate_deck(df, audio_files)
                    st.success(f"Complete deck created successfully! Saved to: {output_path}")
                    
                except Exception as e:
                    st.error(f"Error creating complete deck: {str(e)}")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An error occurred. Please check the logs for details.")

if __name__ == "__main__":
    main()
