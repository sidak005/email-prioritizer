from typing import Dict, List
from datetime import datetime
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
    
    async def calculate_priority(
        self,
        subject: str,
        body: str,
        sender: str,
        received_at: datetime,
        user_id: str
    ) -> Dict:
        """Calculate priority score and level for an email"""
        import time
        start_time = time.time()
        
        # 1. Analyze intent
        intent = self.llm_service.classify_intent(body, subject)
        
        # 2. Analyze sentiment
        sentiment_result = self.llm_service.analyze_sentiment(f"{subject} {body}")
        sentiment_score = sentiment_result.get("score", 0.5)
        
        # 3. Check urgency keywords
        urgency_score = self._calculate_urgency_score(subject, body)
        
        # 4. Calculate sender importance (simplified - can be enhanced with history)
        sender_importance = await self._calculate_sender_importance(sender, user_id)
        
        # 5. Time sensitivity (emails received during work hours get slight boost)
        time_sensitivity = self._calculate_time_sensitivity(received_at)
        
        # 6. Similar emails priority (check if similar emails were high priority)
        similar_emails_score = await self._get_similar_emails_priority(subject, body)
        
        # Calculate weighted priority score (0-100)
        priority_score = (
            sender_importance * self.weights["sender_importance"] * 100 +
            urgency_score * self.weights["urgency_keywords"] * 100 +
            (1.0 if intent in ["action_required", "question"] else 0.5) * self.weights["intent"] * 100 +
            sentiment_score * self.weights["sentiment"] * 100 +
            time_sensitivity * self.weights["time_sensitivity"] * 100 +
            similar_emails_score * self.weights["similar_emails"] * 100
        )
        
        # Normalize to 0-100
        priority_score = min(100, max(0, priority_score))
        
        # Determine priority level
        priority_level = self._score_to_level(priority_score, intent)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
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
        """Calculate urgency score based on keywords and time context"""
        import re
        text = f"{subject} {body}".lower()
        max_score = max(self.urgency_keywords.values())
        
        found_keywords = []
        total_score = 0
        time_modifier = 1.0
        time_based_urgency = 0.0  # Urgency from "in X days" etc. when no keywords
        
        # Near-term deadlines: "in 1 day", "in 2 days", "1 day", etc.
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
                time_based_urgency = 0.95   # "in 1 day" → very high
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
        
        # "today" / "tomorrow" / "in X hours" → boost
        if re.search(r'\b(?:today|tomorrow|this\s+week)\b', text):
            time_based_urgency = max(time_based_urgency, 0.9)
        hours = re.findall(r'in\s+(\d+)\s+hours?', text)
        if hours and int(hours[0]) <= 24:
            time_based_urgency = max(time_based_urgency, 0.9)
        
        # Far future: "after X days" (distant) → reduce
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
        
        # Keyword-based urgency
        for keyword, score in self.urgency_keywords.items():
            if keyword in text:
                found_keywords.append(keyword)
                total_score += score
        
        if total_score > 0:
            base = min(1.0, total_score / (max_score * 2))
            base = base * time_modifier
        else:
            base = 0.0
        
        # Use time-based urgency when we have "in 1 day" etc. but no keywords
        final = max(base, time_based_urgency * time_modifier)
        return min(1.0, max(0.0, final))
    
    def _extract_urgency_keywords(self, subject: str, body: str) -> List[str]:
        """Extract found urgency keywords"""
        text = f"{subject} {body}".lower()
        return [kw for kw in self.urgency_keywords.keys() if kw in text]
    
    async def _calculate_sender_importance(self, sender: str, user_id: str) -> float:
        """Calculate sender importance (0-1)"""
        # TODO: Enhance with historical data from database
        # For now, use simple heuristics:
        # - Known contacts: higher importance
        # - Domain-based: work emails > personal > unknown
        
        # Check if sender is in user's contacts (would query database)
        # For now, return default
        return 0.5  # Default importance
    
    def _calculate_time_sensitivity(self, received_at: datetime) -> float:
        """Calculate time sensitivity based on when email was received"""
        hour = received_at.hour
        
        # Work hours (9 AM - 5 PM) get higher score
        if 9 <= hour <= 17:
            return 0.8
        elif 8 <= hour <= 20:
            return 0.6
        else:
            return 0.4
    
    async def _get_similar_emails_priority(self, subject: str, body: str) -> float:
        """Get priority score based on similar emails"""
        try:
            # Generate embedding
            embedding = self.embedding_service.generate_embedding(f"{subject} {body}")
            
            # Search for similar emails
            similar = await self.pinecone_service.search_similar_emails(embedding, top_k=3)
            
            if not similar:
                return 0.5  # Default
            
            # Average priority of similar emails
            total_score = 0
            count = 0
            
            for match in similar:
                metadata = match.get("metadata", {})
                if "priority_score" in metadata:
                    total_score += metadata["priority_score"] / 100  # Normalize
                    count += 1
            
            if count == 0:
                return 0.5
            
            return total_score / count
        except Exception as e:
            print(f"Error getting similar emails priority: {e}")
            return 0.5
    
    def _score_to_level(self, score: float, intent: str) -> PriorityLevel:
        """Convert priority score to level"""
        # Override for spam
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
