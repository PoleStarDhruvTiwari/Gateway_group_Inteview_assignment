from sqlalchemy import create_engine, text
from ..config import config
from ..llm_factory import EmbeddingFactory
import json

# Cache embeddings instance
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = EmbeddingFactory.create_embeddings()
    return _embeddings

def retrieve_documents(state):
    """Hybrid search using vector similarity"""
    
    engine = create_engine(config.DATABASE_URL)
    all_docs = []
    
    # Get user's files
    with engine.connect() as conn:
        files = conn.execute(
            text("SELECT filename FROM files WHERE user_id = :user_id AND status = 'indexed'"),
            {"user_id": state.get("user_id", 1)}
        ).fetchall()
    
    file_names = [f[0] for f in files] if files else ["sample_policies"]
    
    embeddings = get_embeddings()
    
    for sub_query in state['sub_queries']:
        try:
            # Get embedding
            embedding = embeddings.embed_query(sub_query)
            
            # Vector search
            with engine.connect() as conn:
                results = conn.execute(
                    text("""
                        SELECT chunk_text, metadata, 
                               1 - (embedding <=> :embedding) as similarity
                        FROM document_chunks
                        WHERE source_file = ANY(:files)
                        ORDER BY embedding <=> :embedding
                        LIMIT 3
                    """),
                    {"embedding": embedding, "files": file_names}
                ).fetchall()
                
                for row in results:
                    all_docs.append({
                        "text": row[0],
                        "metadata": json.loads(row[1]) if row[1] else {},
                        "score": float(row[2]) if row[2] else 0
                    })
        except Exception as e:
            print(f"Error in retrieval: {e}")
            continue
    
    # Deduplicate
    seen = set()
    unique_docs = []
    for doc in all_docs[:10]:
        if doc["text"][:100] not in seen:
            seen.add(doc["text"][:100])
            unique_docs.append(doc)
    
    return {
        "retrieved_docs": unique_docs,
        "trace": [{"agent": "retriever", "output": f"Found {len(unique_docs)} relevant chunks"}]
    }