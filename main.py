from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.proxies import GenericProxyConfig
import uvicorn
import os

app = FastAPI()

# 1. CONFIGURE YOUR PROXY HERE
# Replace these placeholders with your actual proxy provider details
PROXY_USER = "your_proxy_username"
PROXY_PASS = "your_proxy_password"
PROXY_HOST = "my-custom-proxy.org"
PROXY_PORT = "port"

@app.get("/transcript")
def get_transcript(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="Missing 'id' parameter in URL")
    
    # 2. CHECK IF PROXY IS CONFIGURED
    use_proxy = all([
        PROXY_USER and PROXY_USER != "your_proxy_username",
        PROXY_PASS and PROXY_PASS != "your_proxy_password",
        PROXY_HOST and PROXY_HOST != "my-custom-proxy.org",
        PROXY_PORT and PROXY_PORT != "port"
    ])
    
    try:
        # 3. INITIALIZE THE API CLIENT
        if use_proxy:
            # Build the authenticated URLs exactly like your snippet
            http_string = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
            https_string = f"https://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
            
            proxy_config = GenericProxyConfig(
                http_url=http_string,
                https_url=https_string
            )
            # Create the proxied API instance
            api_instance = YouTubeTranscriptApi(proxy_config=proxy_config)
        else:
            # Fallback to standard client if no proxy is configured yet
            api_instance = YouTubeTranscriptApi

        # 4. FETCH THE TRANSCRIPT LIST VIA THE INSTANCE
        transcript_list = api_instance.list_transcripts(id)
        
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
