import os
import pickle
from googleapiclient.http import MediaFileUpload
import google_auth_oauthlib.flow
import googleapiclient.discovery

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"

class YouTubeClient(object):
    def __init__(self, credentials_location):
        
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            credentials_location, scopes)
        #credentials = flow.run_console()
        #youtube_client = googleapiclient.discovery.build(
         #   api_service_name, api_version, credentials=credentials)
        youtube_client = get_authenticated_service(credentials_location)
        self.youtube_client = youtube_client

    def set_thumbnail(self, video_id, thumbnail):
        request = self.youtube_client.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail)
        )
        response = request.execute()

        return response
    
def get_authenticated_service(client_secrets_file):
    if os.path.exists("tokens_pickle"):
        with open("tokens_pickle", 'rb') as f:
            credentials = pickle.load(f)
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        credentials = flow.run_console()
        with open("tokens_pickle", 'wb') as f:
            pickle.dump(credentials, f)
    return googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)