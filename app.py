"""
Minimal backend: URL or text + question -> Featherless AI answer.
API key from .env; never exposed to frontend.
"""
import os
import re

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()

app = Flask(__name__, static_folder=".", static_url_path="")
API_KEY = os.getenv("FEATHERLESS_API_KEY")
FEATHERLESS_URL = "https://api.featherless.ai/v1/chat/completions"
MAX_TEXT_CHARS = 4000

def is_url(s: str) -> bool:
    s = s.strip()
    return re.match(r"^https?://", s, re.I) is not None


def extract_visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "head", "nav", "footer"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def get_text_from_url(url: str) -> str:
    resp = requests.get(url, headers=BROWSER_HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    text = extract_visible_text(resp.text)
    return text[:MAX_TEXT_CHARS] if len(text) > MAX_TEXT_CHARS else text


def ask_ai(content: str, question: str) -> str:
    if not API_KEY or API_KEY == "PUT_YOUR_KEY_HERE":
        raise ValueError("FEATHERLESS_API_KEY is not set in .env")
    payload = {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "messages": [
            {"role": "system", "content": "Answer the user's question based only on the provided text. Be concise."},
            {"role": "user", "content": f"Text:\n{content}\n\nQuestion: {question}"},
        ],
        "max_tokens": 500,
        "temperature": 0.3,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    r = requests.post(FEATHERLESS_URL, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()
    choice = data.get("choices", [{}])[0]
    message = choice.get("message", {})
    return message.get("content", "").strip() or "(No response)"


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/nozylot.ico")
def favicon():
    return send_from_directory(".", "nozylot.ico", mimetype="image/x-icon")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        body = request.get_json() or {}
        url = (body.get("url") or "").strip()
        text = (body.get("text") or "").strip()
        question = (body.get("question") or "").strip()

        if not question:
            return jsonify({"error": "question is required"}), 400

        if url and text:
            return jsonify({"error": "provide either url or text, not both"}), 400
        if not url and not text:
            return jsonify({"error": "provide url or text"}), 400

        if url:
            if not is_url(url):
                return jsonify({"error": "invalid url"}), 400
            try:
                content = get_text_from_url(url)
            except requests.RequestException:
                return jsonify({
                    "error": "This site blocked the request (e.g. 403). Try pasting the page text manually in the text box instead."
                }), 422
        else:
            content = text[:MAX_TEXT_CHARS] if len(text) > MAX_TEXT_CHARS else text

        if not content:
            return jsonify({"error": "no text could be extracted"}), 422

        answer = ask_ai(content, question)
        return jsonify({"answer": answer})
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except requests.RequestException as e:
        return jsonify({"error": f"AI request failed: {e}"}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
