import os
import sys
import json
import time
from huggingface_hub import InferenceClient

HF_TOKEN = open("hf_token", "r").read().strip()
MODELO_HF = "meta-llama/Meta-Llama-3-8B-Instruct"

def generate_summary_from_json(data, json_name):
    print(f"Sending {json_name} data to Hugging Face ({MODELO_HF})...")
    start_time = time.time()

    client = InferenceClient(model=MODELO_HF, token=HF_TOKEN)

    system_prompt = """
    Eres un asistente experto en ayudas y becas educativas. Tu tarea es leer un JSON con datos estructurados de una convocatoria de becas del BOE y generar un resumen claro y conciso en español escrito profesionalmente.
    El resumen debe estar redactado en lenguaje natural, dirigido a estudiantes pero escrito de forma profesional, e incluir toda la información relevante: curso académico, cuantías, notas mínimas, umbrales de renta y plazos de solicitud.
    NO incluyas el JSON en tu respuesta. Escribe únicamente el resumen en texto plano, sin formato markdown.
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