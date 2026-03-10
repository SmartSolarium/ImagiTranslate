import os
import io
import base64
from flask import Flask, render_template, request, jsonify
from PIL import Image
from google import genai
from google.genai import types

app = Flask(__name__)

# Assicurati di impostare la variabile d'ambiente o di inserirla per i test locali
# os.environ["GEMINI_API_KEY"] = "la_tua_chiave"

def get_client(api_key):
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Errore inizializzazione client: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate_image():
    api_key = request.form.get('api_key')
    
    # Verifica client
    client = get_client(api_key)
    if not client:
        return jsonify({"error": "API Key di Gemini non fornita o non valida."}), 401

    # Estrarre i parametri
    source_lang = request.form.get('source_lang', 'auto-detect')
    target_lang = request.form.get('target_lang')

    if not target_lang:
        return jsonify({"error": "La lingua di destinazione è obbligatoria."}), 400

    # Verifica file immagine
    if 'image' not in request.files:
        return jsonify({"error": "Nessuna immagine fornita."}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Nessun file selezionato."}), 400

    try:
        # Legge l'immagine e crea un oggetto PIL
        img_bytes = file.read()
        base_image = Image.open(io.BytesIO(img_bytes))
        
        # Gestione formati supportati e conversioni se necessario
        if base_image.mode in ('RGBA', 'P') and file.filename.lower().endswith(('.jpg', '.jpeg')):
             base_image = base_image.convert('RGB')

        # Prompt per il modello
        prompt = (
            f"Translate all text in this image from {source_lang} to {target_lang}. "
            "Strictly maintain the exact original layout, typography, colors, and visual style. "
            "The output should look identical to the original image but with the text translated."
        )
        
        # Chiamata API Gemini via generate_content (con sistema di retry)
        max_retries = 3
        retry_delay = 2 # secondi
        response = None
        
        import time
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-3.1-flash-image-preview',
                    contents=[base_image, prompt]
                )
                
                if response and response.candidates and response.candidates[0].content.parts:
                    break # Successo, esce dal loop di retry
                else:
                    raise Exception("Risposta vuota o non valida dal modello")
                    
            except Exception as e:
                print(f"Tentativo {attempt + 1}/{max_retries} fallito: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2 # Exponential backoff
                else:
                    return jsonify({"error": f"Modello Gemini: Elaborazione fallita dopo {max_retries} tentativi. Errore: {e}"}), 500

        # Prende l'immagine tradotta
        part = response.candidates[0].content.parts[0]
        
        if hasattr(part, 'image') and part.image:
            result_pil_img = part.image
        elif hasattr(part, 'inline_data') and part.inline_data:
            result_pil_img = Image.open(io.BytesIO(part.inline_data.data))
        else:
            return jsonify({"error": "Modello Gemini non ha restituito un'immagine."}), 500
        
        # Converte nuovamente in bytes e poi in base64 per re-inviarlo al client
        img_byte_arr = io.BytesIO()
        result_pil_img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        encoded_img = base64.b64encode(img_byte_arr.read()).decode('utf-8')
        
        return jsonify({
            "success": True,
            "image": f"data:image/jpeg;base64,{encoded_img}"
        })

    except Exception as e:
        print(f"Errore durante l'elaborazione: {e}")
        return jsonify({"error": f"Errore del server: {str(e)}"}), 500

if __name__ == '__main__':
    # Esegui l'app in modalità debug su porta 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
