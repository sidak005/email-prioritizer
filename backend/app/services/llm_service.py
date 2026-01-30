from typing import Dict, List, Optional

from backend.app.config import settings

# Lazy imports for local models (dev only); production uses HF API

HF_SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"


class LLMService:
    def __init__(self):
        self.sentiment_analyzer = None
        self.text_generator = None
        self.use_api = settings.environment == "production"

    async def initialize(self):
        if self.use_api:
            return
        
        try:
            from transformers import pipeline
            import torch
            device = 0 if torch.cuda.is_available() else -1
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=HF_SENTIMENT_MODEL,
                device=device,
            )
        except ImportError:
            self.use_api = True

    def analyze_sentiment(self, text: str) -> Dict:
        if self.use_api:
            return self._sentiment_via_api(text)
        if self.sentiment_analyzer is None:
            return {"label": "NEUTRAL", "score": 0.5}
        
        r = self.sentiment_analyzer(text[:512])[0]
        return {"label": r["label"], "score": r["score"]}

    def _sentiment_via_api(self, text: str) -> Dict:
        import httpx
        url = f"https://api-inference.huggingface.co/models/{HF_SENTIMENT_MODEL}"
        headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
        
        try:
            with httpx.Client(timeout=30.0) as client:
                r = client.post(url, headers=headers, json={"inputs": text[:512]})
                r.raise_for_status()
                out = r.json()
                if isinstance(out, list) and out:
                    e = out[0]
                    if isinstance(e, dict):
                        return {
                            "label": e.get("label", "NEUTRAL"),
                            "score": float(e.get("score", 0.5)),
                        }
        except Exception:
            pass
        return {"label": "NEUTRAL", "score": 0.5}

    def classify_intent(self, text: str, subject: str) -> str:
        combined = f"{subject} {text}".lower()
        intent_keywords = {
            "action_required": ["urgent", "asap", "deadline", "required", "need", "please", "action", "very important", "really important", "as soon as possible", "send it as soon as possible"],
            "question": ["?", "question", "wondering", "ask", "help"],
            "meeting": ["meeting", "call", "schedule", "calendar", "zoom", "teams"],
            "newsletter": ["newsletter", "unsubscribe", "subscribe"],
            "promotional": ["sale", "discount", "offer", "deal", "promo"],
            "spam": ["click here", "limited time", "act now", "winner", "prize"],
        }
        scores = {k: sum(1 for w in v if w in combined) for k, v in intent_keywords.items()}
        if max(scores.values()) == 0:
            return "information"
        return max(scores, key=scores.get)

    async def generate_response(
        self,
        email_subject: str,
        email_body: str,
        tone: str = "professional",
    ) -> str:
        import httpx
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
        prompt = f"Generate a {tone} email response to the following email:\n\nSubject: {email_subject}\nBody: {email_body[:500]}\n\nResponse:"
        
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    url,
                    headers=headers,
                    json={"inputs": prompt, "max_length": 200},
                    timeout=30.0,
                )
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list) and data:
                        raw = data[0].get("generated_text", "")
                        if "Response:" in raw:
                            return raw.split("Response:")[-1].strip()
                        return raw.strip()
        except Exception:
            pass
        return self._generate_fallback_response(email_subject, tone)

    def _generate_fallback_response(self, subject: str, tone: str) -> str:
        greetings = {
            "professional": "Thank you for your email.",
            "casual": "Thanks for reaching out!",
            "friendly": "Hi! Thanks for your message.",
        }
        return f"{greetings.get(tone, greetings['professional'])} I'll get back to you soon regarding: {subject}"
