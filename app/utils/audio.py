import yt_dlp
import whisper
import os
import logging
import tempfile

class AudioProcessor:
    def __init__(self, temp_dir="data/temp"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        try:
            self.logger.info("Loading Whisper model...")
            self.model = whisper.load_model("base")
            self.logger.info("Whisper model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading Whisper model: {str(e)}")
            raise

    def download_youtube_audio(self, url):
        """Download audio from YouTube URL with enhanced error handling and options"""
        output_path = os.path.join(self.temp_dir, "audio.mp3")
        
        # Create a temporary cookie file
        cookie_path = os.path.join(tempfile.gettempdir(), 'youtube_cookies.txt')
        
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',  # Changed format selection
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path.replace('.mp3', ''),
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'quiet': False,
            'no_warnings': False,
            'extract_audio': True,
            'audioformat': 'mp3',
            'socket_timeout': 30,  # Increased timeout
            'retries': 10,  # Increased retries
            'fragment_retries': 10,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'cookiefile': cookie_path,  # Use cookie file
            'verbose': True,  # Enable verbose output for debugging
        }

        try:
            self.logger.info(f"Attempting to download audio from: {url}")
            
            # Create empty cookie file if it doesn't exist
            if not os.path.exists(cookie_path):
                with open(cookie_path, 'w') as f:
                    f.write('')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Try first method
                    info = ydl.extract_info(url, download=True)
                except Exception as e:
                    self.logger.warning(f"First attempt failed: {str(e)}")
                    # Try alternative format if first attempt fails
                    ydl_opts['format'] = 'worstaudio/worst'
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                        info = ydl2.extract_info(url, download=True)
                
                if info is None:
                    raise Exception("Failed to extract video information")
                
                # Get the final filepath
                final_path = output_path.replace('.mp3', '') + '.mp3'
                if not os.path.exists(final_path):
                    raise Exception(f"Downloaded file not found at {final_path}")
                
                self.logger.info(f"Successfully downloaded audio to {final_path}")
                return final_path

        except Exception as e:
            self.logger.error(f"Download error: {str(e)}")
            # Try alternative method with different options
            try:
                self.logger.info("Trying alternative download method...")
                alternative_opts = ydl_opts.copy()
                alternative_opts['format'] = 'bestaudio[acodec^=opus]/bestaudio/best'
                alternative_opts['external_downloader'] = 'aria2c'
                
                with yt_dlp.YoutubeDL(alternative_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    final_path = output_path.replace('.mp3', '') + '.mp3'
                    if os.path.exists(final_path):
                        return final_path
                    
            except Exception as e2:
                self.logger.error(f"Alternative method also failed: {str(e2)}")
                raise Exception(f"All download attempts failed: {str(e)} | {str(e2)}")
        finally:
            # Cleanup cookie file
            if os.path.exists(cookie_path):
                try:
                    os.remove(cookie_path)
                except:
                    pass

    def transcribe_audio(self, audio_path):
        """Transcribe audio file to text with error handling"""
        try:
            self.logger.info(f"Starting transcription of {audio_path}")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            file_size = os.path.getsize(audio_path)
            if file_size == 0:
                raise Exception("Audio file is empty")
            
            result = self.model.transcribe(audio_path)
            
            if not result or 'text' not in result:
                raise Exception("Transcription failed - no text generated")
            
            transcribed_text = result['text'].strip()
            if not transcribed_text:
                raise Exception("Transcription resulted in empty text")
            
            self.logger.info("Transcription completed successfully")
            return transcribed_text

        except Exception as e:
            self.logger.error(f"Error during transcription: {str(e)}")
            raise

    def cleanup(self):
        """Clean up temporary files"""
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    self.logger.error(f"Error deleting {file_path}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
