from typing import Dict, List
from datetime import datetime
from backend.app.config import settings
from backend.app.models.email import PriorityLevel, EmailIntent
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.pinecone_service import PineconeService
from backend.app.services.llm_service import LLMService


class PriorityService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        pinecone_service: PineconeService,
        llm_service: LLMService
    ):
        self.embedding_service = embedding_service
        self.pinecone_service = pinecone_service
        self.llm_service = llm_service
        
        # Priority weights
        self.weights = {
            "sender_importance": 0.25,
            "urgency_keywords": 0.20,
            "intent": 0.20,
            "sentiment": 0.15,
            "time_sensitivity": 0.10,
            "similar_emails": 0.10
        }
        
        # Urgency keywords with scores
        self.urgency_keywords = {
            "urgent": 10,
            "asap": 10,
            "immediate": 9,
            "deadline": 8,
            "important": 7,
            "critical": 9,
            "emergency": 10,
            "today": 6,
            "now": 8,
            "required": 7
        }
        self.low_urgency_phrases = [
            "not important", "not urgent", "not critical", "whenever you want",
            "whenever you can", "no rush", "low priority", "not a priority",
            "take your time", "when you get a chance", "no hurry"
        ]
        self.strong_urgency_phrases = [
            "very important", "really important", "extremely important", "highly important",
            "as soon as possible", "asap", "send it as soon as possible",
            "need it urgently", "top priority", "highest priority", "critically important"
        ]
    
    async def calculate_priority(
        self,
        subject: str,
        body: str,
        sender: str,
        received_at: datetime,
        user_id: str
    ) -> Dict:
        import time
        start_time = time.time()

        intent = self.llm_service.classify_intent(body, subject)
        sentiment_result = self.llm_service.analyze_sentiment(f"{subject} {body}")

        if getattr(settings, "use_llm_priority", True):
            llm_priority = self.llm_service.classify_priority_llm(subject, body)
            if llm_priority is not None:
                try:
                    priority_level = PriorityLevel(llm_priority["priority_level"])
                except ValueError:
                    priority_level = PriorityLevel.NORMAL
                priority_score = min(100, max(0, float(llm_priority.get("priority_score", 50))))
                if intent == "spam":
                    priority_level = PriorityLevel.SPAM
                processing_time = (time.time() - start_time) * 1000
                sender_importance = await self._calculate_sender_importance(sender, user_id)
                return {
                    "priority_score": round(priority_score, 2),
                    "priority_level": priority_level,
                    "intent": intent,
                    "sentiment": sentiment_result.get("label", "NEUTRAL"),
                    "urgency_keywords": self._extract_urgency_keywords(subject, body),
                    "sender_importance": round(sender_importance, 2),
                    "processing_time_ms": round(processing_time, 2),
                }
        # Fallback: rule-based (no API or LLM failed)
        sentiment_score = sentiment_result.get("score", 0.5)
        urgency_score = self._calculate_urgency_score(subject, body)
        sender_importance = await self._calculate_sender_importance(sender, user_id)
        time_sensitivity = self._calculate_time_sensitivity(received_at)
        similar_emails_score = await self._get_similar_emails_priority(subject, body)
        priority_score = (
            sender_importance * self.weights["sender_importance"] * 100 +
            urgency_score * self.weights["urgency_keywords"] * 100 +
            (1.0 if intent in ["action_required", "question"] else 0.5) * self.weights["intent"] * 100 +
            sentiment_score * self.weights["sentiment"] * 100 +
            time_sensitivity * self.weights["time_sensitivity"] * 100 +
            similar_emails_score * self.weights["similar_emails"] * 100
        )
        text_lower = f"{subject} {body}".lower()
        has_strong_importance = any(phrase in text_lower for phrase in self.strong_urgency_phrases)
        if any(phrase in text_lower for phrase in self.low_urgency_phrases):
            priority_score -= 15
        elif has_strong_importance:
            priority_score += 28
        priority_score = min(100, max(0, priority_score))
        priority_level = self._score_to_level(priority_score, intent)
        if has_strong_importance and intent != "spam":
            priority_level = PriorityLevel.URGENT
            if priority_score < 80:
                priority_score = min(100, 80.0)
        processing_time = (time.time() - start_time) * 1000
        return {
            "priority_score": round(priority_score, 2),
            "priority_level": priority_level,
            "intent": intent,
            "sentiment": sentiment_result.get("label", "NEUTRAL"),
            "urgency_keywords": self._extract_urgency_keywords(subject, body),
            "sender_importance": round(sender_importance, 2),
            "processing_time_ms": round(processing_time, 2)
        }
    
    def _calculate_urgency_score(self, subject: str, body: str) -> float:
        import re
        text = f"{subject} {body}".lower()
        max_score = max(self.urgency_keywords.values())

        for phrase in self.low_urgency_phrases:
            if phrase in text:
                return 0.2  # low urgency so "not important" → LOW priority

        strong_boost = 0.0
        for phrase in self.strong_urgency_phrases:
            if phrase in text:
                strong_boost = 0.95  # push toward high/urgent
                break

        negated_important = re.search(r'\bnot\s+important\b', text) or "not important" in text
        negated_urgent = re.search(r'\bnot\s+urgent\b', text) or "not urgent" in text

        found_keywords = []
        total_score = 0
        time_modifier = 1.0
        time_based_urgency = 0.0

        near_deadline = re.search(
            r'(?:in\s+(\d+)\s+day|(\d+)\s+day\s+(?:left|remaining|to\s+go|until)|due\s+in\s+(\d+)\s+day)',
            text, re.I
        )
        in_days = re.findall(r'in\s+(\d+)\s+days?', text)
        days_only = re.findall(r'(\d+)\s+days?\s+(?:from\s+now|away|left|remaining)', text)
        all_days = []
        for m in in_days:
            all_days.append(int(m))
        for m in days_only:
            all_days.append(int(m))
        if near_deadline:
            g = near_deadline.groups()
            for x in g:
                if x and x.isdigit():
                    all_days.append(int(x))
                    break
        
        if all_days:
            d = min(all_days)
            if d <= 1:
                time_based_urgency = 0.95
            elif d <= 2:
                time_based_urgency = 0.85
            elif d <= 3:
                time_based_urgency = 0.75
            elif d <= 7:
                time_based_urgency = 0.6
            elif d <= 14:
                time_modifier = 0.8
            elif d <= 30:
                time_modifier = 0.6
            elif d <= 50:
                time_modifier = 0.4
            else:
                time_modifier = 0.2
        
        # "today" / "tomorrow" / "in X hours"
        if re.search(r'\b(?:today|tomorrow|this\s+week)\b', text):
            time_based_urgency = max(time_based_urgency, 0.9)
        hours = re.findall(r'in\s+(\d+)\s+hours?', text)
        if hours and int(hours[0]) <= 24:
            time_based_urgency = max(time_based_urgency, 0.9)
        
        # Far future
        after = re.findall(r'after\s+(\d+)\s+days?', text)
        for m in after:
            try:
                d = int(m)
                if d >= 50:
                    time_modifier = min(time_modifier, 0.2)
                elif d >= 30:
                    time_modifier = min(time_modifier, 0.4)
                elif d >= 14:
                    time_modifier = min(time_modifier, 0.6)
            except ValueError:
                pass
        
        for keyword, score in self.urgency_keywords.items():
            if keyword in text:
                # Don't count "important" if text says "not important"
                if keyword == "important" and negated_important:
                    continue
                if keyword == "urgent" and negated_urgent:
                    continue
                found_keywords.append(keyword)
                total_score += score

        if total_score > 0:
            base = min(1.0, total_score / (max_score * 2))
            base = base * time_modifier
        else:
            base = 0.0

        # time-based urgency
        final = max(base, time_based_urgency * time_modifier)
        # Apply strong importance boost (e.g. "very important", "as soon as possible")
        if strong_boost > 0:
            final = max(final, strong_boost)
        return min(1.0, max(0.0, final))
    
    def _extract_urgency_keywords(self, subject: str, body: str) -> List[str]:
        text = f"{subject} {body}".lower()
        return [kw for kw in self.urgency_keywords.keys() if kw in text]
    
    async def _calculate_sender_importance(self, sender: str, user_id: str) -> float:
        """Calculate sender importance score (0.0 to 1.0)"""
        sender_lower = sender.lower()
        
        important_domains = ["@company.com", "@work.com", "@official", "noreply", "no-reply"]
        if any(domain in sender_lower for domain in important_domains):
            if "noreply" in sender_lower or "no-reply" in sender_lower:
                return 0.3
            return 0.8
        
        personal_domains = ["@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com"]
        if any(domain in sender_lower for domain in personal_domains):
            return 0.5
        
        return 0.5
    
    def _calculate_time_sensitivity(self, received_at: datetime) -> float:
        hour = received_at.hour
        
        if 9 <= hour <= 17:
            return 0.8
        elif 8 <= hour <= 20:
            return 0.6
        else:
            return 0.4
    
    async def _get_similar_emails_priority(self, subject: str, body: str) -> float:
        try:
            embedding = self.embedding_service.generate_embedding(f"{subject} {body}")
            similar = await self.pinecone_service.search_similar_emails(embedding, top_k=3)
            
            if not similar:
                return 0.5  
            total_score = 0
            count = 0
            
            for match in similar:
                metadata = match.get("metadata", {})
                if "priority_score" in metadata:
                    total_score += metadata["priority_score"] / 100
                    count += 1
            
            if count == 0:
                return 0.5
            
            return total_score / count
        except Exception as e:
            print(f"Error getting similar emails priority: {e}")
            return 0.5
    
    def _score_to_level(self, score: float, intent: str) -> PriorityLevel:
        if intent == "spam":
            return PriorityLevel.SPAM
        
        if score >= 80:
            return PriorityLevel.URGENT
        elif score >= 60:
            return PriorityLevel.HIGH
        elif score >= 40:
            return PriorityLevel.NORMAL
        else:
            return PriorityLevel.LOW
