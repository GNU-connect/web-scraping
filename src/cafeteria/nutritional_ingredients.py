from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from datetime import datetime
from src.utils.supabase import get_supabase_client
from dotenv import load_dotenv

load_dotenv(verbose=True)

prompt = """
당신은 경상국립대학교 각 카테고리 별 학식 메뉴의 영양 성분을 분석하는 프로그램입니다.
다음 지침을 따르세요.

1. 각 카테고리 별 메뉴들을 분석하여 최대한 비슷한 일반적인 음식들의 영양 정보를 바탕으로 대략적인 추정치를 계산한다.
2-1. 메뉴들의 총 영양 성분을 합산하여 계산해서 출력한다.
2-2. 만약 카테고리가 여러 개 존재한다면 총 영양 성분은 따로 계산하세요.

출력 포맷은 별도의 부가 설명과 마크다운을 사용하지 않고, 다음 형식을 따르세요:

[카테고리1]

1. 쌀밥
칼로리: 300 kcal
탄: 65 g
단: 5 g
지: 0.5 g

[카테고리1 총 영양 성분]

총 칼로리: 1580 kcal
총 탄수화물: 225 g
총 지방: 45.5 g
총 단백질: 53.5 g

⚠️ 주의: 이 정보는 AI 모델에 의해 생성된 결과값으로, 실제 학식 메뉴의 영양 성분과 다를 수 있어! ⚠️


다음은 메뉴입니다:
{input}
"""

def get_nutritional_ingredients(cafeteria_id, date, time, dishes):
  global prompt

  llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
  prompt = ChatPromptTemplate.from_template(prompt)
  chain = prompt | llm | StrOutputParser()
  content = chain.invoke({"input": dishes})
  print(content)
  insert_nutritional_ingredients(cafeteria_id, date, time, content)


def insert_nutritional_ingredients(cafeteria_id, date, time, content: str):
  get_supabase_client().table('cafeteria_nutritional_ingredients').upsert({
    'cafeteria_id': int(cafeteria_id),
    'date': date,
    'time': time,
    'content': content
  }).execute()

def isExistNutritionalIngredients(cafeteria_id, date, time):
    # date가 문자열인 경우 datetime 객체로 변환
    if isinstance(date, str):
        date = datetime.fromisoformat(date)
    
    # date를 문자열 형식으로 변환 (예: '2024-09-02')
    date_str = date.strftime('%Y-%m-%d')
    
    # Supabase 클라이언트 호출
    response = get_supabase_client().table('cafeteria_nutritional_ingredients') \
        .select('*') \
        .eq('cafeteria_id', cafeteria_id) \
        .eq('date', date_str) \
        .eq('time', time) \
        .execute()

    # 데이터를 찾았는지 여부 반환
    return len(response.data) > 0
    