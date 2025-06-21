import google.generativeai as genai
import os
import json

# Gemini API 키 설정은 애플리케이션 시작점에서 한 번만 호출하는 것이 가장 좋습니다.
# (예: app/main.py). 여기서도 호출은 가능합니다.
if not os.getenv("GEMINI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def create_travel_plan(destination: str, schedule: str) -> dict:
    """
    여행지(destination)와 일정(schedule)을 받아 Gemini API를 통해 여행 계획을 생성합니다.

    Returns:
        dict: 생성된 여행 계획 JSON 데이터
    
    Raises:
        json.JSONDecodeError: API 응답이 유효한 JSON이 아닐 경우
        Exception: API 호출 또는 기타 과정에서 오류 발생 시
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
        여행지: {destination}
        일정: {schedule}

        위 정보를 바탕으로 여행 계획을 짜줘. 응답은 반드시 아래 형식의 JSON 객체로만 제공해줘.
        설명은 한국어로 작성하고, 마크다운(`json` 블록 포함)이나 다른 설명 없이 순수한 JSON 텍스트만 응답해야 해.

        {{
          "plan": [
            {{
              "day": 1,
              "description": "첫째 날",
              "places": [
                {{ "name": "장소 이름", "address": "주소", "activity": "할 것", "estimated_cost": "예상 비용" }}
              ]
            }}
          ]
        }}
        """

        response = model.generate_content(prompt)
        
        # 가끔 응답이 마크다운 코드 블록으로 감싸여 오는 경우가 있어 제거합니다.
        json_response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        plan_data = json.loads(json_response_text)
        return plan_data

    except (json.JSONDecodeError, Exception) as e:
        # 예외를 상위 호출자(API 엔드포인트)로 다시 던져서 처리하도록 합니다.
        print(f"Error in create_travel_plan: {e}")
        raise 