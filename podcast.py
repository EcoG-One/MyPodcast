import openai
from pydub import AudioSegment
import os
import re
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

load_dotenv()
# Set up your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

class DialogueTurn(BaseModel):
    speaker: str  # "HostA" or "HostB"
    text: str     # The spoken content

class Dialogue(BaseModel):
    turns: List[DialogueTurn]

def generate_dialogue(topic):
    prompt = f"Create an one minute podcast dialogue between you and Doris discussing about {topic}."
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "developer", "content": "You are creating a podcast "
         "dialogue between two hosts. Host A is male cheerful and energetic. "
            "Host B is female, calm and analytical. Host A is named George. Host B is named Doris"},
                  {"role": "user", "content": prompt}],
        response_format=Dialogue,
    )
    return completion.choices[0].message.parsed


def text_to_audio(text, host, filename):
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=host,
        input=text,
        instructions="Speak in a cheerful and positive tone."
    )as response:
        response.stream_to_file(filename)


def clean_path(path):
    if os.name == 'nt':  # Windows
        return re.sub(r'[<>:"/\\|?*]', '', path)
    else:  # POSIX
        return re.sub(r'[\/\0]', '', path)


def create_podcast(topic):
    print(f"Generating podcast for the topic: {topic}")
    dialogue = generate_dialogue(topic)
    print("Podcast Text:", dialogue.turns)
    print("Podcast generated. Converting to audio...")
    for i in range(len(dialogue.turns)):
        if dialogue.turns[i].speaker == "George":
            host = "ash"
        else:
            host = "shimmer"
        text_to_audio(dialogue.turns[i].text, host, f"podcast_line_{i}.mp3")
        print(f"Audio saved to: podcast_line_{i}.mp3")

    # List mp3 files in the order we want to concatenate
    mp3_files = []
    for i in range(len(dialogue.turns)):
        mp3_files.append(f"podcast_line_{i}.mp3")
    # Start with the first file
    # combined = AudioSegment.from_mp3(mp3_files[0])
    combined = AudioSegment.from_mp3("static/audio/mind-intro.mp3")
    # os.remove(mp3_files[0])
    # Loop through and add the rest
    for mp3_file in mp3_files:
        combined += AudioSegment.from_mp3(mp3_file)
        os.remove(mp3_file)
    combined += AudioSegment.from_mp3("static/audio/mind-intro.mp3")
    # Export the combined file
    podcast_path = os.path.join(os.getcwd(), "static/audio", f"{clean_path(topic)}.mp3")
    combined.export(podcast_path, format='mp3')
    return f"{clean_path(topic)}.mp3"