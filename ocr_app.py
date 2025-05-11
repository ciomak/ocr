import os

import pandas as pd
import easyocr
import numpy as np
import pytesseract
import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image

UPLOADS = "uploads"
try:
    # Create the directory (and any necessary parent directories).
    os.makedirs(UPLOADS)
    print(f"Directory '{UPLOADS}' created successfully.")
except OSError as e:
    print(f"Error creating directory: {e}")


def perform_ocr_tesseract(image_path, lang="eng"):
    """Performs OCR on an image and returns the extracted text."""
    try:
        if image_path is None:
            st.error(f"Error: Could not read image at {image_path}")
            return None
        text = pytesseract.image_to_string(image_path, lang=lang)
        return text
    except Exception as e:
        st.error(f"An error occurred during OCR: {e}")
        return None


def perform_ocr_easy(im, lang=["en", "pl"]):
    reader = easyocr.Reader(lang, gpu=False)

    try:
        if im is None:
            st.error(f"Error: Could not read image at {im}")
            return None
        text = reader.readtext(np.array(im))
        return text
    except Exception as e:
        st.error(f"An error occurred during OCR: {e}")
        return None


def pdf_to_images(pdf_path):
    """Converts a PDF to a list of images."""
    try:
        images = convert_from_bytes(pdf_path)
        return images
    except Exception as e:
        st.error(f"An error occurred while converting PDF to images: {e}")
        return None


def main():
    st.title("OCR Application")

    ocr_tool = "EasyOCR"  # Default OCR tool

    with st.sidebar:
        ocr_tool = st.radio("Select OCR Tool:", ["EasyOCR", "Tesseract"])

    langs = pytesseract.get_languages() if ocr_tool == "Tesseract" else ["en", "pl"]
    with st.sidebar:
        # Add language selection dropdown
        selected_language = st.selectbox("Choose OCR Language", langs)

        uploaded_file = st.file_uploader(
            "Choose a PDF or image file", type=["pdf", "png", "jpg", "jpeg"]
        )
        if uploaded_file is not None:
            with open(os.path.join(UPLOADS, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Uploaded successfully: {uploaded_file.name}")

    if uploaded_file is not None:
        file_type = uploaded_file.type
        file_name = uploaded_file.name
        st.write(f"Filename: {file_name}")

        col1, col2 = st.columns([4, 7])
        if file_type == "application/pdf":
            # Handle PDF files
            images = pdf_to_images(uploaded_file.getvalue())
            if images:
                for i, img in enumerate(images):
                    with col1:
                        st.image(img, caption=f"Page {i + 1}", use_container_width=True)
                    with col2:
                        if ocr_tool == "Tesseract":
                            text = perform_ocr_tesseract(img, selected_language)
                        else:
                            st.write(ocr_tool)
                            text = perform_ocr_easy(img)

                        st.write(f"Page {i + 1} Text:")

                        if ocr_tool == "Tesseract":
                            st.write(text)
                        else:
                            df = pd.DataFrame(
                                text, columns=["Dimensions", "Text", "Scoring"]
                            )
                            df = df.drop(columns=["Dimensions"])
                            st.table(df)

            else:
                st.error("Could not convert PDF to images.")

        else:
            # Handle image files
            image = Image.open(uploaded_file)
            with col1:
                st.image(image, caption="Uploaded Image", use_container_width=True)

            if ocr_tool == "Tesseract":
                text = perform_ocr_tesseract(image, selected_language)
            else:
                text = perform_ocr_easy(image)
                df = pd.DataFrame(text, columns=["Dimensions", "Text", "Scoring"])
                df = df.drop(columns=["Dimensions"])

            with col2:
                st.write("Extracted Text:")
                if text:
                    if ocr_tool == "Tesseract":
                        st.write(text)
                    else:
                        st.table(df)
                else:
                    st.error("OCR failed to extract text.")


if __name__ == "__main__":
    main()
