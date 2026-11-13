# SummarAI

A web app that turns long text and PDF documents into clear, concise summaries using Google's Gemini API. You choose the format, length and output language, and the summary streams in as it is generated.

https://github.com/user-attachments/assets/d58e6978-cabb-4961-a630-044ab17b8a2a

**Live demo:** https://summarai02.streamlit.app/

## Features

- **Two input methods:** paste text or upload a PDF.
- **Format:** paragraph or bullet points.
- **Length:** short, medium or detailed.
- **Output language:** English, Hindi, Spanish, French, German or Portuguese. The source text can be in any language Gemini understands.
- **Streaming output:** the summary appears word by word instead of after a long wait.
- **Summary statistics:** original word count, summary word count and percentage reduction.
- **Copy and download:** copy the summary to the clipboard or save it as a `.txt` file.
- **Input checks:** warns on empty input, on too little text (for example scanned PDFs with no readable text), and trims very long documents to 50,000 words.
- **Clean, responsive interface** with a light blue theme, built with custom CSS on top of Streamlit.

## Tech stack

| Part | Tool |
|---|---|
| Interface | Streamlit |
| AI model | Google Gemini (`google-genai` SDK) |
| PDF reading | pypdf |
| Configuration | python-dotenv |
| Language | Python 3.10+ |

## How it works

1. The user picks a format, length and language, then pastes text or uploads a PDF.
2. For PDFs, `pypdf` extracts the text from every page.
3. The app checks the input length and trims it if it exceeds the limit.
4. `build_prompt()` combines the text with the chosen format, length and language into a single instruction. For example: "Summarize the text below as 5-7 bullet points. Write the summary in Spanish."
5. The prompt is sent to Gemini with streaming enabled, and the response is displayed as it arrives.
6. The result is stored in `st.session_state`, so it stays on screen when buttons such as Download trigger a rerun.

Language support works through the prompt itself, so no separate translation library is needed. Adding a language only requires adding its name to the `LANGUAGES` list.

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/aditi-tyagi02/SummarAI.git
cd SummarAI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API key

Get a free key from [Google AI Studio](https://aistudio.google.com/), then create a file named `.env` in the project folder:

```
GEMINI_API_KEY=your-key-here
```

### 4. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Project structure

```
.
├── app.py              # The complete application
├── requirements.txt    # Python dependencies
├── .gitignore          # Keeps .env out of version control
└── README.md
```

### requirements.txt

```
streamlit>=1.42
python-dotenv
google-genai
pypdf
```

### .gitignore

```
.env
__pycache__/
```

## Configuration

These constants are at the top of `app.py`:

| Constant | Purpose |
|---|---|
| `MODEL` | Gemini model used for summaries |
| `MAX_WORDS` | Maximum words sent to the model (default 50,000) |
| `LENGTHS` | Instruction used for each format and length combination |
| `LANGUAGES` | Output languages shown in the dropdown |

## Deployment

The app is deployed on [Streamlit Community Cloud](https://share.streamlit.io/), which is free.

1. Push `app.py`, `requirements.txt` and `.gitignore` to a GitHub repository. Do not push `.env`.
2. On Streamlit Community Cloud, choose **Create app** and select the repository, branch and `app.py`.
3. Under **Advanced settings**, add your key in the Secrets box:
   ```
   GEMINI_API_KEY = "your-key-here"
   ```
4. Click **Deploy**. Later pushes to GitHub update the live app automatically.


## Limitations

- **Scanned PDFs:** there is no OCR, so PDFs that are only images cannot be summarized.
- **Very long documents:** text beyond `MAX_WORDS` is trimmed rather than summarized in chunks.
- **Word counts:** counts are based on splitting at spaces, so the reduction percentage is approximate, and less meaningful for languages that do not separate words with spaces.
- **Accuracy:** summaries come directly from the model and are not checked against the source.
- **Privacy:** text you paste or upload is sent to the Gemini API. Do not use confidential documents.

