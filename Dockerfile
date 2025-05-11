
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install Tesseract OCR
RUN apt-get update -y && \
  apt-get install -y --no-install-recommends --no-install-suggests tesseract-ocr libtesseract-dev libleptonica-dev tesseract-ocr-pol tesseract-ocr-eng ffmpeg libsm6 libxext6 poppler-utils && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set the Tesseract command path (check if this is the correct path)
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

COPY ocr_app.py ./

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "ocr_app.py", "--browser.gatherUsageStats", "no"]
