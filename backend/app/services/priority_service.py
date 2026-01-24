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
        
        # Check for time-based urgency modifiers (reduce score if deadline is far)
        time_modifier = 1.0  # Default: no reduction
        
        # Patterns that indicate far future deadlines (reduce urgency)
        far_future_patterns = [
            r'after\s+(\d+)\s+days?',
            r'in\s+(\d+)\s+days?',
            r'(\d+)\s+days?\s+from\s+now',
            r'(\d+)\s+days?\s+away',
            r'deadline.*?(\d+)\s+days?',
        ]
        
        # Patterns that indicate near future (increase urgency)
        near_future_patterns = [
            r'today',
            r'tomorrow',
            r'this\s+week',
            r'in\s+(\d+)\s+hours?',
            r'(\d+)\s+hours?\s+from\s+now',
        ]
        
        # Check for far future deadlines
        for pattern in far_future_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                try:
                    days = int(match) if match.isdigit() else 0
                    if days > 7:  # More than a week away
                        # Reduce urgency: 50+ days = very low, 7-50 days = moderate reduction
                        if days >= 50:
                            time_modifier = 0.2  # Very low urgency
                        elif days >= 30:
                            time_modifier = 0.4
                        elif days >= 14:
                            time_modifier = 0.6
                        else:  # 7-14 days
                            time_modifier = 0.8
                        break
                except (ValueError, AttributeError):
                    pass
        
        # Check for near future (increase urgency)
        for pattern in near_future_patterns:
            if re.search(pattern, text):
                time_modifier = 1.2  # Boost urgency
                break
        
        # Calculate keyword-based urgency
        for keyword, score in self.urgency_keywords.items():
            if keyword in text:
                found_keywords.append(keyword)
                total_score += score
        
        # Normalize to 0-1
        if total_score == 0:
            return 0.0
        
        base_score = min(1.0, total_score / (max_score * 2))
        
        # Apply time modifier (but don't go below 0 or above 1)
        final_score = base_score * time_modifier
        return min(1.0, max(0.0, final_score))
    
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
