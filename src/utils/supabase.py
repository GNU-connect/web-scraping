import os
from supabase import create_client, Client

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

def get_supabase_client():
    supabase_client: Client = create_client(url, key)
    return supabase_client