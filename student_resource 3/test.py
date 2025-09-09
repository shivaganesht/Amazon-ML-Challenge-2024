import csv
import requests
from PIL import Image
import pytesseract
from io import BytesIO
import concurrent.futures
import threading

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    
    text = pytesseract.image_to_string(img)
    
    cleaned_text = text.replace('\n', ' ').strip()
    
    return cleaned_text

def process_row(row, lock, processed_counter):
    image_url = row['image_link']
    extracted_text = extract_text_from_image(image_url)
    
    row['extracted_text'] = extracted_text
    
    with lock:
        processed_counter[0] += 1
        print(f"Rows processed: {processed_counter[0]}")
    
    return row

def process_csv(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['extracted_text']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        rows = []
        lock = threading.Lock()
        processed_counter = [0]  
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = {executor.submit(process_row, row, lock, processed_counter): row for row in reader}
            for future in concurrent.futures.as_completed(futures):
                try:
                    processed_row = future.result()
                    rows.append(processed_row)
                except Exception as e:
                    print(f"Error processing row: {e}")
        
        writer.writerows(rows)

input_csv = './dataset/train.csv'
output_csv = './dataset/train_with_extracted_text.csv'
process_csv(input_csv, output_csv)
print("Processing complete. Check the output CSV file.")