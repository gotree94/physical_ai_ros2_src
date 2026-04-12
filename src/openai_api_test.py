# pip install openai
import base64
from openai import OpenAI

# OpenAI 클라이언트 생성
client = OpenAI(api_key="API_KEY_HERE")

# 이미지 파일 읽기
image_path = r"도시야경.jpg"
with open(image_path, "rb") as f:
    image_bytes = f.read()

# base64 인코딩
image_base64 = base64.b64encode(image_bytes).decode("utf-8")

# Data URL 생성 (⭐ 핵심)
image_data_url = f"data:image/jpeg;base64,{image_base64}"

response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "그림을 설명해줘"},
                {
                    "type": "input_image",
                    "image_url": image_data_url
                }
            ]
        }
    ]
)

print(response.output_text)
