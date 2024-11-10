import os
import asyncio
import argparse
from openai import OpenAI
from groq import Groq
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
from utility.translation.translator import translate_script

# Set up API clients
OPENAI_API_KEY = os.getenv('OPENAI_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if len(GROQ_API_KEY) > 30:
    model = "mixtral-8x7b-32768"
    client = Groq(api_key=GROQ_API_KEY)
else:
    model = "gpt-4"
    client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_video(topic, duration, language):
    # Generate script
    script = generate_script(topic, duration)
    print(f"Generated script: {script}")

    # Translate script if language is Hindi
    if language == "hindi":
        script = translate_script(script, "en", "hi")
        print(f"Translated script: {script}")

    # Generate audio
    audio_file = f"audio_{language}.wav"
    await generate_audio(script, audio_file, language)

    # Generate timed captions
    timed_captions = generate_timed_captions(audio_file, language)
    print(f"Generated timed captions: {timed_captions}")

    # Generate video search queries
    search_terms = getVideoSearchQueriesTimed(script, timed_captions)
    print(f"Generated search terms: {search_terms}")

    # Generate background video URLs
    background_video_urls = generate_video_url(search_terms, "pexel", duration * 60)
    background_video_urls = merge_empty_intervals(background_video_urls)
    print(f"Generated background video URLs: {background_video_urls}")

    # Render final video
    if background_video_urls:
        output_file = get_output_media(audio_file, timed_captions, background_video_urls, "pexel", language)
        print(f"Generated video: {output_file}")
    else:
        print("No background video available")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a long fact video in English or Hindi.")
    parser.add_argument("topic", type=str, help="The topic for the video")
    parser.add_argument("--duration", type=int, default=10, help="Duration of the video in minutes (max 10)")
    parser.add_argument("--language", type=str, choices=["english", "hindi"], default="english", help="Language of the video")

    args = parser.parse_args()
    
    if args.duration > 10:
        print("Maximum duration is 10 minutes. Setting duration to 10 minutes.")
        args.duration = 10

    asyncio.run(generate_video(args.topic, args.duration, args.language))
