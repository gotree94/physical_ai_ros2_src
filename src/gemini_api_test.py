from google import genai
from google.genai import types

with open('도시야경.jpg', 'rb') as f:
  image_bytes = f.read()

client = genai.Client(api_key="API_KEY_HERA")
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
