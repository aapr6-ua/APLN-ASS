import pdfplumber
import os
import time
import re

def extract_relevant_text(pdf_path):
    """
    Reads a BOE PDF, extracts all text, splits it into full sentences,
    and applies strict double-matching rules to only keep factual sentences.
    """
    print(f"Processing document: {pdf_path}...")
    start_time = time.time()
    
    relevant_sentences = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            # Read text from all pages without visual formatting to join sentences properly
            for page in pdf.pages:
                text = page.extract_text()
                if text: 
                    full_text += text + " "
                    
        # Clean line breaks and extra spaces
        full_text = re.sub(r'\s+', ' ', full_text)
        
        # Split the entire text into sentences using periods as separators
        sentences = full_text.split('. ')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # RULE 1: Financial amounts (Must contain the keyword AND the word 'euros')
            if ("cuantía" in sentence_lower or "umbral" in sentence_lower) and "euros" in sentence_lower:
                relevant_sentences.append(sentence.strip())
                
            # RULE 2: Deadlines (Must contain the deadline keyword AND a month)
            elif ("plazo" in sentence_lower or "solicitudes" in sentence_lower) and \
                 ("octubre" in sentence_lower or "septiembre" in sentence_lower or "mayo" in sentence_lower or "diciembre" in sentence_lower):
                relevant_sentences.append(sentence.strip())
                
            # RULE 3: Academic grades (Must contain the word 'nota' AND the word 'puntos')
            elif "nota" in sentence_lower and "puntos" in sentence_lower:
                relevant_sentences.append(sentence.strip())
                
            # RULE 4: Academic year
            elif "curso académico 20" in sentence_lower:
                relevant_sentences.append(sentence.strip())
                
        # Remove duplicate sentences by converting the list to a set
        relevant_sentences = list(set(relevant_sentences))
        
        # Join the surviving sentences
        relevant_text = ".\n\n".join(relevant_sentences)
        
        execution_time = time.time() - start_time
        print(f"Success. Extracted {len(relevant_text)} characters (Sniper Mode).")
        print(f"Execution time: {execution_time:.2f} seconds.")
        
        return relevant_text

    except Exception as e:
        print(f"Error processing the PDF: {e}")
        return None

# --- TESTING AREA ---
if __name__ == "__main__":
    test_file = "pdfs/ayudas_25-26.pdf" 
    if os.path.exists(test_file):
        filtered_text = extract_relevant_text(test_file)
        if filtered_text:
            print("\n--- EXTRACTED TEXT SAMPLE ---")
            # Print everything since the output should be short now
            print(filtered_text)
            print("-----------------------------\n")
    else:
        print(f"Warning: File not found -> {test_file}")