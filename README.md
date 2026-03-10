# ImagiTranslate (Image Translator)

This application translates text within images while faithfully preserving the original layout, colors, typography, and backgrounds.

It leverages the new **Gemini 3.1 Flash Image Preview** model (also known as *Nano Banana 2*).

## Requirements

- **Python 3.9+** (or higher)
- **Gemini API Key**: You need a valid API key with access to the Gemini 3.1 Flash Image Preview model.

1. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

2. *(Optional)* Set your Gemini API Key as an environment variable (mostly useful for CLI usage):
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

## 🌐 Web Interface (Recommended)

The easiest and most interactive way to use ImagiTranslate is through its modern, glassmorphism-styled web app.
It allows you to upload an image, select the source/target languages, and securely input your Gemini API Key directly from the browser.

To start the web application:
```bash
python app.py
```
Then, open your web browser and navigate to: **`http://localhost:5000`**

**Features of the Web App:**
- Simple drag-and-drop or click-to-upload interface.
- Instant visual feedback and side-by-side comparison of original and translated images.
- No need to save your API Key in the code; you can input it securely during the session.

---

## 💻 CLI Usage (Batch Processing)

If you prefer the command line or need to process multiple images at once, you can use the CLI script. 
By default, the script looks for images in an `input` folder and saves the translated versions in an `output` folder (creating them if they don't exist).

### Basic Command

Translate all images in `./input` to English:

```bash
python image_translator.py -t "English"
```

### Advanced Options

You can customize the folders and languages specifying the appropriate flags:

- `-i`, `--input`: Path to the folder containing the source images.
- `-o`, `--output`: Path to the folder to save the translated images.
- `-s`, `--source-lang`: Source language (default: "auto-detect")
- `-t`, `--target-lang`: Target language (required, e.g., "English", "Italiano", "Spanish").

**Example:**

```bash
python image_translator.py --input ./original_images --output ./translated_images --source-lang "English" --target-lang "French"
```

## Supported Formats

Both the Web App and the CLI script process `.jpg`, `.jpeg`, `.png`, and `.webp` files.

## Note

Since Gemini 3.1 Flash Image is an advanced model for visual generation/editing, speed and quality depend on your region and the input image type. The model will accurately translate the text while visually recreating the original layout!
