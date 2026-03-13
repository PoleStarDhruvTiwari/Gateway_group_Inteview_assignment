from fastapi import APIRouter, Depends, Form, HTTPException, BackgroundTasks
from sqlalchemy import text
from sqlalchemy.orm import Session
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Optional, Any

from ..database import get_db
from .. import auth
from ..agents.orchestrator import create_hr_agent_workflow

router = APIRouter()

# Pydantic models for response
class TraceStep(BaseModel):
    agent: str
    output: str

class QueryResponse(BaseModel):
    cached: bool
    answer: str
    agent_trace: List[TraceStep]
    query_id: Optional[str] = None
    hit_count: Optional[int] = None

@router.post("/query", response_model=QueryResponse)
async def submit_query(
    query: str = Form(...),
    use_cache: bool = Form(True),
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a query and get answer as JSON"""
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Generate cache key
    query_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    # Check cache if enabled
    if use_cache:
        try:
            cached = db.execute(
                text("""
                    SELECT answer, agent_trace, hit_count 
                    FROM query_cache 
                    WHERE query_hash = :hash 
                      AND expires_at > NOW()
                """),
                {"hash": query_hash}
            ).fetchone()
            
            if cached:
                # Update hit count
                db.execute(
                    text("UPDATE query_cache SET hit_count = hit_count + 1 WHERE query_hash = :hash"),
                    {"hash": query_hash}
                )
                db.commit()
                
                return {
                    "cached": True,
                    "answer": cached[0],
                    "agent_trace": json.loads(cached[1]) if cached[1] else [],
                    "hit_count": cached[2] + 1
                }
        except Exception as e:
            print(f"Cache check error: {e}")
            # Continue without cache if there's an error
    
    # No cache - run agent workflow
    workflow = create_hr_agent_workflow()
    
    try:
        result = workflow.invoke({
            "query": query,
            "user_id": current_user.id
        })
        
        # Store in cache
        try:
            db.execute(
                text("""
                    INSERT INTO query_cache (query_hash, query_text, answer, agent_trace, expires_at)
                    VALUES (:hash, :query, :answer, :trace, NOW() + INTERVAL '7 days')
                    ON CONFLICT (query_hash) 
                    DO UPDATE SET answer = :answer, agent_trace = :trace, 
                                  expires_at = NOW() + INTERVAL '7 days',
                                  hit_count = query_cache.hit_count + 1
                """),
                {
                    "hash": query_hash,
                    "query": query,
                    "answer": result["final_answer"],
                    "trace": json.dumps(result.get("trace", []))
                }
            )
            
            # Save to history
            db.execute(
                text("""
                    INSERT INTO queries (user_id, query_text, final_answer, agent_trace)
                    VALUES (:user, :query, :answer, :trace)
                """),
                {
                    "user": current_user.id,
                    "query": query,
                    "answer": result["final_answer"],
                    "trace": json.dumps(result.get("trace", []))
                }
            )
            
            db.commit()
        except Exception as e:
            print(f"Error saving to cache/history: {e}")
            db.rollback()
            # Continue even if cache save fails
        
        return {
            "cached": False,
            "answer": result["final_answer"],
            "agent_trace": result.get("trace", []),
            "query_id": str(uuid.uuid4())
        }
        
    except Exception as e:
        print(f"Error in agent workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")