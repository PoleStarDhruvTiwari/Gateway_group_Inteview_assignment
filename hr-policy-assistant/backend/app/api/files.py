from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from .. import auth

router = APIRouter()

# Pydantic model for file response
class FileResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    status: str
    total_chunks: int
    upload_date: str
    
    class Config:
        from_attributes = True

@router.get("/files", response_model=List[FileResponse])
async def list_files(
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Return list of user's files as JSON"""
    
    try:
        files = db.execute(
            text("""
                SELECT id, filename, file_type, status, total_chunks, 
                       to_char(upload_date, 'YYYY-MM-DD HH24:MI:SS') as upload_date
                FROM files 
                WHERE user_id = :user_id
                ORDER BY upload_date DESC
                LIMIT 20
            """),
            {"user_id": current_user.id}
        ).fetchall()
        
        return [
            {
                "id": f.id,
                "filename": f.filename,
                "file_type": f.file_type,
                "status": f.status,
                "total_chunks": f.total_chunks or 0,
                "upload_date": f.upload_date
            }
            for f in files
        ]
    except Exception as e:
        print(f"Error fetching files: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch files")