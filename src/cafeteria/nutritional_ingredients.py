import google.generativeai as genai
import os
from dotenv import load_dotenv

from utils.supabase import get_supabase_client
load_dotenv(verbose=True)

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

prompt = """
당신은 경상국립대학교 각 카테고리 별 학식 메뉴의 영양 성분을 분석하는 프로그램입니다.
다음 지침을 따르세요.

1. 각 카테고리 별 메뉴들을 분석하여 최대한 비슷한 일반적인 음식들의 영양 정보를 바탕으로 대략적인 추정치를 계산한다.
2-1. 메뉴들의 총 영양 성분을 합산하여 계산해서 출력한다.
2-2. 만약 카테고리가 여러 개 존재한다면 총 영양 성분은 따로 계산하세요.

출력 포맷은 별도의 부가 설명과 마크다운을 사용하지 않고, 다음 형식을 따르세요:
"""

class NutritionalIngredients:
  def __init__(self, cafeteria_id, day, time, dishes):
    self.cafeteria_id = cafeteria_id
    self.day = day
    self.time = time
    self.dishes = ""
  
  def get_nutritional_ingredients(self):
    content = model.generate_content(prompt + self.dishes)
    self.update_nutritional_ingredients(content)
  
  def update_nutritional_ingredients(self, content: str):
    get_supabase_client().table('nutritional_ingredients').insert(content).execute()