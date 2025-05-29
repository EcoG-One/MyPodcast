import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import wave
from open_ai import clean_path

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)


def gemini_create_podcast(topic, options_dic):
   host_sex = []
   for i in range(2):  # get sex from names
      if options_dic[f'host{i+1}_voice'] in ["Kore", "Leda", "Aoede", "Callirrhoe",
         "Autonoe", "Despina", "ErinomeErinome", "Laomedeia", "Achernar",
         "Gacrux", "Pulcherrima", "Vindemiatrix", "Sulafat"]:
         host_sex.append("female")
      else:
         host_sex.append("male")
   transcript = client.models.generate_content(
      model="gemini-2.0-flash",
      contents=""f"Generate a transcript around 300 words that reads like it was"
               f" a podcast about {topic} by two hosts. The hosts names are "
               f"{options_dic['host1_name']} and {options_dic['host2_name']}. "
               f"{options_dic['host1_name']} is {host_sex[0]}, {options_dic['host1_mood']}"
               f" and {options_dic['host2_name']} is {host_sex[0]}, {options_dic['host1_mood']}""").text
   print(transcript)

   response = client.models.generate_content(
      model="gemini-2.5-flash-preview-tts",
      contents=transcript,
      config=types.GenerateContentConfig(
         response_modalities=["AUDIO"],
         speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
               speaker_voice_configs=[
                  types.SpeakerVoiceConfig(
                     speaker=options_dic['host1_name'],
                     voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                           voice_name=options_dic['host1_voice'],
                        )
                     )
                  ),
                  types.SpeakerVoiceConfig(
                     speaker=options_dic['host2_name'],
                     voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                           voice_name=options_dic['host2_voice'],
                        )
                     )
                  ),
               ]
            )
         )
      )
   )

   data = response.candidates[0].content.parts[0].inline_data.data

   file_name = os.path.join(os.getcwd(), "static/audio",
                               f"{clean_path(topic)}.wav")
   wave_file(file_name, data) # Saves the file to current directory

   # Export the combined file

   return f"{clean_path(topic)}.wav"