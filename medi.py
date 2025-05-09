from google.genai import types
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs

client = genai.Client(api_key="")

def extract_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    if parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
    raise ValueError("Invalid YouTube URL")

def fetch_transcript(video_url):
    video_id = extract_video_id(video_url)

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            transcript = transcript_list.find_transcript(['en'])
            print("Found English transcript.")
        except NoTranscriptFound:
            transcript = transcript_list.find_transcript(['hi'])
            print("English not available. Found Hindi transcript.")

        fetched_transcript = transcript.fetch()
        full_text = " ".join([entry.text for entry in fetched_transcript])
        return full_text

    except TranscriptsDisabled:
        print("Subtitles are disabled for this video.")
    except NoTranscriptFound:
        print("No transcripts found in English or Hindi.")
    except Exception as e:
        print(f"Error fetching transcript: {e}")
    
    return ""


def generate_mcqs(transcript_text, num_questions=10):
    prompt = f"""
You are an AI assistant that generates multiple-choice questions (MCQs) based on educational content.
Your task is to create questions that test the understanding of the content provided in the transcript.
Generate {num_questions} medium level multiple-choice questions based on the educational content below. 
Each question should have 1 correct answer and 3 plausible distractors.

Transcript:
\"\"\"
{transcript_text}
\"\"\"

Output format:
1. Question?
    A. Option1
    B. Option2
    C. Option3
    D. Option4
Answer: A
"""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating MCQs: {e}")
        return ""

if __name__ == "__main__":
    video_url = input("Enter YouTube video URL: ")
    transcript = fetch_transcript(video_url)
    #print(transcript)

    if transcript:
        print("\nGenerating MCQs from video transcript...\n")
        mcqs = generate_mcqs(transcript)
        print(mcqs)
    else:
        print("Failed to fetch transcript.")
