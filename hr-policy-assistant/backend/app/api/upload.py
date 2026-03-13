from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy import text
from sqlalchemy.orm import Session
import json
from pathlib import Path
import pandas as pd
import PyPDF2
from docx import Document
import chardet
import asyncio
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from .. import auth
from ..agents.retriever import get_embeddings

router = APIRouter()
UPLOAD_DIR = Path("/app/data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class UploadResponse(BaseModel):
    status: str
    filename: str
    message: str
    file_id: Optional[int] = None

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    file_type: str = Form(...),
    document_name: str = Form(None),
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and index a file"""
    
    # Validate file type
    allowed_types = ['pdf', 'docx', 'txt', 'csv', 'json']
    if file_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type must be one of: {allowed_types}")
    
    # Validate file size (max 10MB)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File too large. Max size 10MB")
    
    # Save file
    timestamp = datetime.now().timestamp()
    safe_filename = file.filename.replace(" ", "_")
    file_path = UPLOAD_DIR / f"{current_user.id}_{timestamp}_{safe_filename}"
    
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create file record
    doc_name = document_name or file.filename
    try:
        result = db.execute(
            text("""
                INSERT INTO files (filename, file_type, user_id, status, metadata)
                VALUES (:filename, :type, :user_id, 'processing', :metadata)
                RETURNING id
            """),
            {
                "filename": doc_name,
                "type": file_type,
                "user_id": current_user.id,
                "metadata": json.dumps({
                    "original_name": file.filename, 
                    "size": file_size,
                    "upload_time": datetime.now().isoformat()
                })
            }
        )
        file_id = result.fetchone()[0]
        db.commit()
    except Exception as e:
        # Clean up file if DB insert fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to create file record: {str(e)}")
    
    # Start background processing
    background_tasks.add_task(
        process_file,
        file_path=file_path,
        file_type=file_type,
        doc_name=doc_name,
        file_id=file_id,
        user_id=current_user.id
    )
    
    return {
        "status": "processing",
        "filename": doc_name,
        "message": "File uploaded successfully. Processing started.",
        "file_id": file_id
    }

async def process_file(file_path: Path, file_type: str, doc_name: str, file_id: int, user_id: int):
    """Process and index file in background"""
    from sqlalchemy import create_engine
    from ..config import config
    
    engine = create_engine(config.DATABASE_URL)
    
    try:
        # Extract text chunks
        chunks = extract_text(file_path, file_type)
        
        if not chunks:
            raise Exception("No text could be extracted from file")
        
        # Get embeddings
        embeddings = get_embeddings()
        
        # Insert chunks
        with engine.connect() as conn:
            chunk_count = 0
            for i, chunk in enumerate(chunks[:50]):  # Limit to 50 chunks per file
                if not chunk.strip():
                    continue
                
                try:
                    embedding = embeddings.embed_query(chunk[:2000])  # Limit chunk size for embedding
                    
                    conn.execute(
                        text("""
                            INSERT INTO document_chunks (source_file, chunk_text, metadata, embedding)
                            VALUES (:source, :text, :metadata, :embedding)
                        """),
                        {
                            "source": doc_name,
                            "text": chunk[:2000],  # Limit stored text
                            "metadata": json.dumps({"file_id": file_id, "chunk_index": i}),
                            "embedding": embedding
                        }
                    )
                    chunk_count += 1
                except Exception as e:
                    print(f"Error embedding chunk {i}: {e}")
                    continue
            
            # Update file status
            conn.execute(
                text("""
                    UPDATE files 
                    SET status = 'indexed', total_chunks = :chunks
                    WHERE id = :id
                """),
                {"chunks": chunk_count, "id": file_id}
            )
            conn.commit()
            print(f"✅ Indexed {chunk_count} chunks for file {file_id}")
            
    except Exception as e:
        print(f"❌ Error processing file {file_id}: {e}")
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE files SET status = 'failed' WHERE id = :id"),
                {"id": file_id}
            )
            conn.commit()
    finally:
        # Clean up temp file
        if file_path.exists():
            file_path.unlink()

def extract_text(file_path: Path, file_type: str):
    """Extract text chunks from file"""
    chunks = []
    
    try:
        if file_type == "txt":
            with open(file_path, 'rb') as f:
                raw = f.read()
                encoding = chardet.detect(raw)['encoding'] or 'utf-8'
                text = raw.decode(encoding, errors='ignore')
                # Simple chunking
                chunk_size = 500
                overlap = 50
                for i in range(0, len(text), chunk_size - overlap):
                    chunks.append(text[i:i+chunk_size])
        
        elif file_type == "pdf":
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                # Simple chunking
                chunk_size = 500
                for i in range(0, len(text), chunk_size):
                    chunks.append(text[i:i+chunk_size])
        
        elif file_type == "docx":
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            chunk_size = 500
            for i in range(0, len(text), chunk_size):
                chunks.append(text[i:i+chunk_size])
        
        elif file_type == "csv":
            df = pd.read_csv(file_path)
            # Convert each row to text
            for _, row in df.iterrows():
                row_text = " ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                if row_text:
                    chunks.append(row_text[:500])  # Limit row length
        
        elif file_type == "json":
            with open(file_path) as f:
                data = json.load(f)
                # Flatten JSON to text
                text = json.dumps(data, indent=2)
                chunk_size = 500
                for i in range(0, len(text), chunk_size):
                    chunks.append(text[i:i+chunk_size])
    
    except Exception as e:
        print(f"Error extracting text from {file_type}: {e}")
        return []
    
    return chunks