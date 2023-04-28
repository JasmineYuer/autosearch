#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
import PyPDF2
from io import BytesIO
# importing required modules
from PyPDF2 import PdfReader
  

def download_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        print("Failed to download the PDF file.")
        return None

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfFileReader(pdf_file)
    text = ""

    for page_num in range(reader.getNumPages()):
        page = reader.getPage(page_num)
        text += page.extractText()

    return text




# In[1]:


# importing required modules
from PyPDF2 import PdfReader
  


# In[7]:


pip install PyCryptodome 


# In[3]:


# creating a pdf reader object
pdf_file = download_pdf("https://ir.smithmicro.com/presentation/SMSI-Investor-Overview-May-2022.pdf")

reader = PdfReader(pdf_file)
  


# In[6]:


page = reader.pages[1]
  
# extracting text from page
text = page.extract_text()


# In[7]:


text


# In[ ]:


# printing number of pages in pdf file
print(len(reader.pages))
  
# getting a specific page from the pdf file
page = reader.pages[0]
  
# extracting text from page
text = page.extract_text()
print(text)


# In[3]:


if pdf_file:
    text = extract_text_from_pdf(pdf_file)
    print("Extracted Text:")
    print(text)


# In[4]:


pdf_file


# In[ ]:




