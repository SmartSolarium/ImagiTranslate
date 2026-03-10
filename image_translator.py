import os
import argparse
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types

def translate_images(input_dir: str, output_dir: str, source_lang: str, target_lang: str):
    """
    Translates text within a batch of images from a source language to a target language
    using Gemini 3.1 Flash Image Preview (Nano Banana 2).
    """
    # Assicurati di avere impostato la variabile d'ambiente GEMINI_API_KEY
    if not os.environ.get("GEMINI_API_KEY"):
        print("Errore: Variabile d'ambiente GEMINI_API_KEY non trovata.")
        print("Per favore, impostala eseguendo: export GEMINI_API_KEY='la_tua_api_key'")
        return

    try:
        # Inizializza il client GenAI
        client = genai.Client()
    except Exception as e:
        print(f"Errore durante l'inizializzazione del client: {e}")
        return
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Crea la cartella di output se non esiste
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Estensioni supportate
    valid_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
    
    # Cerca le immagini nella cartella di input
    images_found = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]
    
    if not images_found:
        print(f"Nessuna immagine trovata in '{input_dir}'.")
        print(f"Formati supportati: {', '.join(valid_extensions)}")
        return

    print(f"Trovate {len(images_found)} immagini.")
    print(f"Avvio traduzione in batch (da '{source_lang}' a '{target_lang}')...\n")
    
    # Costruiamo il prompt per il modello di image editing
    prompt = (
        f"Translate all text in this image from {source_lang} to {target_lang}. "
        "Strictly maintain the exact original layout, typography, colors, and visual style. "
        "The output should look identical to the original image but with the text translated."
    )

    for img_file in images_found:
        print(f"[*] Elaborazione di: {img_file.name} ...")
        
        try:
            # Apriamo l'immagine base (da tradurre)
            base_image = Image.open(img_file)
            
            # Chiamata al modello con sistema di Retry
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
                        break # Successo
                    else:
                        raise Exception("Risposta vuota o non valida")
                except Exception as e:
                    print(f"    [!] Tentativo {attempt + 1}/{max_retries} fallito per {img_file.name}: {e}")
                    if attempt < max_retries - 1:
                        print(f"    [*] Nuovo tentativo tra {retry_delay} secondi...")
                        time.sleep(retry_delay)
                        retry_delay *= 2 # Exponential backoff
                    else:
                        print(f"    [-] Errore irreversibile dopo {max_retries} tentativi per {img_file.name}.")
                out_file_path = output_path / img_file.name
                
                # Ottiene l'immagine tradotta
                part = response.candidates[0].content.parts[0]
                
                if hasattr(part, 'image') and part.image:
                    result_image = part.image
                elif hasattr(part, 'inline_data') and part.inline_data:
                    import io
                    result_image = Image.open(io.BytesIO(part.inline_data.data))
                else:
                    print(f"    [-] Errore: Il modello non ha restituito un'immagine valida per {img_file.name}.")
                    continue
                
                # Assicuriamoci che sia convertita nel giusto formato colore in base all'estensione
                if img_file.suffix.lower() in {'.jpg', '.jpeg'} and result_image.mode in ('RGBA', 'P'):
                    result_image = result_image.convert('RGB')

                result_image.save(out_file_path)
                
                print(f"    [+] Salvato con successo in: {out_file_path}")
            else:
                print(f"    [-] Errore: Nessuna risposta valida restituita dall'API per {img_file.name}.")
                
        except Exception as e:
            print(f"    [!] Errore durante l'elaborazione di {img_file.name}: {e}")

    print("\nTraduzione in batch completata!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Traduci in batch il testo nelle immagini mantenendo il layout tramite Nano Banana 2 (Gemini 3.1 Flash Image Preview)."
    )
    parser.add_argument("-i", "--input", default="./input", help="Cartella contenente le immagini originali. Default: ./input")
    parser.add_argument("-o", "--output", default="./output", help="Cartella in cui salvare le immagini tradotte. Default: ./output")
    parser.add_argument("-s", "--source-lang", default="auto-detect", help="Lingua originale (es. 'English'). Default: auto-detect")
    parser.add_argument("-t", "--target-lang", required=True, help="Lingua di destinazione (es. 'Italiano'). Richiesto.")
    
    args = parser.parse_args()
    
    translate_images(args.input, args.output, args.source_lang, args.target_lang)
