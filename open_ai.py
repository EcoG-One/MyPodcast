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

def generate_dialogue(topic, options_dic):
    host_sex = []
    for i in range(2):
        print(i) # get sex from names
        if options_dic[f'host{i+1}_voice'] in ["ash","echo","onyx","verse"]:
            host_sex.append("male")
        else:
            host_sex.append("female")
    prompt = (f"Generate a transcript around 300 words that reads like it was a "
              f"podcast about {topic} by two hosts. The hosts names are "
              f"{options_dic['host1_name']} and {options_dic['host2_name']}. "
              f"{options_dic['host1_name']} is {host_sex[0]}, {options_dic['host1_mood']} "
              f"and {options_dic['host2_name']} is {host_sex[0]}, {options_dic['host1_mood']}")
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "developer", "content": f"You are creating a podcast dialogue between two hosts. "
                   f"Host A is {host_sex[0]} {options_dic['host1_mood']}. Host B is {host_sex[1]}, {options_dic['host2_mood']}. "
                   f"Host A is named {options_dic['host1_name']}. Host B is named {options_dic['host2_name']}"},
                  {"role": "user", "content": prompt}],
        response_format=Dialogue,
    )
    return completion.choices[0].message.parsed


def text_to_audio(text, voice, mood, filename):
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
        instructions=f"Speak in a {mood} tone."
    )as response:
        response.stream_to_file(filename)


def clean_path(path):
    if os.name == 'nt':  # Windows
        return re.sub(r'[<>:"/\\|?*]', '', path)
    else:  # POSIX
        return re.sub(r'[\/\0]', '', path)


def ai_create_podcast(topic, options_dic):
    print(f"Generating podcast for the topic: {topic}")
    dialogue = generate_dialogue(topic, options_dic)
    print("Podcast Text:", dialogue.turns)
    print("Podcast generated. Converting to audio...")
    for i in range(len(dialogue.turns)):
        if dialogue.turns[i].speaker == options_dic['host1_name']:
            voice = options_dic['host1_voice']
            mood = options_dic['host1_mood']
        else:
            voice = options_dic['host2_voice']
            mood = options_dic['host2_mood']
        text_to_audio(dialogue.turns[i].text, voice, mood, f"podcast_line_{i}.mp3")
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