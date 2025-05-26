import streamlit as st
import logging
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from utils.audio import AudioProcessor
    from utils.translator import JapaneseTranslator
    from utils.vocabulary import VocabularyExtractor
    from utils.anki import AnkiDeckGenerator
    logger.info("Successfully imported all modules")
except Exception as e:
    logger.error(f"Error importing modules: {str(e)}")
    st.error(f"Error importing modules: {str(e)}")

st.title("Japanese Flashcard Generator")

try:
    input_type = st.radio(
        "Choose input type:",
        ["YouTube URL", "Japanese Text"]
    )

    audio_processor = AudioProcessor()
    translator = JapaneseTranslator()
    vocabulary_extractor = VocabularyExtractor()
    anki_generator = AnkiDeckGenerator()
    logger.info("Successfully initialized all processors")

    if input_type == "YouTube URL":
        url = st.text_input("Enter YouTube URL:")
        if url and st.button("Generate Flashcards"):
            try:
                with st.spinner("Processing..."):
                    logger.info(f"Processing YouTube URL: {url}")
                    
                    # Download and transcribe
                    audio_path = audio_processor.download_youtube_audio(url)
                    logger.info(f"Downloaded audio to: {audio_path}")
                    
                    text = audio_processor.transcribe_audio(audio_path)
                    logger.info("Transcription completed")
                    
                    # Extract and translate vocabulary
                    df = vocabulary_extractor.extract_vocabulary(text)
                    logger.info(f"Extracted {len(df)} vocabulary items")
                    
                    df['translation'] = df['word'].apply(lambda x: translator.translate_text(x))
                    logger.info("Translation completed")
                    
                    # Tampilkan preview hasil
                    st.subheader("Preview Generated Flashcards:")
                    preview_df = df.head()  # Ambil 5 baris pertama
                    st.dataframe(preview_df[['word', 'reading', 'translation']])
                    
                    # Generate Anki deck
                    audio_files = anki_generator.create_audio_files(df)
                    deck_path = anki_generator.generate_deck(df, audio_files)
                    logger.info(f"Generated Anki deck at: {deck_path}")
                    
                    # Informasi statistik
                    st.info(f"Total vocabulary items: {len(df)}")
                    
                    # Download button
                    with open(deck_path, "rb") as file:
                        st.download_button(
                            label="Download Anki Deck",
                            data=file,
                            file_name="japanese_vocabulary.apkg",
                            mime="application/octet-stream"
                        )
            except Exception as e:
                logger.error(f"Error processing YouTube URL: {str(e)}")
                st.error(f"Error: {str(e)}")

    else:  # Japanese Text input
        text = st.text_area("Enter Japanese text:")
        if text and st.button("Generate Flashcards"):
            try:
                with st.spinner("Processing..."):
                    logger.info("Processing text input")
                    
                    # Extract and translate vocabulary
                    df = vocabulary_extractor.extract_vocabulary(text)
                    logger.info(f"Extracted {len(df)} vocabulary items")
                    
                    df['translation'] = df['word'].apply(lambda x: translator.translate_text(x))
                    logger.info("Translation completed")
                    
                    # Tampilkan preview hasil
                    st.subheader("Preview Generated Flashcards:")
                    preview_df = df.head()  # Ambil 5 baris pertama
                    st.dataframe(preview_df[['word', 'reading', 'translation']])
                    
                    # Generate Anki deck
                    audio_files = anki_generator.create_audio_files(df)
                    deck_path = anki_generator.generate_deck(df, audio_files)
                    logger.info(f"Generated Anki deck at: {deck_path}")
                    
                    # Informasi statistik
                    st.info(f"Total vocabulary items: {len(df)}")
                    
                    # Download button
                    with open(deck_path, "rb") as file:
                        st.download_button(
                            label="Download Anki Deck",
                            data=file,
                            file_name="japanese_vocabulary.apkg",
                            mime="application/octet-stream"
                        )
            except Exception as e:
                logger.error(f"Error processing text input: {str(e)}")
                st.error(f"Error: {str(e)}")

except Exception as e:
    logger.error(f"Application error: {str(e)}")
    st.error(f"Application error: {str(e)}")
