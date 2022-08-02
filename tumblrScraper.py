#Using the tumblr API to get post information
import os
import time
import pytumblr
import numpy as np

#Collect posts under a given tag and print their urls
def get_all_notes_and_tags(client, tag:str, all_unique_tags):
    
    #make a loop to be able toget more posts
    for i in range(4):

        min_timestamp=0

        #Get 20 posts with the given tag before the given timestamp

        #Initialize the list of posts using the dedault (current) timestamp
        if(min_timestamp==0):
            response = client.tagged(tag, limit=20)
        #Otherwise, use the min timestamp
        else:
            response = client.tagged(tag, before=min_timestamp, limit=20)

        #Catches status 429 error
        if response['meta']['status'] == 429:
            yield 'too many requests'

        #Track the timestamps to find the oldest one and then search for more posts before that
        min_timestamp=response[0]['timestamp']
        
        #time.sleep(60)
        #For every post, get the tags and notes
        for post in response:
            timestamp = post['timestamp']
            
            #Update the earliest time
            if(timestamp<min_timestamp):
                min_timestamp=timestamp
            
            if('id' in post):
                #Also get the post's tags
                tags = post['tags']
                
                #Add the new ones to the overall tag list
                for tag in tags:
                    if(tag not in all_unique_tags):
                        all_unique_tags.append(tag)
                #time.sleep(2)
                notes = client.notes(post['blog_name'], post['id'])
                yield ['tags:' + str(tags), 'notes: ' + str(notes)]
            else:
                print("Can't find ID for post")

client = pytumblr.TumblrRestClient('9qrx1tFz5fkXYRbyoxK2r4D5JKZNzVqkVxg7DEa7Wm4vzRmP2j',
  'hpUYHxeDnuTL2sf76c9eoN8NqmS9mohPU7ltoGcXfXcClChWNd',
  'CnxE2FveIxmr7WHUMGqZUIxo1NElIggaRWJoEIFeOPHbHwjAEw',
  'QvQaJoUPeVVrkBhVvBvDqqULy6L81UPC6eJVYVkyC07lTGEvpg')

#Make a list of all unique tags to keep feeding the function
#all_unique_tags = np.empty(10)
all_unique_tags = ['thinspo']
os.chdir("C:\\Users\\User\\Downloads\\tumblrPostInfo")
i=0

#The list of tags will change 
while i<len(all_unique_tags):
    
    #The list will hopefully expand as we go
    tag=all_unique_tags[i]
    print(i)
    try: 
        with open(f'{tag}-posts.txt', 'w', encoding='utf-8') as file:
            for notes in get_all_notes_and_tags(client, tag, all_unique_tags):
                if(notes == 'too many requests'):
                    #Need to throw exception instead
                    print("too many requests")
                    break
                file.write(str(notes))
        print(f'{tag} done')
    except:
        print(f'{tag} not done')

    i+=1
    #time.sleep(2)