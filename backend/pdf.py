#!/usr/bin/env python
# coding: utf-8
# %%
import requests
import PyPDF2
from io import BytesIO
from PyPDF2 import PdfReader


def download_pdf(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        "referer": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        print("Failed to download the PDF file.")
        return


def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += f"\n\n\n**********Page {page_num}**********\n"
        text += page.extract_text()

    return text


def process_pdf(url):
    pdf = download_pdf(url)
    if pdf:
        return extract_text_from_pdf(pdf)
    else:
        return
