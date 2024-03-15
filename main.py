from src.supabase_utils import supabase

response = supabase().table('it-category').select("*").execute()

print(response)