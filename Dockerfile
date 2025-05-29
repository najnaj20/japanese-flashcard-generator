FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy aplikasi
COPY . .

# Buat direktori temp dan set permissions
RUN mkdir -p app/data/temp && \
    chmod -R 777 app/data

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]
