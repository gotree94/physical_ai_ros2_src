import base64
from openai import OpenAI

client = OpenAI(api_key="API_KEY_HERE")

image_path = r"도시야경.jpg"
with open(image_path, "rb") as f:
    image_bytes = f.read()

image_base64 = base64.b64encode(image_bytes).decode("utf-8")

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

이상의 예제를 기반으로 /camera/image_raw 토픽을 1회 구독하여 설명하는 python 예제를 만들어줘. 모델은 예제에 있는 모델을 사용해줘.