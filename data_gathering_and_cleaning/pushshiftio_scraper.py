import requests
from datetime import datetime
import traceback
import time
import json


url = "https://api.pushshift.io/reddit/{}/search?subreddit={}&limit=500&fields={}&sort=desc&before="


start_time = datetime.utcnow()


def downloadFromUrl(filename, subreddit):
    object_type = "submission"
    print(f"Saving {object_type}s to {filename}")

    count = 0
    handle = open(filename, 'a')
    previous_epoch = int(start_time.timestamp())

    while True:
        # new_url = url.format(object_type, username)+str(previous_epoch)
        fields = "title,selftext,created_utc,score,id,author,subreddit"
        new_url = url.format(object_type, subreddit, fields)+str(previous_epoch)
        json_response = requests.get(new_url)
        time.sleep(1) # pushshift has a rate limit, if we send requests too fast it will start returning error messages
        try:
            json_data = json_response.json()
        except json.decoder.JSONDecodeError as err:
            print(f'Got corrupt json at epoch {previous_epoch}. Trying again.')
            continue
        if 'data' not in json_data:
            print('No data on json response.')
            break

        objects = json_data['data']
        if len(objects) == 0:
            break

        for object in objects:
            previous_epoch = object['created_utc'] - 1
            count += 1
            
            if 'selftext' not in object:
                continue
            try:
                importantFields = ["title", "selftext", "created_utc", "score", "id", "author", "subreddit"]
                smallJSON = {key:object[key] for key in importantFields}
                smallJSON["body"] = smallJSON.pop("selftext")
                
                json.dump(smallJSON,handle, indent=4)
            
            except Exception as err:
                print(f"Couldn't print post: {object['url']}")
                print(traceback.format_exc())

        print("Saved {} {}s through {}".format(count, object_type, datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d")))
        
    print(f"Saved {count} {object_type}s")
    handle.close()


downloadFromUrl(filename="r_jokes_2021_uncleaned.json", subreddit="jokes")