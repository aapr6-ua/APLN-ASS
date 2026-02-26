import os
import json

# Our function to parse the BOE PDFs
from extractor_pdf import extract_relevant_text

# Our function to generate the information file
from generador_json import generate_json_from_text

# Our function to generate the summary file
from generador_txt import generate_summary_from_json

# Directories
PDF_DIR = "pdfs"
OUTPUT_DIR = "jsons"
SUMMARY_DIR = "txts"

# Hugging Face Configuration
HF_TOKEN = open("hf_token", "r").read().strip()
MODELO_HF = "meta-llama/Meta-Llama-3-8B-Instruct"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)

# This function extracts the information of all the PDFs into JSON
def process_all_pdfs():
    for file_name in os.listdir(PDF_DIR):
        if not file_name.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(PDF_DIR, file_name)
        extracted_text = extract_relevant_text(pdf_path)
        if not extracted_text:
            continue

        structured_data = generate_json_from_text(extracted_text, file_name)
        if not structured_data:
            continue

        output_name = os.path.splitext(file_name)[0] + ".json"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(structured_data, f, indent=4, ensure_ascii=False)

    for file_name in os.listdir(OUTPUT_DIR):
        if not file_name.lower().endswith(".json"):
            continue

        json_path = os.path.join(OUTPUT_DIR, file_name)
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        summary = generate_summary_from_json(data, file_name)
        if not summary:
            continue

        output_name = os.path.splitext(file_name)[0] + ".txt"
        output_path = os.path.join(SUMMARY_DIR, output_name)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)


if __name__ == "__main__":
    process_all_pdfs()