#!/usr/bin/env python3
import os
import sys
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def wait_for_db():
    """Wait for database to be ready"""
    db_url = os.getenv('DATABASE_URL', 'postgresql://hr_user:hr_password@postgres/hr_assistant')
    
    # Parse connection string
    if db_url.startswith('postgresql://'):
        db_url = db_url.replace('postgresql://', '')
        user_pass, host_db = db_url.split('@')
        user, password = user_pass.split(':')
        host, database = host_db.split('/')
    else:
        user = 'hr_user'
        password = 'hr_password'
        host = 'postgres'
        database = 'hr_assistant'
    
    max_retries = 30
    retry_interval = 2
    
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                user=user,
                password=password,
                host=host,
                database=database
            )
            conn.close()
            print("✅ Database is ready!")
            return
        except psycopg2.OperationalError as e:
            print(f"⏳ Waiting for database ({i+1}/{max_retries})...")
            time.sleep(retry_interval)
    
    print("❌ Could not connect to database")
    sys.exit(1)

def init_vector_extension():
    """Ensure vector extension is created"""
    db_url = os.getenv('DATABASE_URL', 'postgresql://hr_user:hr_password@postgres/hr_assistant')
    
    conn = psycopg2.connect(db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.close()
    conn.close()
    print("✅ Vector extension ready")

def create_sample_user():
    """Create a sample user for testing"""
    from passlib.context import CryptContext
    import psycopg2.extras
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    db_url = os.getenv('DATABASE_URL', 'postgresql://hr_user:hr_password@postgres/hr_assistant')
    conn = psycopg2.connect(db_url)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Check if sample user exists
    cur.execute("SELECT id FROM users WHERE email = 'demo@example.com'")
    if not cur.fetchone():
        hashed = pwd_context.hash("demo123")
        cur.execute(
            "INSERT INTO users (email, hashed_password, full_name) VALUES (%s, %s, %s)",
            ('demo@example.com', hashed, 'Demo User')
        )
        conn.commit()
        print("✅ Sample user created (demo@example.com / demo123)")
    else:
        print("✅ Sample user already exists")
    
    cur.close()
    conn.close()

def create_sample_data():
    """Create sample HR documents if none exist"""
    db_url = os.getenv('DATABASE_URL', 'postgresql://hr_user:hr_password@postgres/hr_assistant')
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Check if we already have documents
    cur.execute("SELECT COUNT(*) FROM document_chunks")
    count = cur.fetchone()[0]
    
    if count == 0:
        print("📝 Creating sample HR documents...")
        
        # Sample remote work policy
        remote_work = """
        REMOTE WORK POLICY
        Effective Date: January 1, 2024
        
        1. ELIGIBILITY
        Employees may work remotely up to 3 days per week with manager approval. 
        Full-time remote work is available for roles that do not require physical presence.
        
        2. CALIFORNIA-SPECIFIC PROVISIONS
        California employees have additional rights under SB 1234:
        - Must provide written acknowledgment of remote work agreement
        - Reimbursement for necessary business expenses
        - Right to disconnect after work hours
        
        3. NEW YORK REQUIREMENTS
        New York employees must:
        - Complete remote work safety training
        - Maintain a dedicated workspace
        - Be available during core hours 10am-3pm ET
        """
        
        # Sample leave policy
        leave_policy = """
        PARENTAL LEAVE POLICY
        Last Updated: March 15, 2024
        
        MATERNITY LEAVE
        - Primary caregivers: 12 weeks paid leave
        - Additional 4 weeks unpaid
        - Must take within 3 months of birth/adoption
        
        PATERNITY LEAVE
        - 4 weeks paid leave
        - Must be taken within 6 months
        - Flexible scheduling available
        
        STATE-SPECIFIC BENEFITS
        California: Up to 8 weeks Paid Family Leave (supplemental)
        New York: 12 weeks paid at 67% salary (state program)
        """
        
        # Insert sample chunks
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY', ''))
        
        # Split into chunks (simplified)
        chunks = [
            (remote_work[:500], "remote_work_policy.txt"),
            (remote_work[500:1000], "remote_work_policy.txt"),
            (leave_policy[:500], "leave_policy.txt"),
            (leave_policy[500:1000], "leave_policy.txt"),
        ]
        
        for chunk_text, source in chunks:
            if chunk_text.strip():
                embedding = embeddings.embed_query(chunk_text)
                cur.execute(
                    "INSERT INTO document_chunks (source_file, chunk_text, embedding) VALUES (%s, %s, %s)",
                    (source, chunk_text, embedding)
                )
        
        conn.commit()
        print("✅ Sample documents created")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    print("🚀 Initializing database...")
    wait_for_db()
    init_vector_extension()
    create_sample_user()
    create_sample_data()
    print("✅ Database initialization complete!")