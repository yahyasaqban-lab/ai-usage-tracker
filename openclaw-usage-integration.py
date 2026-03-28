#!/usr/bin/env python3
"""
OpenClaw AI Usage Integration
Integrate AI Usage Tracker with OpenClaw sessions.
"""

import json
import requests
import sqlite3
from datetime import datetime
from pathlib import Path
import re
import uuid
from typing import Dict, Optional

class OpenClawUsageIntegrator:
    """Integrate usage tracking with OpenClaw."""
    
    def __init__(
        self,
        tracker_api_url: str = "http://localhost:8001",
        openclaw_log_dir: str = "/home/y7/.openclaw/logs",
        session_log_path: str = "/home/y7/.openclaw/logs/sessions"
    ):
        self.api_url = tracker_api_url
        self.log_dir = Path(openclaw_log_dir)
        self.session_log_path = Path(session_log_path)
        self.tracked_sessions = set()
    
    def track_session_usage(self, session_key: str = "agent:main:main") -> Dict:
        """Track usage for an OpenClaw session."""
        try:
            # Get latest session log
            session_file = self.session_log_path / f"{session_key}.jsonl"
            
            if not session_file.exists():
                return {"error": f"Session log not found: {session_file}"}
            
            # Parse recent messages
            messages = self._parse_session_log(session_file)
            
            if not messages:
                return {"error": "No messages found in session log"}
            
            # Track each AI interaction
            tracked_jobs = []
            for msg in messages:
                if self._is_ai_interaction(msg):
                    job_result = self._track_message_as_job(msg, session_key)
                    if job_result and "job_id" in job_result:
                        tracked_jobs.append(job_result)
            
            return {
                "session_key": session_key,
                "tracked_jobs": len(tracked_jobs),
                "jobs": tracked_jobs
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_session_usage_summary(self, session_key: str = "agent:main:main") -> Dict:
        """Get usage summary for a session."""
        try:
            # Make API request to get stats
            response = requests.get(f"{self.api_url}/stats?days=30")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def auto_track_openclaw_usage(self, check_interval: int = 300) -> None:
        """Automatically track OpenClaw usage in the background."""
        import time
        import threading
        
        def track_loop():
            while True:
                try:
                    # Track main session usage
                    result = self.track_session_usage()
                    if "tracked_jobs" in result and result["tracked_jobs"] > 0:
                        print(f"[{datetime.now()}] Tracked {result['tracked_jobs']} new AI jobs")
                    
                    time.sleep(check_interval)
                except Exception as e:
                    print(f"[{datetime.now()}] Auto-track error: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        # Start background thread
        thread = threading.Thread(target=track_loop, daemon=True)
        thread.start()
        print(f"Started auto-tracking OpenClaw usage (interval: {check_interval}s)")
    
    def _parse_session_log(self, session_file: Path, limit: int = 50) -> list:
        """Parse recent messages from OpenClaw session log."""
        messages = []
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get last N lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
            for line in recent_lines:
                try:
                    msg = json.loads(line.strip())
                    messages.append(msg)
                except json.JSONDecodeError:
                    continue
            
            return messages
            
        except Exception as e:
            print(f"Error parsing session log: {e}")
            return []
    
    def _is_ai_interaction(self, message: Dict) -> bool:
        """Check if message represents an AI interaction."""
        # Look for tool calls and AI responses
        if message.get("role") == "assistant":
            return True
        
        # Check for tool usage
        if "tool_calls" in message or "tool_call_id" in message:
            return True
        
        # Check for model usage in metadata
        metadata = message.get("metadata", {})
        if "model" in metadata or "usage" in metadata:
            return True
        
        return False
    
    def _track_message_as_job(self, message: Dict, session_key: str) -> Optional[Dict]:
        """Convert OpenClaw message to tracked job."""
        try:
            # Extract job details
            job_name = self._generate_job_name(message, session_key)
            model = self._extract_model(message)
            input_text, output_text = self._extract_io_text(message)
            input_tokens, output_tokens = self._extract_token_counts(message)
            
            # Prepare job data
            job_data = {
                "name": job_name,
                "model": model,
                "input_text": input_text,
                "output_text": output_text,
                "description": f"OpenClaw session: {session_key}",
                "metadata": {
                    "session_key": session_key,
                    "timestamp": message.get("timestamp"),
                    "message_id": message.get("id"),
                    "role": message.get("role")
                }
            }
            
            # Add token counts if available
            if input_tokens is not None:
                job_data["input_tokens"] = input_tokens
            if output_tokens is not None:
                job_data["output_tokens"] = output_tokens
            
            # Make API request to log job
            response = requests.post(f"{self.api_url}/jobs", json=job_data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error logging job: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error tracking message as job: {e}")
            return None
    
    def _generate_job_name(self, message: Dict, session_key: str) -> str:
        """Generate a descriptive job name."""
        role = message.get("role", "unknown")
        timestamp = message.get("timestamp", datetime.now().isoformat())
        
        # Try to extract meaningful content
        content = message.get("content", "")
        if isinstance(content, str) and content:
            # Get first few words
            words = content.split()[:5]
            preview = " ".join(words)
            if len(preview) > 50:
                preview = preview[:50] + "..."
            return f"{role}: {preview}"
        
        # Check for tool calls
        if "tool_calls" in message:
            tool_names = [tool.get("function", {}).get("name", "unknown") 
                         for tool in message.get("tool_calls", [])]
            if tool_names:
                return f"{role}: {', '.join(tool_names[:3])}"
        
        # Default name
        return f"{role}: {timestamp[:16]}"
    
    def _extract_model(self, message: Dict) -> str:
        """Extract AI model from message metadata."""
        # Check metadata
        metadata = message.get("metadata", {})
        if "model" in metadata:
            return metadata["model"]
        
        # Check usage info
        usage = metadata.get("usage", {})
        if "model" in usage:
            return usage["model"]
        
        # Default fallback
        return "unknown"
    
    def _extract_io_text(self, message: Dict) -> tuple:
        """Extract input/output text from message."""
        content = message.get("content", "")
        
        if isinstance(content, str):
            # For assistant messages, content is output
            if message.get("role") == "assistant":
                return "", content
            else:
                return content, ""
        elif isinstance(content, list):
            # Handle complex content structures
            text_parts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
            
            combined_text = " ".join(text_parts)
            if message.get("role") == "assistant":
                return "", combined_text
            else:
                return combined_text, ""
        
        return "", ""
    
    def _extract_token_counts(self, message: Dict) -> tuple:
        """Extract token counts from message metadata."""
        metadata = message.get("metadata", {})
        usage = metadata.get("usage", {})
        
        input_tokens = usage.get("prompt_tokens") or usage.get("input_tokens")
        output_tokens = usage.get("completion_tokens") or usage.get("output_tokens")
        
        return input_tokens, output_tokens


def create_openclaw_skill():
    """Create an OpenClaw skill for usage tracking."""
    skill_dir = Path("/home/y7/.openclaw/workspace/skills/usage-tracker")
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    # Create skill metadata
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("""# Usage Tracker Skill

Track AI usage and costs in OpenClaw sessions.

## Commands

- `/track-usage` - Track current session usage
- `/usage-stats` - Show usage statistics
- `/usage-balance` - Show credit balance

## Setup

1. Start the usage tracker API:
   ```bash
   python ai-tracker-api.py
   ```

2. Enable auto-tracking:
   ```bash
   python openclaw-usage-integration.py --auto-track
   ```

## Usage

The skill automatically tracks AI interactions and costs.
View reports via commands or the web dashboard.
""")
    
    # Create skill implementation
    skill_py = skill_dir / "skill.py"
    skill_py.write_text('''#!/usr/bin/env python3
"""OpenClaw Usage Tracker Skill"""

import json
import requests
from datetime import datetime

def handle_command(command: str, args: list = None) -> str:
    """Handle usage tracking commands."""
    
    if command == "track-usage":
        return track_current_usage()
    elif command == "usage-stats":
        return show_usage_stats()
    elif command == "usage-balance":
        return show_credit_balance()
    else:
        return "Unknown command. Use: track-usage, usage-stats, or usage-balance"

def track_current_usage():
    """Track current session usage."""
    try:
        from openclaw_usage_integration import OpenClawUsageIntegrator
        
        integrator = OpenClawUsageIntegrator()
        result = integrator.track_session_usage()
        
        if "error" in result:
            return f"❌ Error: {result['error']}"
        
        return f"""✅ Usage Tracked
Session: {result['session_key']}
New Jobs: {result['tracked_jobs']}
"""
        
    except Exception as e:
        return f"❌ Error: {e}"

def show_usage_stats():
    """Show usage statistics."""
    try:
        response = requests.get("http://localhost:8001/stats?days=30")
        if response.status_code != 200:
            return f"❌ API Error: {response.status_code}"
        
        stats = response.json()
        
        return f"""📊 Usage Stats (30 days)
Jobs: {stats['total_jobs']}
Tokens: {stats['total_tokens']:,}
Cost: ${stats['total_cost']:.6f}
Avg/Job: ${stats['average_cost_per_job']:.6f}
"""
        
    except Exception as e:
        return f"❌ Error: {e}"

def show_credit_balance():
    """Show credit balance."""
    try:
        response = requests.get("http://localhost:8001/balance")
        if response.status_code != 200:
            return f"❌ API Error: {response.status_code}"
        
        balance = response.json()
        
        return f"""💰 Credit Balance
Total: ${balance['total_credits']:.2f}
Spent: ${balance['total_spent']:.6f}
Remaining: ${balance['remaining_credits']:.6f}
Subscriptions: {balance['active_subscriptions']}
"""
        
    except Exception as e:
        return f"❌ Error: {e}"
''')
    
    print(f"✅ Created OpenClaw usage tracking skill at: {skill_dir}")


def main():
    """CLI for OpenClaw usage integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Usage Integration")
    parser.add_argument("--track-session", help="Track specific session")
    parser.add_argument("--auto-track", action="store_true", help="Start auto-tracking")
    parser.add_argument("--create-skill", action="store_true", help="Create OpenClaw skill")
    parser.add_argument("--interval", type=int, default=300, help="Auto-track interval (seconds)")
    
    args = parser.parse_args()
    
    integrator = OpenClawUsageIntegrator()
    
    if args.create_skill:
        create_openclaw_skill()
        
    elif args.track_session:
        result = integrator.track_session_usage(args.track_session)
        print(json.dumps(result, indent=2))
        
    elif args.auto_track:
        print("Starting auto-tracking...")
        integrator.auto_track_openclaw_usage(args.interval)
        
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping auto-tracking...")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()