#!/usr/bin/env python3
"""
Example usage of AI Usage Tracker
Demonstrates all major features and API calls.
"""

import time
import requests
from ai_usage_tracker import AIUsageTracker

def main():
    """Run example usage scenarios."""
    print("🤖 AI Usage Tracker - Example Usage")
    print("=" * 50)
    
    # Initialize tracker
    tracker = AIUsageTracker("example.db")
    print("✅ Tracker initialized")
    
    # 1. Set up credits
    print("\n💰 Setting up credits...")
    
    # Add subscription
    sub_id = tracker.add_subscription("OpenAI Pro", 20.00, 30)
    print(f"✅ Added subscription: {sub_id}")
    
    # Purchase credits
    purchase_id = tracker.add_credit_purchase(10.00, "Initial purchase")
    print(f"✅ Purchased credits: {purchase_id}")
    
    # Check balance
    balance = tracker.get_credit_balance()
    print(f"💳 Total credits: ${balance['total_credits']:.2f}")
    
    # 2. Log some jobs
    print("\n📝 Logging AI jobs...")
    
    jobs = [
        {
            "name": "Code Generation",
            "model": "gpt-4o",
            "input_text": "Write a Python function to calculate fibonacci numbers",
            "output_text": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "description": "Generated fibonacci function"
        },
        {
            "name": "Text Summary",
            "model": "claude-3-sonnet",
            "input_text": "Long article about AI trends...",
            "output_text": "Key AI trends include: 1. Multimodal models, 2. Agent frameworks, 3. Local deployment",
            "description": "Summarized AI article"
        },
        {
            "name": "Translation",
            "model": "gemini-pro", 
            "input_text": "Hello, how are you today?",
            "output_text": "مرحبا، كيف حالك اليوم؟",
            "description": "English to Arabic translation"
        }
    ]
    
    job_ids = []
    for job in jobs:
        job_id, result = tracker.log_job(**job)
        job_ids.append(job_id)
        print(f"✅ Logged job: {job['name']} - ${result['total_cost']:.6f}")
    
    # 3. View analytics
    print("\n📊 Usage analytics...")
    
    stats = tracker.get_usage_stats(30)
    print(f"Total jobs: {stats['total_jobs']}")
    print(f"Total cost: ${stats['total_cost']:.6f}")
    print(f"Average per job: ${stats['average_cost_per_job']:.6f}")
    
    print("\nTop models:")
    for model in stats['by_model'][:3]:
        print(f"  {model['model']}: {model['jobs']} jobs, ${model['cost']:.6f}")
    
    # 4. Check updated balance
    print("\n💰 Updated balance...")
    
    balance = tracker.get_credit_balance()
    print(f"Total spent: ${balance['total_spent']:.6f}")
    print(f"Remaining: ${balance['remaining_credits']:.6f}")
    
    # 5. List recent jobs
    print("\n📋 Recent jobs...")
    
    recent = tracker.list_recent_jobs(5)
    for job in recent:
        print(f"  {job['name']} ({job['model']}) - ${job['cost']:.6f}")
    
    print("\n🎉 Example completed! Check example.db for data.")


def api_example():
    """Example using the REST API."""
    print("\n🌐 API Example")
    print("=" * 30)
    
    API_BASE = "http://localhost:8001"
    
    try:
        # Check API health
        response = requests.get(f"{API_BASE}/health")
        if response.status_code != 200:
            print("❌ API not running. Start with: python ai-tracker-api.py")
            return
        
        print("✅ API is running")
        
        # Get balance
        balance = requests.get(f"{API_BASE}/balance").json()
        print(f"💰 Balance: ${balance['remaining_credits']:.6f}")
        
        # Log a job via API
        job_data = {
            "name": "API Test Job",
            "model": "gpt-4o-mini",
            "input_text": "Test input via API",
            "output_text": "Test output via API",
            "description": "Example API usage"
        }
        
        response = requests.post(f"{API_BASE}/jobs", json=job_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job logged via API: ${result['total_cost']:.6f}")
        
        # Get stats
        stats = requests.get(f"{API_BASE}/stats?days=30").json()
        print(f"📊 Total jobs: {stats['total_jobs']}")
        
    except requests.exceptions.ConnectionError:
        print("❌ API not running. Start with: python ai-tracker-api.py")


if __name__ == "__main__":
    main()
    
    # Uncomment to test API
    # api_example()