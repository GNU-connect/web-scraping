import os
from supabase import create_client

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

def get_supabase_client():
    return create_client(url, key)