import openai
from pydub import AudioSegment
import os
from dotenv import load_dotenv

load_dotenv()

# Set up your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_dialogue(topic):
    prompt = f"Create an one minute podcast dialogue between you and Doris discussing about {topic}."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "developer", "content": "You are creating a podcast "
         "dialogue between two hosts. Host A is male cheerful and energetic. "
            "Host B is female, calm and analytical. Host A is named George. Host B is named Doris"},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def split_dialogue(dialogue):
    lines = dialogue.splitlines()
    host_a_lines = []
    for line in lines:
        if line.startswith("**George:** "):
            host_a_lines.append(line.split("**George:** ")[1])
    host_b_lines = []
    for line in lines:
        if line.startswith("**Doris:** "):
            host_b_lines.append(line.split("**Doris:** ")[1])
    return host_a_lines, host_b_lines


def text_to_audio(text, host, filename):
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=host,
        input=text,
        instructions="Speak in a cheerful and positive tone."
    )as response:
        response.stream_to_file(filename)



def create_podcast(topic):
    print(f"Generating podcast for the topic: {topic}")
    dialogue = generate_dialogue(topic)
    print("Podcast Text:", dialogue)
    print("Podcast generated. Converting to audio...")
    host_a_lines, host_b_lines = split_dialogue(dialogue)
    # Convert Host A's lines to audio
    for i, line in enumerate(host_a_lines): # voices: alloy, echo, fable, onyx, nova, shimmer
        text_to_audio(line, "ash", f"host_a_line_{i}.mp3")
        print(f"Audio saved to: host_a_line_{i}.mp3")
    # Convert Host B's lines to audio
    for i, line in enumerate(host_b_lines):
        text_to_audio(line, "shimmer", f"host_b_line_{i}.mp3")
        print(f"Audio saved to: host_b_line_{i}.mp3")

    # List mp3 files in the order we want to concatenate
    mp3_files = []
    for i in range(len(host_a_lines)):
        mp3_files.append(f"host_a_line_{i}.mp3")
        if i < len(host_b_lines):
            mp3_files.append(f"host_b_line_{i}.mp3")

    # Start with the first file
    combined = AudioSegment.from_mp3(mp3_files[0])

    # Loop through and add the rest
    for mp3_file in mp3_files[1:]:
        combined += AudioSegment.from_mp3(mp3_file)
        os.remove(mp3_file)

    # Export the combined file
    combined.export(f'{topic}.mp3', format='mp3')


if __name__ == "__main__":
    topic = input("Enter the podcast topic: ")
    create_podcast(topic)