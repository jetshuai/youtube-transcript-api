from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import uvicorn
import os

app = FastAPI()

# Input your proxy credentials here (Free residential proxies can be found on WebShare.io)
PROXY_USER = "your_proxy_username"
PROXY_PASS = "your_proxy_password"
PROXY_HOST = "your_proxy_address_or_ip"
PROXY_PORT = "your_proxy_port"

PROXIES = {
    "http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}",
    "https": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
}

@app.get("/transcript")
def get_transcript(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="Missing 'id' parameter in URL")
        
    try:
        # Pass the proxy directly into the backend configuration parameter
        transcript_list = YouTubeTranscriptApi.list_transcripts(id, proxies=PROXIES)
        
        try:
            srt = transcript_list.find_manually_created_transcript(['en']).fetch()
        except NoTranscriptFound:
            srt = transcript_list.find_generated_transcript(['en']).fetch()
            
        return {
            "status": "success",
            "video_id": id,
            "snippets": srt
        }
        
    except (TranscriptsDisabled, NoTranscriptFound):
        raise HTTPException(status_code=404, detail="YouTube reported no English captions available for this video ID.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API Engine Error: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
