# 🌐 ImagiTranslate

![ImagiTranslate](https://img.shields.io/badge/Gemini_3.1-Flash_Image-blue?style=for-the-badge&logo=google) ![Python](https://img.shields.io/badge/Python-3.9%2B-green?style=for-the-badge&logo=python) ![Flask](https://img.shields.io/badge/Flask-Web_App-black?style=for-the-badge&logo=flask)

**ImagiTranslate** is an advanced application that translates text within images while faithfully preserving the original layout, colors, typography, and backgrounds.

Powered by the **Gemini 3.1 Flash Image Preview** model (also known as *Nano Banana 2*), it seamlessly replaces the original text with the translated text as if the image were natively created in the target language.

---

## ✨ Features

- **Layout Preservation:** Maintains fonts, colors, and the original visual hierarchy.
- **Modern Web Interface:** A sleek, glassmorphism-styled Web UI for quick, single-image translations.
- **Batch Processing CLI:** Command-line tool for translating entire folders of images at once.
- **Secure:** Your Gemini API key is required but never hardcoded. You can input it safely via the UI.
- **Supported Formats:** `.jpg`, `.jpeg`, `.png`, and `.webp`.

---

## 🚀 Getting Started

### 1. Requirements

- Python 3.9 or higher.
- A **Gemini API Key** with access to the `gemini-3.1-flash-image-preview` model.

### 2. Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/SmartSolarium/ImagiTranslate.git
cd ImagiTranslate
pip install -r requirements.txt
```

---

## 🖥️ Usage: Web Application (Recommended)

The easiest and most interactive way to use ImagiTranslate is through its web interface.

1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your browser and navigate to: **`http://localhost:5000`**
3. **Upload an image**, select your languages, securely paste your **Gemini API Key**, and click "Translate"!

---

## 💻 Usage: Command Line (Batch Processing)

For processing multiple files simultaneously, you can use the CLI script.

1. *(Optional)* Set your API key as an environment variable to avoid entering it every time:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```
2. Place your source images in an `input/` folder.
3. Run the script specifying the target language (e.g., Italian):
   ```bash
   python image_translator.py --target-lang "Italiano"
   ```
4. The translated images will be saved in the `output/` folder.

#### CLI Options:
| Flag | Name | Description | Default |
|---|---|---|---|
| `-i` | `--input` | Folder containing source images | `./input` |
| `-o` | `--output` | Folder to save translated images | `./output` |
| `-s` | `--source-lang` | Source language (e.g., "English") | `auto-detect` |
| `-t` | `--target-lang` | Target language (e.g., "French") | **Required** |

**Example:**
```bash
python image_translator.py -i ./my_images -o ./translated -s "English" -t "Spanish"
```

---

## ⚠️ Notes & Limitations

- As an advanced visual generation model, **translation speed and output quality depend heavily on the complexity of the image** and current server loads.
- The model aims to achieve identical layouts, but very complex graphical text or low-resolution inputs may yield varying results.
