import os
import json
import time
from huggingface_hub import InferenceClient

from extractor_pdf import extract_relevant_text

# Hugging Face Configuration
HF_TOKEN = ""
MODELO_HF = "meta-llama/Meta-Llama-3-8B-Instruct"

def generate_json_from_text(text, pdf_name):
    """
    Sends the filtered BOE text to Hugging Face Inference API
    and requests an EXTENDED strictly formatted JSON output.
    """
    print(f"Sending {pdf_name} data to Hugging Face ({MODELO_HF})...")
    start_time = time.time()
    
    client = InferenceClient(model=MODELO_HF, token=HF_TOKEN)
    
    # SYSTEM PROMPT: Requesting detailed information
    system_prompt = """
    Eres un asistente experto en extraer datos legales. Tu ÚNICA tarea es leer el texto y devolver un JSON.
    NO escribas NADA MÁS, ni saludos, ni explicaciones. Solo el JSON puro.
    
    Estructura OBLIGATORIA. Respeta los nombres de las claves. Si no encuentras un dato exacto en el texto, el valor DEBE ser null:
    {
        "curso_academico": "ejemplo 2021-2022",
        "cuantia_fija_renta": 1500,
        "cuantia_fija_residencia": 900,
        "cuantia_beca_basica": 100,
        "cuantia_variable_minima": 40,
        "cuantia_excelencia_maxima": 110,
        "nota_minima_universidad_grado": 4.0,
        "umbral_1_un_miembro": 847,
        "umbral_2_un_miembro": 13346,
        "umbral_3_un_miembro": 14888,
        "plazo_solicitud_universitarios": "16 de septiembre de 2021",
        "plazo_solicitud_no_universitarios": null
    }
    """

    try:
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                # Mensaje del usuario también en español
                {"role": "user", "content": f"Extrae los datos de este texto del BOE:\n\n{text}"}
            ],
            max_tokens=1000,
            temperature=0.1 
        )
        
        json_string = response.choices[0].message.content
        json_string = json_string.replace("```json", "").replace("```", "").strip()
        
        data_dict = json.loads(json_string)
        
        execution_time = time.time() - start_time
        print(f"AI processing successful in {execution_time:.2f} seconds.")
        
        return data_dict

    except Exception as e:
        print(f"Error during AI generation: {e}")
        return None

# --- TESTING AREA ---
if __name__ == "__main__":
    test_pdf = "pdfs/ayudas_21-22.pdf"
    
    if os.path.exists(test_pdf):
        extracted_text = extract_relevant_text(test_pdf)
        
        if extracted_text:
            structured_data = generate_json_from_text(extracted_text, os.path.basename(test_pdf))
            
            if structured_data:
                print("\n--- FINAL EXTRACTED JSON (EXTENDED) ---")
                print(json.dumps(structured_data, indent=4, ensure_ascii=False))
                print("---------------------------------------\n")
    else:
        print(f"Warning: File not found -> {test_pdf}")