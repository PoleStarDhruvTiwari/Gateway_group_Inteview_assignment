from langchain_core.messages import HumanMessage
from .orchestrator import get_llm
from ..config import config

def generate_answer(state):
    """Generate final answer from reranked documents"""
    
    if not state['reranked_docs']:
        return {
            "final_answer": "I couldn't find any relevant information to answer your question.",
            "trace": [{"agent": "summarizer", "output": "No relevant documents found"}]
        }
    
    llm = get_llm(temperature=0.3)  # Slightly more creative for answers
    
    # Prepare context
    context = "\n\n".join([
        f"[From {doc.get('metadata', {}).get('file_id', 'HR Policy')}]:\n{doc['text']}"
        for doc in state['reranked_docs']
    ])
    
    prompt = f"""You are an HR policy expert. Answer the question based ONLY on the provided context.
    
    Question: {state['query']}
    
    Context from HR documents:
    {context}
    
    Provide a clear, concise answer. If the context doesn't contain enough information, say so.
    Include specific policy details when available.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        answer = f"Error generating answer with {config.LLM_PROVIDER}: {str(e)}"
    
    return {
        "final_answer": answer,
        "trace": [{"agent": "summarizer", "output": f"Generated answer using {config.LLM_PROVIDER} with {len(state['reranked_docs'])} sources"}]
    }