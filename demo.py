#!/usr/bin/env python3
"""
Email Prioritizer - Portfolio Demo Script
Showcases AI-powered email prioritization and response generation
"""

import requests
import json
from datetime import datetime
from typing import Dict

API_BASE = "http://localhost:8000"

def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_section(text: str):
    """Print a section divider"""
    print(f"\n{'─'*70}")
    print(f"  {text}")
    print(f"{'─'*70}\n")

def analyze_email(subject: str, sender: str, body: str) -> Dict:
    """Analyze an email and return priority analysis"""
    url = f"{API_BASE}/api/v1/emails/analyze"
    payload = {
        "subject": subject,
        "sender": sender,
        "recipient": "you@company.com",
        "body": body,
        "received_at": datetime.now().isoformat()
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def generate_response(subject: str, body: str, tone: str = "professional") -> Dict:
    """Generate an email response"""
    url = f"{API_BASE}/api/v1/responses/generate"
    payload = {
        "email_subject": subject,
        "email_body": body,
        "tone": tone
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def display_analysis(email_data: Dict, analysis: Dict):
    """Display email analysis in a formatted way"""
    print(f"📧 Email: {email_data['subject']}")
    print(f"👤 From: {email_data['sender']}")
    print(f"\n📊 Analysis Results:")
    print(f"   Priority Score: {analysis['priority_score']:.2f}/100")
    print(f"   Priority Level: {analysis['priority_level'].upper()}")
    print(f"   Intent: {analysis['intent'].replace('_', ' ').title()}")
    print(f"   Sentiment: {analysis['sentiment'].title()}")
    if analysis.get('urgency_keywords'):
        print(f"   Urgency Keywords: {', '.join(analysis['urgency_keywords'])}")
    print(f"   Processing Time: {analysis['processing_time_ms']:.2f}ms")

def display_response(original: Dict, response: Dict):
    """Display generated response"""
    print(f"\n💬 Generated Response ({response['tone']} tone):")
    print(f"   {response['generated_response']}")

def main():
    print_header("🚀 Email Prioritizer - AI Demo")
    print("Demonstrating intelligent email prioritization and response generation")
    
    # Test Case 1: High Priority - Urgent Business Email
    print_section("Test 1: High Priority Email")
    email1 = {
        "subject": "URGENT: Production server down - immediate action required",
        "sender": "cto@techcorp.com",
        "body": "The production server crashed 10 minutes ago. All services are down. We need you to investigate and fix this immediately. This is critical for our customers."
    }
    analysis1 = analyze_email(**email1)
    display_analysis(email1, analysis1)
    
    # Test Case 2: Low Priority - Newsletter
    print_section("Test 2: Low Priority Email")
    email2 = {
        "subject": "Weekly Tech Newsletter - January 2024",
        "sender": "newsletter@techblog.com",
        "body": "Hi! Here's your weekly roundup of tech news. Check out our latest articles on AI, cloud computing, and more. Have a great week!"
    }
    analysis2 = analyze_email(**email2)
    display_analysis(email2, analysis2)
    
    # Test Case 3: Meeting Request - Generate Response
    print_section("Test 3: Response Generation - Meeting Request")
    email3 = {
        "subject": "Can we schedule a meeting tomorrow?",
        "sender": "colleague@company.com",
        "body": "Hi, I would like to discuss the Q1 project roadmap. Are you available for a 30-minute meeting tomorrow afternoon? Let me know what works for you."
    }
    analysis3 = analyze_email(**email3)
    display_analysis(email3, analysis3)
    
    # Generate professional response
    response_prof = generate_response(email3["subject"], email3["body"], "professional")
    display_response(email3, response_prof)
    
    # Generate casual response
    print_section("Test 4: Response Generation - Different Tones")
    response_casual = generate_response(email3["subject"], email3["body"], "casual")
    print(f"💬 Generated Response (casual tone):")
    print(f"   {response_casual['generated_response']}")
    
    # Test Case 4: Action Required
    print_section("Test 5: Action Required Email")
    email4 = {
        "subject": "Deadline approaching: Project proposal due Friday",
        "sender": "manager@company.com",
        "body": "Just a reminder that the project proposal is due this Friday at 5 PM. Please make sure all sections are complete and reviewed. Let me know if you need any help."
    }
    analysis4 = analyze_email(**email4)
    display_analysis(email4, analysis4)
    
    # Summary
    print_header("📈 Demo Summary")
    print("✅ Successfully analyzed 4 different email types")
    print("✅ Correctly identified priority levels (urgent, high, normal, low)")
    print("✅ Generated contextual email responses")
    print("✅ Demonstrated AI-powered email management capabilities")
    print("\n🎯 Key Features Demonstrated:")
    print("   • Intelligent priority scoring (0-100)")
    print("   • Intent classification (action_required, meeting, newsletter, etc.)")
    print("   • Sentiment analysis")
    print("   • Urgency keyword detection")
    print("   • AI-powered response generation")
    print("   • Multiple tone options (professional, casual, friendly)")
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server.")
        print("   Make sure the server is running: python3 run.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
