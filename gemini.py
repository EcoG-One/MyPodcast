import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import wave

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


def gemini_create_podcast():
   transcript = client.models.generate_content(
      model="gemini-2.0-flash",
      contents="""Generate a transcript around 500 words that reads
               like it was a podcast about insomnia by two excited hosts.
               The hosts names are George and Doris.""").text
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
                     speaker='George',
                     voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                           voice_name='Puck',
                        )
                     )
                  ),
                  types.SpeakerVoiceConfig(
                     speaker='Doris',
                     voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                           voice_name='Despina',
                        )
                     )
                  ),
               ]
            )
         )
      )
   )

   data = response.candidates[0].content.parts[0].inline_data.data

   file_name='out.wav'
   wave_file(file_name, data) # Saves the file to current directory