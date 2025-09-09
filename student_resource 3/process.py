import pytesseract
import ollama
import csv
import requests
from PIL import Image
from io import BytesIO
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(img)
    cleaned_text = text.replace('\n', ' ').strip()
    return cleaned_text

def run_ollama(extracted_text,entity_name):
    print("EXTRACTED TEXT IS:",extracted_text)
    entity_value = ollama.chat(model='llama2', messages=[
      {
        'role': 'system',
        'content': f'This is the text extracted from image: ""{extracted_text}"",Now your task is to return the value of {entity_name} present in the extracted text. NOTE: You should only return digits of the value and don\'t return any text.because i have to append this value in CSV file.',
        'max_turns': 1
      },
    ])
    return entity_value['message']['content']

def process_row(row):
    image_url = row['image_link']
    extracted_text = extract_text_from_image(image_url)
    result = run_ollama(extracted_text,row['entity_name'])
    return result
