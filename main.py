from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
import uvicorn
import os

app = FastAPI()

@app.get("/transcript")
def get_transcript(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="Missing 'id' parameter in URL")
    
    try:
        # This calls the GitHub library to get the data
        srt = YouTubeTranscriptApi.get_transcript(id)
        
        # This formats the snippets exactly like your GitHub example
        return {
            "video_id": id,
            "snippets": srt
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)