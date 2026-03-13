from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from langchain_core.messages import HumanMessage
import json

from .retriever import retrieve_documents
from .reranker import rerank_documents
from .summarizer import generate_answer
from ..llm_factory import LLMFactory

class AgentState(TypedDict):
    query: str
    sub_queries: List[str]
    retrieved_docs: List[Dict[str, Any]]
    reranked_docs: List[Dict[str, Any]]
    final_answer: str
    trace: List[Dict[str, Any]]
    user_id: int

def create_hr_agent_workflow():
    """Create the multi-agent workflow using LangGraph"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", plan_sub_queries)
    workflow.add_node("retriever", retrieve_documents)
    workflow.add_node("reranker", rerank_documents)
    workflow.add_node("summarizer", generate_answer)
    
    # Add edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "retriever")
    workflow.add_edge("retriever", "reranker")
    workflow.add_edge("reranker", "summarizer")
    workflow.add_edge("summarizer", END)
    
    return workflow.compile()

def get_llm(temperature=0):
    """Get LLM instance from factory based on .env setting"""
    return LLMFactory.create_llm(temperature=temperature)

def plan_sub_queries(state: AgentState):
    """Decompose complex HR query into simpler sub-queries"""
    llm = get_llm(temperature=0)
    
    prompt = f"""You are an HR policy expert. Break this HR question into 2-3 simpler search queries.
    
    Question: {state['query']}
    
    Return ONLY the queries as a JSON array of strings, nothing else.
    Example: ["remote work policy California", "parental leave duration", "overtime approval process"]
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        # Try to parse JSON
        content = response.content if hasattr(response, 'content') else str(response)
        sub_queries = json.loads(content)
        if not isinstance(sub_queries, list):
            sub_queries = [state['query']]
    except Exception as e:
        print(f"Planning error: {e}")
        # Fallback: use original query
        sub_queries = [state['query']]
    
    # Limit to 3 sub-queries
    sub_queries = sub_queries[:3]
    
    return {
        "sub_queries": sub_queries,
        "trace": [{"agent": "planner", "output": f"Split into: {', '.join(sub_queries)}"}]
    }