from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from typing import Dict, List, Optional
import torch
from backend.app.config import settings


class LLMService:
    def __init__(self):
        self.sentiment_analyzer = None
        self.text_generator = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.use_api = True  # Use Hugging Face API for generation (faster)
    
    async def initialize(self):
        """Initialize LLM models"""
        print("Loading LLM models...")
        
        # Sentiment analysis (lightweight, can run locally)
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if self.device == "cuda" else -1
            )
            print("✅ Sentiment analyzer loaded")
        except Exception as e:
            print(f"⚠️ Could not load sentiment analyzer: {e}")
        
        # For text generation, we'll use Hugging Face API (more efficient)
        # Or use a smaller model locally
        if not self.use_api:
            try:
                model_name = "microsoft/DialoGPT-medium"  # Smaller model
                self.text_generator = pipeline(
                    "text-generation",
                    model=model_name,
                    device=0 if self.device == "cuda" else -1
                )
                print("✅ Text generator loaded")
            except Exception as e:
                print(f"⚠️ Could not load text generator: {e}")
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        if self.sentiment_analyzer is None:
            return {"label": "NEUTRAL", "score": 0.5}
        
        try:
            result = self.sentiment_analyzer(text[:512])[0]  # Limit length
            return {
                "label": result["label"],
                "score": result["score"]
            }
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {"label": "NEUTRAL", "score": 0.5}
    
    def classify_intent(self, text: str, subject: str) -> str:
        """Classify email intent using keyword matching and simple heuristics"""
        # Combine subject and body for analysis
        combined_text = f"{subject} {text}".lower()
        
        # Intent keywords
        intent_keywords = {
            "action_required": ["urgent", "asap", "deadline", "required", "need", "please", "action"],
            "question": ["?", "question", "wondering", "ask", "help"],
            "meeting": ["meeting", "call", "schedule", "calendar", "zoom", "teams"],
            "newsletter": ["newsletter", "unsubscribe", "subscribe"],
            "promotional": ["sale", "discount", "offer", "deal", "promo"],
            "spam": ["click here", "limited time", "act now", "winner", "prize"]
        }
        
        scores = {}
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            scores[intent] = score
        
        # Get intent with highest score
        if max(scores.values()) == 0:
            return "information"
        
        return max(scores, key=scores.get)
    
    async def generate_response(
        self,
        email_subject: str,
        email_body: str,
        tone: str = "professional"
    ) -> str:
        """Generate email response using Hugging Face API"""
        import httpx
        
        # Use Hugging Face Inference API
        api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
        
        prompt = f"""Generate a {tone} email response to the following email:

Subject: {email_subject}
Body: {email_body[:500]}

Response:"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_url,
                    headers=headers,
                    json={"inputs": prompt, "max_length": 200},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "")
                        # Extract just the response part
                        if "Response:" in generated_text:
                            return generated_text.split("Response:")[-1].strip()
                        return generated_text.strip()
        except Exception as e:
            print(f"Error generating response via API: {e}")
        
        # Fallback: simple template-based response
        return self._generate_fallback_response(email_subject, tone)
    
    def _generate_fallback_response(self, subject: str, tone: str) -> str:
        """Fallback response generator"""
        greetings = {
            "professional": "Thank you for your email.",
            "casual": "Thanks for reaching out!",
            "friendly": "Hi! Thanks for your message."
        }
        
        return f"{greetings.get(tone, greetings['professional'])} I'll get back to you soon regarding: {subject}"
