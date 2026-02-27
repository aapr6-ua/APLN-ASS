import os
import sys
import json
import time
from huggingface_hub import InferenceClient

# Hugging Face configuration
HF_TOKEN = open("hf_token", "r").read().strip()
#MODELO_HF = "meta-llama/Meta-Llama-3-8B-Instruct"
#MODELO_HF = "Qwen/Qwen2.5-72B-Instruct"
#MODELO_HF = "deepseek-ai/DeepSeek-V3"
#MODELO_HF = "meta-llama/Llama-3.2-3B-Instruct"
#MODELO_HF = "deepseek-ai/DeepSeek-R1"
MODELO_HF = "moonshotai/Kimi-K2-Instruct"

# Sends the JSON to an LLM that generates the final summary
def generate_summary_from_json(data, json_name):
    print(f"Sending {json_name} data to Hugging Face ({MODELO_HF})...")
    start_time = time.time()

    client = InferenceClient(model=MODELO_HF, token=HF_TOKEN)

    system_prompt = """
    Eres un asistente experto en ayudas y becas educativas. Tu tarea es leer un JSON con datos oficiales de la convocatoria de becas del BOE y generar un resumen en español.
    
    El resumen debe estar redactado en un lenguaje profesional pero accesible y amigable, dirigido directamente a estudiantes. 
    Usa formato Markdown para estructurar la información (títulos ##, negritas y listas) para que sea visual y fácil de leer por encima.
    
    ESTRUCTURA OBLIGATORIA DEL RESUMEN:
    1. Título principal (ej. ## Resumen de Becas MEC Curso 202X-202X).
    2. Enseñanzas a las que aplica: enuméralas de forma natural.
    3. Presupuesto y Plazos: incluye el dinero total destinado y las fechas límite (diferenciando universitarios de no universitarios si aplica).
    4. Cuantías de la Beca: detalla el dinero (renta, residencia, excelencia, básica, variable y bonus insular).
    5. Requisitos: nota mínima y umbrales económicos (renta y patrimonio).
    
    NORMAS DE FORMATO IMPORTANTES:
    - Si ves que algún dato es 'null', simplemente indica de forma natural que la convocatoria no lo especifica.
    - Convierte los números grandes (como el presupuesto) a un formato legible en 'millones de euros' (por ejemplo 2536000000 -> 2.536 millones de euros).
    - Pon el símbolo € detrás de las cifras económicas.
    """

    try:
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Genera un resumen de esta convocatoria de becas:\n\n{json.dumps(data, indent=4, ensure_ascii=False)}"}
            ],
            max_tokens=1000,
            temperature=0.2
        )

        summary = response.choices[0].message.content.strip()

        execution_time = time.time() - start_time
        print(f"Summary generated successfully in {execution_time:.2f} seconds")

        return summary

    except Exception as e:
        print(f"Error during summary generation: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_json = sys.argv[1]
    else:
        test_json = "jsons/ayudas_21-22.json"

    if os.path.exists(test_json):
        with open(test_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        summary = generate_summary_from_json(data, os.path.basename(test_json))

        if summary:
            print("\n--- GENERATED SUMMARY ---")
            print(summary)
            print("-------------------------\n")
    else:
        print(f"Warning: File not found -> {test_json}")