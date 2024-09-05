import time
from nutritional_ingredients import *
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from google.api_core.exceptions import ResourceExhausted
from src.utils.supabase import get_supabase_client
import traceback
import sys
from dotenv import load_dotenv
from src.utils.slack import Slack_Notifier

load_dotenv(verbose=True)

class CafeteriaDietAnalyzer:
    def __init__(self):
        self.prompt_template = """
        당신은 경상국립대학교 각 카테고리 별 학식 메뉴의 영양 성분을 분석하는 프로그램입니다.
        다음 지침을 따르세요.

        1. 각 카테고리 별 메뉴들을 분석하여 최대한 비슷한 일반적인 음식들의 영양 정보를 바탕으로 대략적인 추정치를 계산한다.
        2-1. 메뉴들의 총 영양 성분을 합산하여 계산해서 출력한다.
        2-2. 만약 카테고리가 여러 개 존재한다면 총 영양 성분은 따로 계산하세요.

        출력 포맷은 별도의 부가 설명과 마크다운을 사용하지 않고, 다음 형식을 따르세요:

        [카테고리1]

        1. 쌀밥 (1인분, 약 200g)
        칼로리: 300 kcal
        탄: 65 g
        단: 5 g
        지: 0.5 g

        [카테고리1 총 영양 성분]

        총 칼로리: 1580 kcal
        총 탄수화물: 225 g
        총 단백질: 53.5 g
        총 지방: 45.5 g

        다음은 메뉴입니다:
        {input}
        """

        # Initialize LLM and other components
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
        self.prompt = ChatPromptTemplate.from_template(self.prompt_template)
        self.chain = self.prompt | self.llm | StrOutputParser()
        self.supabase_client = get_supabase_client()

    def get_nutritional_ingredients(self, cafeteria_id, date, time, dishes):
        """Fetch nutritional information for the provided dishes using AI model."""
        try:
            content = self.chain.invoke({"input": dishes})
            self.insert_nutritional_ingredients(cafeteria_id, date, time, content)
        except ResourceExhausted as e:
            print("Resource exhausted. Please try again later.")
            sys.exit(0)
        except Exception as e:
            error_message = f'영양 성분을 가져오는데 실패했습니다: {e}'
            print(error_message)
            Slack_Notifier().fail(error_message)
            traceback.print_exc()
            

    def insert_nutritional_ingredients(self, cafeteria_id, date, time, content):
        """Insert the calculated nutritional information into the Supabase table."""
        self.supabase_client.table('cafeteria_nutritional_ingredients').upsert({
            'cafeteria_id': int(cafeteria_id),
            'date': date,
            'time': time,
            'content': content
        }).execute()

    def is_exist_cafeteria_nutritional_ingredients(self, cafeteria_id, date, time):
        """Check if nutritional information already exists for the given cafeteria, date, and time."""
        data = self.supabase_client.table('cafeteria_nutritional_ingredients').select('*') \
            .eq('cafeteria_id', cafeteria_id) \
            .eq('date', date) \
            .eq('time', time) \
            .execute().data
        return len(data) > 0

    def process_diet(self, cafeteria_diet):
        """Process a single cafeteria diet entry."""
        cafeteria_id = cafeteria_diet['cafeteria_id']
        date = cafeteria_diet['date']
        time = cafeteria_diet['time']
        formatted_output = cafeteria_diet['formatted_output']

        if not self.is_exist_cafeteria_nutritional_ingredients(cafeteria_id, date, time):
            self.get_nutritional_ingredients(cafeteria_id, date, time, formatted_output)

    def find_all_cafeteria_diet(self):
        """Find and process all cafeteria diets."""
        all_cafeteria_diet = self.supabase_client.table('cafeteria_diet_view').select('*').execute().data

        for cafeteria_diet in all_cafeteria_diet:
            self.process_diet(cafeteria_diet)
            # You can add a delay here if needed
            time.sleep(1)  # Optional: delay between processing each entry


def main():
    analyzer = CafeteriaDietAnalyzer()
    analyzer.find_all_cafeteria_diet()

if __name__ == '__main__':
    main()
