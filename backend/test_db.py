from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the directory where this file lives
current_dir = Path(__file__).parent
env_path = current_dir / '.env'

print(f'Looking for .env at: {env_path}')
print(f'File exists: {env_path.exists()}')

load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL')
print(f'DATABASE_URL loaded: {DATABASE_URL}')

if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text('SELECT version();'))
            version = result.fetchone()
            print(f'✅ Connected! PostgreSQL version: {version[0][:50]}...')
    except Exception as e:
        print(f'❌ Connection failed: {e}')
else:
    print('❌ DATABASE_URL is still None!')
