import os
from openai import OpenAI
from groq import Groq
import json

OPENAI_API_KEY = os.getenv('OPENAI_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if len(GROQ_API_KEY) > 30:
    model = "mixtral-8x7b-32768"
    client = Groq(api_key=GROQ_API_KEY)
else:
    model = "gpt-4"
    client = OpenAI(api_key=OPENAI_API_KEY)

def generate_script(topic, duration_minutes):
    prompt = f"""You are a seasoned content writer for an educational YouTube channel, specializing in fact-based videos. 
    Create an engaging and informative script for a {duration_minutes}-minute video about {topic}.
    The script should be structured with an introduction, several fact segments, and a conclusion.
    Each fact should be concise and interesting. Aim for approximately 150 words per minute.

    Strictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'script'.

    # Output
    {{"script": "Here is the script ..."}}
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": topic}
        ]
    )
    content = response.choices[0].message.content
    try:
        script = json.loads(content)["script"]
    except Exception as e:
        json_start_index = content.find('{')
        json_end_index = content.rfind('}')
        print(content)
        content = content[json_start_index:json_end_index+1]
        script = json.loads(content)["script"]
    return script
