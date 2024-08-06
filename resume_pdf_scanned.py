# Importing the Necessary Libraries:

import json
import os
import time
import re
import docx2txt
import google.generativeai as genai
import pdfminer
from pdfminer.high_level import extract_text
from google.api_core import retry
from dotenv import load_dotenv
load_dotenv()
import PIL
from PIL import Image, ImageDraw, ImageFont

# Configuring the Gemini API:

genai.configure(api_key=os.getenv("GOOGLE_API_KEY1"))

# Uploading the File to the Gemini:

file_path = input("Enter the File Path: ") 

def upload_file_gemini(file_path):
    file = genai.upload_file(file_path)
    print(f"File Uploaded: {file.display_name} and File URI: {file.uri}")
    return file

file_uploaded = upload_file_gemini(file_path)
print(file_uploaded)

uploaded_file_name = file_uploaded.name
print(uploaded_file_name)

# Waiting If the File is Not Active:

def wait_for_active_file(file_uploaded):
    global file_get
    file_get = genai.get_file(uploaded_file_name)
    print(file_get)
    print(file_get.name, file_get.display_name)
    print(file_get.state.name)
    while file_get.state.name == 'PROCESSING':
        print("The file is still Processing.")
        time.sleep(20)
        file_get = genai.get_file(uploaded_file_name)
        print(file_get)
        print(file_get.name, file_get.display_name)
        print(file_get.state.name)
    if file_get.state.name != 'ACTIVE':
        raise Exception(f"File: {file_get.name} not processed till now.")
    

    return "The File is Active and it is ready for Data Scrapping..."

file_state = wait_for_active_file(file_uploaded)
print(file_state)

instruction = "Behave like the best text extractor. Extract the text as like in the file uploaded as well as give proper spacing. Give the Contents of the Uploaded file as it is without any change. It should be present as like in the file uploaded. Give some space between each sections strictly."

safety = {
    'HATE' : 'BLOCK_NONE',
    'HARASSMENT' : 'BLOCK_NONE',
    'SEXUAL' : 'BLOCK_NONE',
    'DANGEROUS' : 'BLOCK_NONE',
}

# Configuring the Gemini Model:

model = genai.GenerativeModel(model_name="gemini-1.5-flash",generation_config=genai.GenerationConfig(
    temperature=0.7,
    top_p=0.95,
    top_k=64,
    response_mime_type='text/plain',
    max_output_tokens=8192,
),system_instruction=instruction, safety_settings=safety,) 

prompt ="""
Give the Contents of the Uploaded file as it is without any change. Give the name of the candidate in the first line. Both the final data and the file uploaded should have the data in the same order. Please include a line space inbetween 2 sections compulsorily. Dont include Start of OCR and End of OCR in the final data and in the image strictly. Extract the table present in the uploaded file in a single row strictly. Give proper spacing in the table format. Give the mailid correctly without any spelling mistakes. Dont change any formats and orders just give as in the pdf file uploaded strictly. Give the data in a beautiful manner strictly. Strictly dont skip any data in the final data. The image should look nice and should be easily understood. The line should come next to the bullet point and if there is a value with colon it should come in a single line strictly. Give the table data with a : between the data. Dont skip any duration in the final data."""

def get_response(prompt,file_uploaded):
    response = model.generate_content([prompt,file_uploaded], request_options={'retry' : retry.Retry(predicate=retry.if_transient_error)})
    return response.text

details = get_response(prompt,file_uploaded)
details = details.replace("**","").replace("#","").replace("##","")
print(details)

for file in genai.list_files():
    print(f"File Name: {file.display_name} and File URI: {file.uri}")

print(f"File to be Deleted: {file_uploaded}")
genai.delete_file(file_uploaded)

print("File Deleted Successfully...")

def text_to_image(text, filename):
    padding = 10
    font = ImageFont.load_default()
    dummy_img = Image.new("RGB", (1,1))
    draw = ImageDraw.Draw(dummy_img)
    textbbox = draw.textbbox((0,0), text, font=font)
    print(textbbox)
    text_width = textbbox[2] - textbbox[0]
    text_height = textbbox[3] - textbbox[1]
    print(text_width)
    print(text_height)

    image_width = text_width + padding * 2
    image_height = text_height + padding * 2
    print(image_width)
    print(image_height)

    img = Image.new("RGB",(image_width, image_height), color='white')
    d = ImageDraw.Draw(img)
    d.text((padding,padding), text, font=font, fill='black')
    img.save(filename)

text = details
filename = input("Enter the Output Filename: ")
text_to_image(text, filename)
