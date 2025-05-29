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
    speaker_to_voice = {
        options_dic['host1_name']: options_dic['host1_voice'],
        options_dic['host2_name']: options_dic['host2_voice']
    }
    speaker_to_mood = {
        options_dic['host1_name']: options_dic['host1_mood'],
        options_dic['host2_name']: options_dic['host2_mood']
    }
    audio_segments = []
    audio_segment = 0
    for dialogue_turn in dialogue.turns:
        audio_segment += 1
        filename = f"{audio_segment}.mp3"
        with client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice=speaker_to_voice[dialogue_turn.speaker],
                input=dialogue_turn.text,
                instructions=f"Speak in a {speaker_to_mood[dialogue_turn.speaker]} tone."
        ) as response:
            response.stream_to_file(filename)
            audio_segments.append(filename)

    print("Generated audio files:", audio_segments)

    combined = AudioSegment.from_mp3("static/audio/mind-intro.mp3")
    for filename in audio_segments:
        combined += AudioSegment.from_mp3(filename)
        os.remove(filename)
    combined += AudioSegment.from_mp3("static/audio/mind-intro.mp3")
    # Export the combined file
    podcast_path = os.path.join(os.getcwd(), "static/audio", f"{clean_path(topic)}.mp3")
    combined.export(podcast_path, format='mp3')

    print("Final podcast exported as podcast_final.mp3")
    return f"{clean_path(topic)}.mp3"