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

2. Set your Gemini API Key as an environment variable (for CLI usage):
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

## Web Interface

A web interface is available by running `app.py`.
It allows you to upload an image, specify the source and target languages, and provide your Gemini API key to get the translated image directly in your browser.

```bash
python app.py
```
Open `http://localhost:5000` in your web browser.

## CLI Usage

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

The app processes `.jpg`, `.jpeg`, `.png`, and `.webp` files.

## Note

Since Gemini 3.1 Flash Image is an advanced model for visual generation/editing, speed and quality depend on the server and the input image type. The model will accurately translate the text while visually recreating the original layout!
