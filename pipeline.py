import os
import json
import sys

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

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)

# This function extracts the information of all the PDFs into JSON and then generates the summaries in TXT
def process_all_pdfs(skip=False):
    if not skip:
        count = 0
        for file_name in os.listdir(PDF_DIR):
            if not file_name.lower().endswith(".pdf"):
                continue
            count += 1
            print(f"\n ***{count} -> ", end="")
            
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
        
        print(f"\n *** Finished processing the PDF files. Now generating summaries... ***\n")

    count = 0
    for file_name in os.listdir(OUTPUT_DIR):
        if not file_name.lower().endswith(".json"):
            continue
        count += 1
        print(f"\n ---{count} -> ", end="")

        json_path = os.path.join(OUTPUT_DIR, file_name)
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        summary = generate_summary_from_json(data, file_name)
        if not summary:
            continue

        output_name = os.path.splitext(file_name)[0] + ".md"
        output_path = os.path.join(SUMMARY_DIR, output_name)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-s":
        print(" *** Skipping PDF processing. Only generating summaries from existing JSON files... ***\n")
        process_all_pdfs(skip=True)
    else:
        process_all_pdfs(skip=False)