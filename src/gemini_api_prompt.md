from google import genai
from google.genai import types

with open('도시야경.jpg', 'rb') as f:
    image_bytes = f.read()

client = genai.Client(api_key="API_KEY_HERE")
response = client.models.generate_content(
    model='gemini-3-flash-preview',
    contents=[
        types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/jpeg',
        ),
        '그림을 설명해줘'
    ]
)

print(response.text)

이상의 예제를 기반으로 /camera/image_raw 토픽을 1회 구독하여 설명하는 python 예제를 만들어줘. 모델은 예제에 있는 모델을 사용해줘.
