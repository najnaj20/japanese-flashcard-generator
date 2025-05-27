import yt_dlp
import whisper
import os
import logging
import warnings
import torch
import tempfile
from datetime import datetime
import random

warnings.filterwarnings("ignore", category=UserWarning, module="torch.nn.modules.lazy")
warnings.filterwarnings("ignore", message=".*torch.classes.*")

class AudioProcessor:
    def __init__(self, temp_dir="data/temp", model_type="base"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        self.logger = self._setup_logger()
        self.setup_whisper_model(model_type)

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def setup_whisper_model(self, model_type):
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.logger.info(f"Using device: {self.device}")
            self.model = whisper.load_model(model_type, device=self.device)
            self.logger.info("Whisper model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading Whisper model: {str(e)}")
            raise

    def download_youtube_audio(self, url):
        output_path = os.path.join(self.temp_dir, f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
        
        # List of free proxy servers (update these with working proxies)
        proxies = [
            'http://proxy1.example.com:8080',
            'http://proxy2.example.com:8080',
            # Add more proxies here
        ]

        # Rotate User-Agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15'
        ]

        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path.replace('.mp3', ''),
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'no_warnings': True,
            'quiet': False,
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'http_headers': {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
            },
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],  # Try different clients
                    'skip': ['hls', 'dash'],  # Skip problematic formats
                }
            }
        }

        download_methods = [
            # Method 1: Direct download
            lambda: self._try_download(ydl_opts, url),
            
            # Method 2: With proxy
            lambda: self._try_download({**ydl_opts, 'proxy': random.choice(proxies)}, url),
            
            # Method 3: Different format
            lambda: self._try_download({**ydl_opts, 'format': 'worstaudio/worst'}, url),
            
            # Method 4: Using cookies
            lambda: self._try_download_with_cookies(ydl_opts, url),
            
            # Method 5: Using external downloader
            lambda: self._try_download({
                **ydl_opts,
                'external_downloader': 'aria2c',
                'external_downloader_args': ['--min-split-size=1M', '--max-connection-per-server=16']
            }, url)
        ]

        last_error = None
        for method in download_methods:
            try:
                result = method()
                if result and os.path.exists(result):
                    self.logger.info(f"Successfully downloaded audio to {result}")
                    return result
            except Exception as e:
                last_error = e
                self.logger.warning(f"Download method failed: {str(e)}")
                continue

        raise Exception(f"All download methods failed. Last error: {str(last_error)}")

    def _try_download(self, opts, url):
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise Exception("Failed to extract video information")
            return opts['outtmpl'] + '.mp3'

    def _try_download_with_cookies(self, opts, url):
        cookie_path = os.path.join(tempfile.gettempdir(), 'youtube_cookies.txt')
        try:
            # Create empty cookie file
            with open(cookie_path, 'w') as f:
                f.write('')
            
            opts['cookiefile'] = cookie_path
            return self._try_download(opts, url)
        finally:
            if os.path.exists(cookie_path):
                os.remove(cookie_path)

    def transcribe_audio(self, audio_path):
        try:
            self.logger.info(f"Starting transcription of {audio_path}")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            result = self.model.transcribe(
                audio_path,
                task="transcribe",
                temperature=0,
                best_of=1,
                beam_size=1,
                patience=1
            )
            
            if not result or 'text' not in result:
                raise Exception("Transcription failed - no text generated")
            
            transcribed_text = result['text'].strip()
            self.logger.info("Transcription completed successfully")
            return transcribed_text

        except Exception as e:
            self.logger.error(f"Error during transcription: {str(e)}")
            raise

    def cleanup(self):
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    self.logger.warning(f"Error deleting {file_path}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
