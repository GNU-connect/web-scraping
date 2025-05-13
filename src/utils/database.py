import os
from supabase import create_client

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

_supabase = None


def get_supabase_client():
    global _supabase
    if _supabase is None:
        _supabase = create_client(url, key)
    return _supabase
