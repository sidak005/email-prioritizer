import time
from typing import Dict, List
from collections import defaultdict
from datetime import datetime, timedelta


class MetricsCollector:
    """Collect and track performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "total_emails_processed": 0,
            "total_processing_time_ms": 0,
            "average_latency_ms": 0,
            "priority_accuracy": 0,
            "response_generation_count": 0,
            "errors": 0,
            "requests_per_hour": defaultdict(int),
            "latency_distribution": {
                "<50ms": 0,
                "50-100ms": 0,
                "100-200ms": 0,
                ">200ms": 0
            }
        }
        self.start_time = datetime.now()
    
    def record_email_processing(self, latency_ms: float, success: bool = True):
        """Record email processing metrics"""
        self.metrics["total_emails_processed"] += 1
        if success:
            self.metrics["total_processing_time_ms"] += latency_ms
            self.metrics["average_latency_ms"] = (
                self.metrics["total_processing_time_ms"] / 
                self.metrics["total_emails_processed"]
            )
            
            # Categorize latency
            if latency_ms < 50:
                self.metrics["latency_distribution"]["<50ms"] += 1
            elif latency_ms < 100:
                self.metrics["latency_distribution"]["50-100ms"] += 1
            elif latency_ms < 200:
                self.metrics["latency_distribution"]["100-200ms"] += 1
            else:
                self.metrics["latency_distribution"][">200ms"] += 1
        else:
            self.metrics["errors"] += 1
    
    def record_response_generation(self):
        """Record response generation"""
        self.metrics["response_generation_count"] += 1
    
    def record_priority_feedback(self, correct: bool):
        """Record priority accuracy feedback"""
        # Simple accuracy tracking (can be enhanced)
        if correct:
            self.metrics["priority_accuracy"] = min(100, self.metrics["priority_accuracy"] + 0.1)
        else:
            self.metrics["priority_accuracy"] = max(0, self.metrics["priority_accuracy"] - 0.1)
    
    def get_metrics(self) -> Dict:
        """Get all metrics"""
        uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
        
        return {
            **self.metrics,
            "uptime_hours": round(uptime_hours, 2),
            "throughput_per_hour": round(
                self.metrics["total_emails_processed"] / max(uptime_hours, 0.01),
                2
            ),
            "success_rate": round(
                (self.metrics["total_emails_processed"] - self.metrics["errors"]) /
                max(self.metrics["total_emails_processed"], 1) * 100,
                2
            )
        }
    
    def reset(self):
        """Reset metrics"""
        self.__init__()
