from langchain_core.messages import HumanMessage
from .orchestrator import get_llm
import json

def rerank_documents(state):
    """Rerank documents using relevance scoring"""
    
    if not state['retrieved_docs']:
        return {
            "reranked_docs": [],
            "trace": [{"agent": "reranker", "output": "No documents to rerank"}]
        }
    
    llm = get_llm(temperature=0)
    
    # Prepare documents for reranking
    docs_text = "\n\n---\n\n".join([
        f"Document {i+1}:\n{doc['text'][:500]}"
        for i, doc in enumerate(state['retrieved_docs'])
    ])
    
    prompt = f"""Rate the relevance of each document to this query from 1-10.
    
    Query: {state['query']}
    
    {docs_text}
    
    Return ONLY a JSON array of scores, one for each document.
    Example: [8, 3, 9, 2]
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content if hasattr(response, 'content') else str(response)
        scores = json.loads(content)
        
        # Add scores to docs
        docs_with_scores = []
        for i, doc in enumerate(state['retrieved_docs']):
            if i < len(scores):
                doc['relevance_score'] = scores[i]
                docs_with_scores.append(doc)
        
        # Sort by relevance
        docs_with_scores.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return {
            "reranked_docs": docs_with_scores[:5],
            "trace": [{"agent": "reranker", "output": f"Reranked {len(docs_with_scores)} documents using {config.LLM_PROVIDER}"}]
        }
    except Exception as e:
        print(f"Reranking error: {e}")
        # Fallback to original order
        return {
            "reranked_docs": state['retrieved_docs'][:5],
            "trace": [{"agent": "reranker", "output": f"Used original ordering (error with {config.LLM_PROVIDER})"}]
        }