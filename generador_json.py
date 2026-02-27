import os
import sys
import json
import time
from huggingface_hub import InferenceClient

# Our function to parse the BOE PDFs
from extractor_pdf import extract_relevant_text

# Hugging Face configuration
HF_TOKEN = open("hf_token", "r").read().strip()
MODELO_HF = "meta-llama/Meta-Llama-3-8B-Instruct"

# Sends the filtered BOE text to Hugging Face Inference API and requests a formatted JSON output
def generate_json_from_text(text, pdf_name):
    print(f"Sending {pdf_name} data to Hugging Face ({MODELO_HF})...")
    start_time = time.time()
    
    client = InferenceClient(model=MODELO_HF, token=HF_TOKEN)
    
    # SYSTEM PROMPT: Requesting the information
    system_prompt = """
    Eres un asistente experto en extraer datos legales. Tu ÚNICA tarea es leer el texto y devolver un JSON.
    NO escribas NADA MÁS, ni saludos, ni explicaciones. Solo el JSON puro.
    
    INSTRUCCIONES CRÍTICAS:
    1. Si no encuentras un dato exacto en el texto, el valor DEBE ser null. NO te inventes datos ni copies los ejemplos!
    2. El presupuesto total debe estar SIEMPRE en euros absolutos (ejemplo: si el texto dice "2.038,13 millones", debes escribir 2038130000. Si no lo encuentras, null).
    
    Estructura OBLIGATORIA a rellenar:
    {
        "curso_academico": null,
        "presupuesto_total_becas": null, 
        "cuantia_fija_renta": null,
        "cuantia_fija_residencia": null,
        "beca_basica": null,
        "cuantia_variable_minima": null,
        "cuantia_excelencia_minima": null,
        "cuantia_excelencia_maxima": null,
        "nota_minima_universidad_grado": null,
        "plazo_solicitud_universitarios": null,
        "plazo_solicitud_no_universitarios": null,
        "umbral_1_un_miembro": null,
        "umbral_2_un_miembro": null,
        "umbral_3_un_miembro": null,
        "umbral_patrimonio_fincas_urbanas": null,
        "cuantia_adicional_insular": null
    }
    """

    try:
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extrae los datos de este PDF del BOE:\n\n{text}"}
            ],
            max_tokens=1000,
            temperature=0.0
        )
        
        json_string = response.choices[0].message.content
        json_string = json_string.replace("```json", "").replace("```", "").strip()
        
        data_dict = json.loads(json_string)
        
        execution_time = time.time() - start_time
        print(f"AI processing successful in {execution_time:.2f} seconds")
        
        return data_dict

    except Exception as e:
        print(f"Error during AI generation: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_pdf = sys.argv[1]
    else:
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
