from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import uvicorn
import os

app = FastAPI()

# EDIT THESE VALUES WITH REAL CREDENTIALS IF YOU USE A PROXY
PROXY_USER = "your_proxy_username"
PROXY_PASS = "your_proxy_password"
PROXY_HOST = "your_proxy_address_or_ip"
PROXY_PORT = "your_proxy_port"

@app.get("/transcript")
def get_transcript(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="Missing 'id' parameter in URL")
    
    # Check if user actually replaced the placeholder text
    use_proxy = all([
        PROXY_USER and PROXY_USER != "your_proxy_username",
        PROXY_PASS and PROXY_PASS != "your_proxy_password",
        PROXY_HOST and PROXY_HOST != "your_proxy_address_or_ip",
        PROXY_PORT and PROXY_PORT != "your_proxy_port"
    ])
    
    proxy_dict = None
    if use_proxy:
        proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        proxy_dict = {
            "http": proxy_url,
            "https": proxy_url
        }

    try:
        # Pass proxy dict conditionally (Will be None if placeholders are left unchanged)
        transcript_list = YouTubeTranscriptApi.list_transcripts(id, proxies=proxy_dict)
        
        try:
            srt = transcript_list.find_manually_created_transcript(['en']).fetch()
        except NoTranscriptFound:
            srt = transcript_list.find_generated_transcript(['en']).fetch()
            
        return {
            "status": "success",
            "proxy_active": use_proxy,
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
