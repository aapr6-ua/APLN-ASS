import pdfplumber
import sys
import os
import time
import re

# Reads the PDF and extracts all text, splits it and applies double-matching rules to only keep factual sentences
def extract_relevant_text(pdf_path):
    print(f"Processing document: {pdf_path}")
    start_time = time.time()
    relevant_sentences = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text: 
                    full_text += text + " "
                    
        full_text = re.sub(r'\s+', ' ', full_text)
        sentences = full_text.split('. ')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            
            # RULE 1: Financial amounts, budgets and thresholds (Renta, patrimonio, presupuestos)
            if ("cuantía" in sentence_lower or "umbral" in sentence_lower or "presupuesto" in sentence_lower or "patrimonio" in sentence_lower or "fincas urbanas" in sentence_lower) and \
               ("euros" in sentence_lower or "millones" in sentence_lower or "€" in sentence_lower):
                relevant_sentences.append(sentence.strip())
                
            # RULE 2: Deadlines
            elif ("plazo" in sentence_lower or "solicitud" in sentence_lower) and any(mes in sentence_lower for mes in meses):
                relevant_sentences.append(sentence.strip())
                
            # RULE 3: Academic grades
            elif "nota" in sentence_lower and "puntos" in sentence_lower:
                relevant_sentences.append(sentence.strip())
                
            # RULE 4: Academic year 
            elif "curso académico 20" in sentence_lower:
                relevant_sentences.append(sentence.strip())
                
            # RULE 5: Insular/Territorial bonuses 
            elif "insular" in sentence_lower or "canarias" in sentence_lower or "baleares" in sentence_lower or "ceuta" in sentence_lower or "melilla" in sentence_lower:
                relevant_sentences.append(sentence.strip())
                
        # Remove duplicates and join
        relevant_sentences = list(set(relevant_sentences))
        relevant_text = ".\n\n".join(relevant_sentences)
        
        execution_time = time.time() - start_time
        print(f"Success. Extracted {len(relevant_text)} characters")
        print(f"Execution time: {execution_time:.2f} seconds")
        return relevant_text

    except Exception as e:
        print(f"Error processing the PDF: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        test_file = "pdfs/ayudas_25-26.pdf" 

    if os.path.exists(test_file):
        filtered_text = extract_relevant_text(test_file)
        if filtered_text:
            print("\n--- EXTRACTED TEXT SAMPLE ---")
            print(filtered_text)
            print("-----------------------------\n")
    else:
        print(f"Error: File not found -> {test_file}")
        sys.exit(1)
