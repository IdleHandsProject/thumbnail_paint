from collections import defaultdict
import json
import random
import pandas as pd
from utils.helper import openURL
from config import YOUTUBE_COMMENT_URL, SAVE_PATH
import re
from datetime import datetime, timedelta
import numpy as np


numComments = 100
commentMaxPages = 1
commentsPerPage = 100
totalPixels = 64
pixel_list = np.zeros((totalPixels * numComments), dtype=int)


class VideoComment:
    pixel_num=0
    
    def __init__(self, maxResults, videoId, key ):
        self.comments = defaultdict(list)
        self.replies = defaultdict(list)
        self.params = {
                    'part': 'snippet',
                    'maxResults': maxResults,
                    'videoId': videoId,
                    'order': 'time',
                    'textFormat': 'plainText',
                    'key': key
                }

    def load_comments(self, mat, pageNum):
        random.seed(datetime.utcnow())
        comment_num = 0
        pixel_num = 0
        if (pageNum>0):
            pixel_num = pageNum * numComments * totalPixels
        any_pixels = 0
        for item in mat["items"]:
            comment = item["snippet"]["topLevelComment"]
            self.comments["comment"].append(comment["snippet"]["textDisplay"])
            user_comment = comment["snippet"]["textDisplay"]   
            #if (user_comment[0] == '$'):
            #    if (user_comment[1] == '$'):
            comment_time = comment["snippet"]["publishedAt"]
            comment_datetime = datetime.strptime(comment_time, '%Y-%m-%dT%H:%M:%SZ')
            current_time = datetime.utcnow()
            since_time = current_time - timedelta(seconds = 80)
            
            #print(comment_datetime, " - ", (comment_datetime>since_time))
            user_pixel_num = 0
            
            if (comment_datetime>since_time):
                isolated_pixels = isolate_pixel(user_comment)
                num_isolated_pixels = len(isolated_pixels)
                if (num_isolated_pixels>4):
                    remainder = num_isolated_pixels % 5
                    if (remainder>0):
                        num_isolated_pixels -= remainder
                    if(num_isolated_pixels>(5*totalPixels)-1):
                        num_isolated_pixels = 5*totalPixels
                    for x in range(num_isolated_pixels):
                        pixel_list[pixel_num] = isolated_pixels[x]
                        pixel_num+=1
                        any_pixels = 1
                if(any_pixels == 0):
                    startx = random.randint(0, 830)
                    starty = random.randint(0, 555)
                    r = random.randint(0, 255)
                    g = random.randint(0, 255)
                    b = random.randint(0, 255)
                    for x in range(4):
                        for y in range(4):
                            pixel_list[pixel_num] = (startx + x)
                            pixel_num+=1
                            pixel_list[pixel_num] = (starty + y)
                            pixel_num+=1
                            pixel_list[pixel_num] = r
                            pixel_num+=1
                            pixel_list[pixel_num] = g
                            pixel_num+=1
                            pixel_list[pixel_num] = b
                            pixel_num+=1
                        
        print (pixel_list)
        return (pixel_list)

    def get_video_comments(self):
        commentPage = 0 
        url_response = json.loads(openURL(YOUTUBE_COMMENT_URL, self.params))
        nextPageToken = url_response.get("nextPageToken")
        next_move = self.load_comments(url_response,commentPage)
        commentPage += 1
        if (commentPage > (commentMaxPages - 1)):
            while nextPageToken:
                self.params.update({'pageToken': nextPageToken})
                url_response = json.loads(openURL(YOUTUBE_COMMENT_URL, self.params))
                nextPageToken = url_response.get("nextPageToken")
                next_move = self.load_comments(url_response, commentPage)
                commentPage += 1
                if (commentPage > (commentMaxPages - 1)):
                    break
        return (next_move)
        

def isolate_pixel(comment):
    #pixel = str(re.findall('\{.*?\}',comment))
    pixel = [int(comment) for comment in re.findall(r'\d+', comment)]
    #print(pixel)
    return pixel