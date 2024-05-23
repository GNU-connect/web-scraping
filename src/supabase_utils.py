import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(verbose=True)
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase_client: Client = create_client(url, key)

def get_supabase_client():
    return supabase_client