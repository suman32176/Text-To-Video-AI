import edge_tts

async def generate_audio(text, output_filename, language):
    voice = "en-US-ChristopherNeural" if language == "english" else "hi-IN-MadhurNeural"
    communicate = edge_tts.Communicate(text, voice)
    
    total_length = len(text)
    current_length = 0

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            with open(output_filename, "ab") as f:
                f.write(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            current_length = chunk["text_position"] + chunk["word_length"]
            progress = (current_length / total_length) * 100
            print(f"Audio generation progress: {progress:.2f}%")

    print("Audio generation complete.")
