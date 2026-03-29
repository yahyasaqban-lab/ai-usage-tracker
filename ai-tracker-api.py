#!/usr/bin/env python3
"""
AI Usage Tracker REST API
FastAPI server for AI usage tracking and credit management.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import json
from datetime import datetime

# Import our tracker
# Import the tracker module from the same directory
import importlib.util
import os

spec = importlib.util.spec_from_file_location("ai_usage_tracker", 
                                              os.path.join(os.path.dirname(__file__), "ai-usage-tracker.py"))
ai_usage_tracker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_usage_tracker)

AIUsageTracker = ai_usage_tracker.AIUsageTracker

# API Models
class SubscriptionCreate(BaseModel):
    name: str
    credits: float
    days: int = 30


class CreditPurchase(BaseModel):
    amount: float
    notes: str = ""


class JobLog(BaseModel):
    name: str
    model: str
    input_text: str = ""
    output_text: str = ""
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    description: str = ""
    metadata: Optional[Dict] = None


class JobResponse(BaseModel):
    job_id: str
    name: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    created_at: str


class CreditBalance(BaseModel):
    subscription_credits: float
    purchased_credits: float
    total_credits: float
    total_spent: float
    remaining_credits: float
    active_subscriptions: int
    subscriptions: List[Dict]


class UsageStats(BaseModel):
    period_days: int
    total_jobs: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost: float
    average_cost_per_job: float
    by_model: List[Dict]
    daily_breakdown: List[Dict]


# Initialize FastAPI app
app = FastAPI(
    title="AI Usage Tracker API",
    description="Track AI usage, manage credits, and monitor costs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tracker
tracker = AIUsageTracker()


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "AI Usage Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "subscriptions": "/subscriptions",
            "credits": "/credits",
            "jobs": "/jobs",
            "balance": "/balance",
            "stats": "/stats"
        }
    }


@app.post("/subscriptions", response_model=Dict)
async def create_subscription(subscription: SubscriptionCreate):
    """Create a new subscription."""
    try:
        sub_id = tracker.add_subscription(
            subscription.name,
            subscription.credits,
            subscription.days
        )
        return {
            "subscription_id": sub_id,
            "name": subscription.name,
            "credits": subscription.credits,
            "days": subscription.days
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/credits", response_model=Dict)
async def purchase_credits(purchase: CreditPurchase):
    """Purchase additional credits."""
    try:
        purchase_id = tracker.add_credit_purchase(
            purchase.amount,
            purchase.notes
        )
        return {
            "purchase_id": purchase_id,
            "amount": purchase.amount,
            "notes": purchase.notes
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/jobs", response_model=JobResponse)
async def log_job(job: JobLog):
    """Log a new AI job."""
    try:
        job_id, result = tracker.log_job(
            job.name,
            job.model,
            job.input_text,
            job.output_text,
            job.input_tokens,
            job.output_tokens,
            job.description,
            job.metadata
        )
        return JobResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/jobs", response_model=List[Dict])
async def list_jobs(limit: int = Query(10, ge=1, le=100)):
    """List recent jobs."""
    try:
        jobs = tracker.list_recent_jobs(limit)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/jobs/{job_id}", response_model=Dict)
async def get_job(job_id: str):
    """Get job details by ID."""
    try:
        job = tracker.get_job_details(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/balance", response_model=CreditBalance)
async def get_balance():
    """Get current credit balance."""
    try:
        balance = tracker.get_credit_balance()
        return CreditBalance(**balance)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/stats", response_model=UsageStats)
async def get_stats(days: int = Query(30, ge=1, le=365)):
    """Get usage statistics."""
    try:
        stats = tracker.get_usage_stats(days)
        return UsageStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/models", response_model=List[Dict])
async def list_models():
    """List available AI models with pricing."""
    MODEL_PRICING = ai_usage_tracker.MODEL_PRICING
    
    models = []
    for key, pricing in MODEL_PRICING.items():
        models.append({
            "model": key,
            "input_per_1k": pricing.input_per_1k,
            "output_per_1k": pricing.output_per_1k,
            "context_window": pricing.context_window,
            "notes": pricing.notes
        })
    
    models.sort(key=lambda x: x["input_per_1k"] + x["output_per_1k"])
    return models


@app.post("/estimate", response_model=Dict)
async def estimate_cost(
    model: str,
    input_text: str = "",
    output_text: str = "",
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None
):
    """Estimate cost for a job without logging it."""
    try:
        MODEL_PRICING = ai_usage_tracker.MODEL_PRICING
        count_tokens = ai_usage_tracker.count_tokens
        
        # Normalize model name
        model_key = model.lower().replace("-", "-")
        if model_key not in MODEL_PRICING:
            # Try fuzzy matching
            for key in MODEL_PRICING:
                if key.replace("-", "") in model_key.replace("-", ""):
                    model_key = key
                    break
            else:
                raise HTTPException(status_code=400, detail=f"Model '{model}' not supported")
        
        pricing = MODEL_PRICING[model_key]
        
        # Calculate tokens
        if input_tokens is None:
            input_tokens = count_tokens(input_text, model_key)
        if output_tokens is None:
            output_tokens = count_tokens(output_text, model_key)
        
        # Calculate costs
        input_cost = (input_tokens / 1000) * pricing.input_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_per_1k
        total_cost = input_cost + output_cost
        
        return {
            "model": model_key,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "pricing": {
                "input_per_1k": pricing.input_per_1k,
                "output_per_1k": pricing.output_per_1k,
                "context_window": pricing.context_window,
                "notes": pricing.notes
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }


if __name__ == "__main__":
    uvicorn.run(
        "ai-tracker-api:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )