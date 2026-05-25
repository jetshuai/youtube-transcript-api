from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import uvicorn
import os

app = FastAPI()

# Locate the cookies file in your project
COOKIES_FILE = os.path.join(os.path.dirname(__file__), 'cookies.txt')

@app.get("/transcript")
def get_transcript(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="Missing 'id' parameter in URL")
    
    # Check if user uploaded cookies
    cookies_param = COOKIES_FILE if os.path.exists(COOKIES_FILE) else None
    
    try:
        # Pass the cookies file into the API request to bypass bot blocks
        transcript_list = YouTubeTranscriptApi.list_transcripts(id, cookies=cookies_param)
        
        try:
            srt = transcript_list.find_manually_created_transcript(['en']).fetch()
        except NoTranscriptFound:
            srt = transcript_list.find_generated_transcript(['en']).fetch()
            
        return {
            "video_id": id,
            "snippets": srt
        }
        
    except (TranscriptsDisabled, NoTranscriptFound):
        raise HTTPException(status_code=404, detail="No English captions found or captions disabled on YouTube.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
