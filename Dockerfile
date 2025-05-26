FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages one by one
RUN pip install --no-cache-dir streamlit==1.32.0
RUN pip install --no-cache-dir yt-dlp==2024.3.10
RUN pip install --no-cache-dir openai-whisper==20240930
RUN pip install --no-cache-dir fugashi==1.2.1
RUN pip install --no-cache-dir unidic-lite==1.0.8
RUN pip install --no-cache-dir googletrans==4.0.0-rc1
RUN pip install --no-cache-dir gtts==2.5.4
RUN pip install --no-cache-dir genanki==0.13.1
RUN pip install --no-cache-dir pandas==2.0.2
RUN pip install --no-cache-dir torch
RUN pip install --no-cache-dir numpy

# Copy application code
COPY ./app .

# Create data directory
RUN mkdir -p data/temp

# Expose port
EXPOSE 8501

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the application
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501"]
