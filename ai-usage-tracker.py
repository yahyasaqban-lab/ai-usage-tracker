#!/usr/bin/env python3
"""
AI Usage Tracker with Credit Management
Track AI usage, manage credits, subscriptions, and job costs.
"""

import json
import sqlite3
import argparse
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

# Enhanced token counting (from previous calculator)
def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Approximate token count for text."""
    text = re.sub(r'\s+', ' ', text.strip())
    char_count = len(text)
    return int(char_count / 4)  # Rough approximation


@dataclass
class ModelPricing:
    """Pricing info for an AI model."""
    input_per_1k: float
    output_per_1k: float
    context_window: int
    notes: str = ""


@dataclass
class Subscription:
    """User subscription details."""
    id: str
    name: str
    credits: float  # Monthly credits in $
    expires_at: str
    created_at: str
    active: bool = True


@dataclass
class CreditPurchase:
    """One-time credit purchase."""
    id: str
    amount: float  # Credits in $
    purchased_at: str
    notes: str = ""


@dataclass
class Job:
    """AI job/task tracking."""
    id: str
    name: str
    description: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    created_at: str
    metadata: Dict = None


# Current AI model pricing (March 2026)
MODEL_PRICING: Dict[str, ModelPricing] = {
    # OpenAI
    "gpt-4o": ModelPricing(0.0025, 0.01, 128000, "GPT-4 Omni"),
    "gpt-4o-mini": ModelPricing(0.00015, 0.0006, 128000, "GPT-4 Omni Mini"),
    "o1": ModelPricing(0.015, 0.06, 200000, "o1 reasoning model"),
    "o3-mini": ModelPricing(0.002, 0.008, 128000, "o3 Mini"),
    
    # Anthropic
    "claude-3-opus": ModelPricing(0.015, 0.075, 200000, "Claude 3 Opus"),
    "claude-3-sonnet": ModelPricing(0.003, 0.015, 200000, "Claude 3 Sonnet"),
    "claude-3-haiku": ModelPricing(0.00025, 0.00125, 200000, "Claude 3 Haiku"),
    "claude-sonnet-4": ModelPricing(0.003, 0.015, 200000, "Claude Sonnet 4.0"),
    
    # Google
    "gemini-pro": ModelPricing(0.00125, 0.005, 2000000, "Gemini Pro"),
    "gemini-flash": ModelPricing(0.000125, 0.0005, 1000000, "Gemini Flash"),
    "gemini-ultra": ModelPricing(0.0125, 0.05, 2000000, "Gemini Ultra"),
    
    # Mistral
    "mistral-small": ModelPricing(0.002, 0.006, 32000, "Mistral Small"),
    "mistral-medium": ModelPricing(0.0027, 0.0081, 32000, "Mistral Medium"),
    "mistral-large": ModelPricing(0.008, 0.024, 32000, "Mistral Large"),
    
    # DeepSeek
    "deepseek-chat": ModelPricing(0.00014, 0.00028, 64000, "DeepSeek Chat"),
    "deepseek-coder": ModelPricing(0.00014, 0.00028, 16000, "DeepSeek Coder"),
    
    # Groq
    "llama-3.3-70b": ModelPricing(0.00059, 0.00079, 131072, "Llama 3.3 70B on Groq"),
    "mixtral-8x7b": ModelPricing(0.00027, 0.00027, 32768, "Mixtral 8x7B on Groq"),
}


class AIUsageTracker:
    """AI Usage and Credit Management System."""
    
    def __init__(self, db_path: str = "ai_usage.db"):
        """Initialize the tracker with SQLite database."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                credits REAL NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                active BOOLEAN DEFAULT 1
            )
        """)
        
        # Credit purchases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credit_purchases (
                id TEXT PRIMARY KEY,
                amount REAL NOT NULL,
                purchased_at TEXT NOT NULL,
                notes TEXT DEFAULT ''
            )
        """)
        
        # Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                model TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                input_cost REAL NOT NULL,
                output_cost REAL NOT NULL,
                total_cost REAL NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # Usage summary table (for quick stats)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_summary (
                date TEXT PRIMARY KEY,
                total_jobs INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                total_cost REAL DEFAULT 0.0,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_subscription(self, name: str, credits: float, days: int = 30) -> str:
        """Add a new subscription."""
        sub_id = str(uuid.uuid4())
        expires_at = (datetime.now() + timedelta(days=days)).isoformat()
        created_at = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO subscriptions (id, name, credits, expires_at, created_at, active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (sub_id, name, credits, expires_at, created_at))
        
        conn.commit()
        conn.close()
        
        return sub_id
    
    def add_credit_purchase(self, amount: float, notes: str = "") -> str:
        """Add a one-time credit purchase."""
        purchase_id = str(uuid.uuid4())
        purchased_at = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO credit_purchases (id, amount, purchased_at, notes)
            VALUES (?, ?, ?, ?)
        """, (purchase_id, amount, purchased_at, notes))
        
        conn.commit()
        conn.close()
        
        return purchase_id
    
    def log_job(
        self, 
        name: str, 
        model: str, 
        input_text: str = "", 
        output_text: str = "",
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        description: str = "",
        metadata: Dict = None
    ) -> Tuple[str, Dict]:
        """Log an AI job and calculate costs."""
        
        # Get model pricing
        model_key = self._normalize_model_name(model)
        if model_key not in MODEL_PRICING:
            raise ValueError(f"Model '{model}' not supported")
        
        pricing = MODEL_PRICING[model_key]
        
        # Calculate tokens if not provided
        if input_tokens is None:
            input_tokens = count_tokens(input_text, model)
        if output_tokens is None:
            output_tokens = count_tokens(output_text, model)
        
        # Calculate costs
        input_cost = (input_tokens / 1000) * pricing.input_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_per_1k
        total_cost = input_cost + output_cost
        
        # Create job record
        job_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO jobs (id, name, description, model, input_tokens, output_tokens,
                            input_cost, output_cost, total_cost, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (job_id, name, description, model_key, input_tokens, output_tokens,
              input_cost, output_cost, total_cost, created_at, json.dumps(metadata or {})))
        
        conn.commit()
        conn.close()
        
        # Update daily summary
        self._update_daily_summary(total_cost, input_tokens + output_tokens)
        
        return job_id, {
            "job_id": job_id,
            "name": name,
            "model": model_key,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "created_at": created_at
        }
    
    def get_credit_balance(self) -> Dict:
        """Get current credit balance from subscriptions and purchases."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get active subscriptions
        cursor.execute("""
            SELECT name, credits, expires_at FROM subscriptions
            WHERE active = 1 AND expires_at > ?
        """, (datetime.now().isoformat(),))
        
        active_subs = cursor.fetchall()
        subscription_credits = sum(credits for _, credits, _ in active_subs)
        
        # Get unused credit purchases
        cursor.execute("SELECT SUM(amount) FROM credit_purchases")
        purchased_credits = cursor.fetchone()[0] or 0
        
        # Get total spent
        cursor.execute("SELECT SUM(total_cost) FROM jobs")
        total_spent = cursor.fetchone()[0] or 0
        
        conn.close()
        
        total_credits = subscription_credits + purchased_credits
        remaining_credits = total_credits - total_spent
        
        return {
            "subscription_credits": subscription_credits,
            "purchased_credits": purchased_credits,
            "total_credits": total_credits,
            "total_spent": round(total_spent, 6),
            "remaining_credits": round(remaining_credits, 6),
            "active_subscriptions": len(active_subs),
            "subscriptions": [
                {
                    "name": name,
                    "credits": credits,
                    "expires_at": expires_at
                } for name, credits, expires_at in active_subs
            ]
        }
    
    def get_usage_stats(self, days: int = 30) -> Dict:
        """Get usage statistics for the last N days."""
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute("""
            SELECT COUNT(*), SUM(input_tokens), SUM(output_tokens), SUM(total_cost)
            FROM jobs WHERE created_at > ?
        """, (start_date,))
        
        overall = cursor.fetchone()
        total_jobs = overall[0] or 0
        total_input_tokens = overall[1] or 0
        total_output_tokens = overall[2] or 0
        total_cost = overall[3] or 0
        
        # By model
        cursor.execute("""
            SELECT model, COUNT(*), SUM(total_cost), SUM(input_tokens + output_tokens)
            FROM jobs WHERE created_at > ?
            GROUP BY model ORDER BY SUM(total_cost) DESC
        """, (start_date,))
        
        by_model = [
            {
                "model": row[0],
                "jobs": row[1],
                "cost": round(row[2], 6),
                "tokens": row[3]
            } for row in cursor.fetchall()
        ]
        
        # Daily breakdown
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*), SUM(total_cost)
            FROM jobs WHERE created_at > ?
            GROUP BY DATE(created_at) ORDER BY date DESC
        """, (start_date,))
        
        daily = [
            {
                "date": row[0],
                "jobs": row[1],
                "cost": round(row[2], 6)
            } for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "period_days": days,
            "total_jobs": total_jobs,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "total_cost": round(total_cost, 6),
            "average_cost_per_job": round(total_cost / total_jobs, 6) if total_jobs > 0 else 0,
            "by_model": by_model,
            "daily_breakdown": daily
        }
    
    def get_job_details(self, job_id: str) -> Optional[Dict]:
        """Get details for a specific job."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM jobs WHERE id = ?
        """, (job_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "model": row[3],
            "input_tokens": row[4],
            "output_tokens": row[5],
            "total_tokens": row[4] + row[5],
            "input_cost": round(row[6], 6),
            "output_cost": round(row[7], 6),
            "total_cost": round(row[8], 6),
            "created_at": row[9],
            "metadata": json.loads(row[10])
        }
    
    def list_recent_jobs(self, limit: int = 10) -> List[Dict]:
        """List recent jobs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, model, total_cost, created_at
            FROM jobs ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        
        jobs = [
            {
                "id": row[0],
                "name": row[1],
                "model": row[2],
                "cost": round(row[3], 6),
                "created_at": row[4]
            } for row in cursor.fetchall()
        ]
        
        conn.close()
        return jobs
    
    def _normalize_model_name(self, model: str) -> str:
        """Normalize model name to match pricing keys."""
        model_lower = model.lower().replace("-", "-")
        
        if model_lower in MODEL_PRICING:
            return model_lower
        
        for key in MODEL_PRICING:
            if key.replace("-", "") in model_lower.replace("-", ""):
                return key
        
        return model_lower
    
    def _update_daily_summary(self, cost: float, tokens: int):
        """Update daily usage summary."""
        today = datetime.now().date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO usage_summary (date, total_jobs, total_tokens, total_cost, updated_at)
            VALUES (?, 1, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                total_jobs = total_jobs + 1,
                total_tokens = total_tokens + ?,
                total_cost = total_cost + ?,
                updated_at = ?
        """, (today, tokens, cost, datetime.now().isoformat(), tokens, cost, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()


def main():
    """Command-line interface for AI Usage Tracker."""
    parser = argparse.ArgumentParser(description="AI Usage Tracker with Credit Management")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add subscription
    sub_parser = subparsers.add_parser("add-subscription", help="Add a subscription")
    sub_parser.add_argument("name", help="Subscription name")
    sub_parser.add_argument("credits", type=float, help="Monthly credits in $")
    sub_parser.add_argument("--days", type=int, default=30, help="Subscription duration in days")
    
    # Add credits
    credits_parser = subparsers.add_parser("add-credits", help="Purchase credits")
    credits_parser.add_argument("amount", type=float, help="Credit amount in $")
    credits_parser.add_argument("--notes", default="", help="Purchase notes")
    
    # Log job
    job_parser = subparsers.add_parser("log-job", help="Log an AI job")
    job_parser.add_argument("name", help="Job name")
    job_parser.add_argument("model", help="AI model used")
    job_parser.add_argument("--input", help="Input text or file")
    job_parser.add_argument("--output", help="Output text or file")
    job_parser.add_argument("--input-tokens", type=int, help="Input token count")
    job_parser.add_argument("--output-tokens", type=int, help="Output token count")
    job_parser.add_argument("--description", default="", help="Job description")
    
    # Show balance
    subparsers.add_parser("balance", help="Show credit balance")
    
    # Show stats
    stats_parser = subparsers.add_parser("stats", help="Show usage statistics")
    stats_parser.add_argument("--days", type=int, default=30, help="Number of days")
    
    # List jobs
    jobs_parser = subparsers.add_parser("jobs", help="List recent jobs")
    jobs_parser.add_parser("list-jobs", help="List recent jobs")
    jobs_parser.add_argument("--limit", type=int, default=10, help="Number of jobs to show")
    
    # Job details
    detail_parser = subparsers.add_parser("job-details", help="Show job details")
    detail_parser.add_argument("job_id", help="Job ID")
    
    # JSON output
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--db", default="ai_usage.db", help="Database file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    tracker = AIUsageTracker(args.db)
    
    try:
        if args.command == "add-subscription":
            sub_id = tracker.add_subscription(args.name, args.credits, args.days)
            result = {"subscription_id": sub_id, "name": args.name, "credits": args.credits}
            
        elif args.command == "add-credits":
            purchase_id = tracker.add_credit_purchase(args.amount, args.notes)
            result = {"purchase_id": purchase_id, "amount": args.amount}
            
        elif args.command == "log-job":
            # Read input/output from files if provided
            input_text = ""
            output_text = ""
            
            if args.input:
                if Path(args.input).exists():
                    with open(args.input, 'r') as f:
                        input_text = f.read()
                else:
                    input_text = args.input
            
            if args.output:
                if Path(args.output).exists():
                    with open(args.output, 'r') as f:
                        output_text = f.read()
                else:
                    output_text = args.output
            
            job_id, result = tracker.log_job(
                args.name,
                args.model,
                input_text,
                output_text,
                args.input_tokens,
                args.output_tokens,
                args.description
            )
            
        elif args.command == "balance":
            result = tracker.get_credit_balance()
            
        elif args.command == "stats":
            result = tracker.get_usage_stats(args.days)
            
        elif args.command in ["jobs", "list-jobs"]:
            result = {"recent_jobs": tracker.list_recent_jobs(getattr(args, 'limit', 10))}
            
        elif args.command == "job-details":
            result = tracker.get_job_details(args.job_id)
            if not result:
                result = {"error": f"Job {args.job_id} not found"}
        
        # Output result
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_formatted_result(args.command, result)
            
    except Exception as e:
        error_result = {"error": str(e)}
        if args.json:
            print(json.dumps(error_result, indent=2))
        else:
            print(f"❌ Error: {e}")


def print_formatted_result(command: str, result: Dict):
    """Print formatted results based on command."""
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    if command == "add-subscription":
        print(f"✅ Subscription added: {result['name']} (${result['credits']}/month)")
        
    elif command == "add-credits":
        print(f"✅ Credits purchased: ${result['amount']}")
        
    elif command == "log-job":
        print(f"""✅ Job logged: {result['name']}
Model: {result['model']}
Tokens: {result['total_tokens']:,} ({result['input_tokens']:,} input + {result['output_tokens']:,} output)
Cost: ${result['total_cost']:.6f}
Job ID: {result['job_id']}""")
        
    elif command == "balance":
        print(f"""💰 Credit Balance
Total Credits: ${result['total_credits']:.2f}
  Subscription: ${result['subscription_credits']:.2f}
  Purchased: ${result['purchased_credits']:.2f}
Total Spent: ${result['total_spent']:.6f}
Remaining: ${result['remaining_credits']:.6f}
Active Subscriptions: {result['active_subscriptions']}""")
        
        if result['subscriptions']:
            print("\n📋 Active Subscriptions:")
            for sub in result['subscriptions']:
                print(f"  • {sub['name']}: ${sub['credits']}/month (expires {sub['expires_at'][:10]})")
    
    elif command == "stats":
        print(f"""📊 Usage Statistics (Last {result['period_days']} days)
Total Jobs: {result['total_jobs']}
Total Tokens: {result['total_tokens']:,}
Total Cost: ${result['total_cost']:.6f}
Average per Job: ${result['average_cost_per_job']:.6f}""")
        
        if result['by_model']:
            print(f"\n🤖 By Model:")
            for model in result['by_model']:
                print(f"  • {model['model']}: {model['jobs']} jobs, ${model['cost']:.6f}")
    
    elif command in ["jobs", "list-jobs"]:
        print("📋 Recent Jobs:")
        for job in result['recent_jobs']:
            print(f"  • {job['name']} ({job['model']}) - ${job['cost']:.6f} - {job['created_at'][:16]}")
    
    elif command == "job-details":
        print(f"""📄 Job Details
ID: {result['id']}
Name: {result['name']}
Description: {result['description']}
Model: {result['model']}
Tokens: {result['total_tokens']:,} ({result['input_tokens']:,} input + {result['output_tokens']:,} output)
Cost: ${result['total_cost']:.6f} (${result['input_cost']:.6f} input + ${result['output_cost']:.6f} output)
Created: {result['created_at']}""")


if __name__ == "__main__":
    main()