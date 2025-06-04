import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import wave
from open_ai import clean_path
from tavili import tavili_answer

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
   host_gender = []
   for i in range(2):  # get gender from names
      if options_dic[f'host{i+1}_voice'] in ["Kore", "Leda", "Aoede", "Callirrhoe",
         "Autonoe", "Despina", "ErinomeErinome", "Laomedeia", "Achernar",
         "Gacrux", "Pulcherrima", "Vindemiatrix", "Sulafat"]:
         host_gender.append("female")
      else:
         host_gender.append("male")
   response_client = (client.models.generate_content(
      model="gemini-2.0-flash",
      contents=f"""
                You are a creative and professional podcast scriptwriter.
                
                Task: Write a ~320-word podcast script for two hosts on the topic: "{topic}" based on the latest news below for the given topic. 
                The script should be engaging, conversational, and informative. 
                Hosts should alternate turns, speak naturally, and respond to each other. 
                Start with a hook or question, explore the topic briefly, and end with a surprising or motivational takeaway. 
                Avoid heavy jargon. Add personality and occasional humor.
                
                Example:
                Topic: {topic}
                Latest news: {tavili_answer(topic)}
                
                Podcast Script:
                Host A ({host_gender[0]}, {options_dic['host1_mood']}, named {options_dic['host1_name']}): [Example line based on Tavili answer]
                Host B ({host_gender[1]}, {options_dic['host2_mood']}, named {options_dic['host2_name']}): [Response line]
                ... [Continue alternating for ~320 words]
                
                ---
                
                Now write a new podcast script on the same topic based on the same latest news using a similar structure and tone.
                Host A is {host_gender[0]}, {options_dic['host1_mood']}, and named {options_dic['host1_name']}.
                Host B is {host_gender[1]}, {options_dic['host2_mood']}, and named {options_dic['host2_name']}.
                """
))
   transcript = response_client.text
   # Access and print the usage_metadata
   if response_client.usage_metadata:
      print(f"\nClient Prompt tokens: {response_client.usage_metadata.prompt_token_count}")
      print(f"Client Candidate tokens: {response_client.usage_metadata.candidates_token_count}")
      print(f"Client Total tokens: {response_client.usage_metadata.total_token_count}")
      print(transcript)
   else:
      print("\nUsage metadata not available in the client response.")

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