# Coform — AI Co-Design Studio

Coform is a small AI co-design prototype built for a design challenge.

It starts with the project itself rather than assuming a visual style. Designers can provide visual references or answer focused questions. Gemini then turns those inputs into a working design direction and Design DNA, followed by three text-based concept directions and a human feedback loop.

## Features

- One-question-at-a-time design discovery
- Optional visual reference analysis
- AI-generated design questions when no references are provided
- Design DNA based on explicit choices and observed reference signals
- Three alternative design concept directions
- Human feedback and AI-assisted revision
- No image generation or paid image-generation API calls

## Tech

- Python
- Streamlit
- Google Gemini API
- Pillow

## Run locally

### 1. Create a virtual environment

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Gemini API key

For local development:

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

Do not put the key directly into `app.py`.

### 4. Run

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Create a new app in Streamlit Community Cloud.
3. Select this repository and `app.py` as the main file.
4. In the app's deployment settings, add this secret:

```toml
GEMINI_API_KEY = "YOUR_API_KEY"
```

5. Deploy.

The API key should live in Streamlit Secrets, not in GitHub.

## Dataset

No external dataset is used. Coform works from user-provided project context, optional visual references, and the designer's answers.

## Credits

Built by Soheil Faridmanesh.
