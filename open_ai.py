import openai
from pydub import AudioSegment
import os
import re
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from tavili import tavili_answer

load_dotenv()
# Set up your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Define OpenAI structured output classes:
class DialogueTurn(BaseModel):
    speaker: str  # "HostA" or "HostB"
    text: str     # The spoken content

class Dialogue(BaseModel):
    turns: List[DialogueTurn]


def generate_dialogue(topic, options_dic):
    """
    Generate the Podcast text, using OpenAI
    :param topic: Podcast topic
    :param options_dic: Dictionary with the Podcast settings
    :return: the Podcast text parsed
    """
    host_gender = []
    for i in range(2): # get gender from names
        if options_dic[f'host{i+1}_voice'] in ["ash","echo","onyx","verse"]:
            host_gender.append("male")
        else:
            host_gender.append("female")
    hosts_check = ''
    if options_dic['host1_name'] in topic:
        hosts_check = (f"- {options_dic['host1_name']} in {topic} and "
                       f"Host A are not the same person.")
    if options_dic['host2_name'] in topic:
        hosts_check = (f"- {options_dic['host2_name']} in {topic} and "
                       f"Host B are not the same person.")
    prompt = f"""
    You are an expert podcast scriptwriter.

    Write a conversational, engaging, and easy-to-follow podcast script 
    (~320 words, ~2 minutes) for two hosts based on the latest news below 
    and the given topic.

    Hosts:
    - Host A: {host_gender[0]}, mood: {options_dic['host1_mood']}, 
    name: {options_dic['host1_name']}
    - Host B: {host_gender[1]}, mood: {options_dic['host2_mood']}, 
    name: {options_dic['host2_name']}

    Script Format Example:
    Host A: [Engaging hook, starts topic]
    Host B: [Replies naturally, adds a twist]
    Host A: [Continues with info or humor]
    Host B: [Builds on the point]
    ... (alternate for ~320 words)
    End with a motivational or surprising takeaway.

    Latest news: {tavili_answer(topic)}
    Topic: "{topic}"

    Instructions:
    - Alternate naturally between hosts.
    - Make the tone conversational, lively, and clear.
    - Avoid jargon; keep it relatable.
    - Show personality, add humor, and ensure a natural flow.
    - Output only the script, with no extra text.
    {hosts_check}
    """

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "developer",
                "content": "You are an expert podcast scriptwriter."
            },
            {
                "role": "user",
                "content": prompt}],
        response_format=Dialogue,
    )
    dialogue = completion.choices[0].message
    # Token usage breakdown
    print("\n--- Token Usage ---")
    print(f"Prompt tokens: {completion.usage.prompt_tokens}")
    print(f"Completion tokens: {completion.usage.completion_tokens}")
    print(f"Total tokens: {completion.usage.total_tokens}")
    # If the model refuses to respond
    if (dialogue.refusal):
        raise Exception(dialogue.refusal)
    else:
        return dialogue.parsed


def text_to_audio(text, voice, mood, filename):
    """
    Converts given text to audio
    :param text: text to convert
    :param voice: voice chosen by user
    :param mood: mood chosen by user
    :param filename: the name of the audio file to be created
    :return: an audio file with the given text converted to audio
    """
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
        instructions=f"Speak in a {mood} tone."
    )as response:
        response.stream_to_file(filename)


def clean_path(path):
    """
    Gets rid of illegal path characters
    :param path: the string to clean
    :return: the path with no illegal characters
    """
    if os.name == 'nt':  # Windows
        return re.sub(r'[<>:"/\\|?*]', '', path)
    else:  # POSIX
        return re.sub(r'[\/\0]', '', path)


def ai_create_podcast(topic, options_dic):
    """
    Creates the Podcast: Text is generated via the generate_dialogue
    function, and then it is converted to audio via the text_to_audio
    function. Finally, all audio segments of the podcast dialogue are
    concatenated in one final audio file, with music intro and outro
    :param topic: Podcast topic
   :param options_dic: Dictionary with the Podcast settings
   :return: the Podcast audio file
    """
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
    for turn in dialogue.turns:
        audio_segment += 1
        text = turn.text
        voice=speaker_to_voice[turn.speaker]
        mood = speaker_to_mood[turn.speaker]
        filename = f"{audio_segment}.mp3"
        text_to_audio(text, voice, mood, filename)
        audio_segments.append(filename)

    print("Generated audio files:", audio_segments)

    combined = AudioSegment.from_mp3("static/audio/mind-intro.mp3")
    for filename in audio_segments:
        combined += AudioSegment.from_mp3(filename)
        os.remove(filename)
    combined += AudioSegment.from_mp3("static/audio/mind-intro.mp3")
    # Export the combined file
    podcast_path = os.path.join(os.getcwd(), "static/audio",
                                f"{clean_path(topic)}.mp3")
    combined.export(podcast_path, format='mp3')

    print("Final podcast exported as podcast_final.mp3")
    return f"{clean_path(topic)}.mp3"