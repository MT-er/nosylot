# Nosylot

A minimal web app that lets you ask questions about a webpage or pasted text. Enter a URL or paste content, ask a question, and get an AI-powered answer.

## Features

- **URL or text** — Choose to analyze a webpage (fetches and extracts visible text) or paste raw text
- **AI answers** — Uses the [Featherless](https://featherless.ai) API to answer your question based on the content
- **Light/dark mode** — Toggle with a button in the top-right; preference is saved
- **Simple UI** — Single page, no clutter

## Prerequisites

- Python 3.8+
- A [Featherless](https://featherless.ai) API key

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/nosylot.git
   cd nosylot
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API key**
   - Copy `.env` or create it in the project root
   - Set your Featherless API key:
     ```
     FEATHERLESS_API_KEY=your_key_here
     ```
   - Get a key at [featherless.ai/account/api-keys](https://featherless.ai/account/api-keys)

## Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Tech stack

- **Backend:** Flask, requests, Beautiful Soup, python-dotenv
- **Frontend:** Vanilla HTML, CSS, JavaScript
- **AI:** [Featherless API](https://featherless.ai/docs)

## License

MIT
