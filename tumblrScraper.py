#Using the tumblr API to get post information
import os
import time
import pytumblr
import numpy as np
import json as js

#Tracks how many requests have been sent to the server
count = 0

#Collect posts under a given tag and print their urls
def get_all_notes_and_tags(client, tag:str, all_unique_tags):
    global count
    
    #make a loop to be able to get more posts
    for i in range(24):

        min_timestamp=0

        #Get 20 posts with the given tag before the given timestamp

        #Initialize the list of posts using the dedault (current) timestamp
        if(min_timestamp==0):
            response = client.tagged(tag, limit=20)
            #This is a request so increment the count
            count+=1
        
        #Otherwise, use the min timestamp
        else:
            count+=1
            response = client.tagged(tag, before=min_timestamp, limit=20)

       
        #Particular error if the server refusing to take more requests
        if 'meta' in response:
            yield 'too many requests'

        #Track the timestamps to find the oldest one and then search for more posts before that
        min_timestamp=response[0]['timestamp']

        #For every post, get the tags and notes
        for post in response:
            timestamp = post['timestamp']
            
            #Update the earliest timeS
            if(timestamp<min_timestamp):
                min_timestamp=timestamp
            
            if('id' in post):
                #Also get the post's tags
                tags = post['tags']
                
                #Add the new ones to the overall tag list
                for tag in tags:
                    if(tag not in all_unique_tags):
                        all_unique_tags.append(tag)
     

                #Get the notes on that post and update the number of requests sent
                notes = client.notes(post['blog_name'], post['id'])
                count+=1

                yield {"tags": str(tags), "notes": str(notes)}
        
            else:
                #If for some reason te post itself can't be retrieved
                print("Can't find ID for post")
        

#Define an exception that will be used when too many requests have been sent to the server 
class Error(Exception):
    pass
class TooManyRequestsError(Error):
    pass
client = pytumblr.TumblrRestClient('9qrx1tFz5fkXYRbyoxK2r4D5JKZNzVqkVxg7DEa7Wm4vzRmP2j',
  'hpUYHxeDnuTL2sf76c9eoN8NqmS9mohPU7ltoGcXfXcClChWNd',
  'CnxE2FveIxmr7WHUMGqZUIxo1NElIggaRWJoEIFeOPHbHwjAEw',
  'QvQaJoUPeVVrkBhVvBvDqqULy6L81UPC6eJVYVkyC07lTGEvpg')

#Make a list of all unique tags to keep feeding the function
#There's one in there as a seed 
all_unique_tags = ['thinspo']
os.chdir("C:\\Users\\User\\Downloads\\tumblrPostInfo")
i=0

#The list of tags will change 
while i<len(all_unique_tags):
    
    #The list will hopefully expand as we go
    tag=all_unique_tags[i]

    #Check if it's already been done
    if tag!='thinspo' and os.path.exists(f'{os.getcwd()}\\{tag}-posts.json') and os.path.getsize('os.getcwd()}\\{tag}-posts.json') != 0:
        i+=1
        continue
    else:
        #print(i)
        try: 
            #Make a json file for each tag
            with open(f'{tag}-posts.json', 'w', encoding='utf-8') as file:
                
                #Overall list that will be written to the file
                posts_info=[]

                #This works b/c of using yield
                for notes in get_all_notes_and_tags(client, tag, all_unique_tags):
                    if(notes == 'too many requests'):   
                        raise TooManyRequestsError

                    else:
                        posts_info.append(notes)
           

                #Write the list of posts to the json file
                js.dump(posts_info, file)

    
                #print('Num of requests sent: ' + str(count))
            print(f'{tag} done')

        #For either exception, the program terminates
        except TooManyRequestsError:
            #print('Num of requests sent: ' +str(count))
            print('Sent too many requests. Wait for a bit.')
            break

            
        except Exception as e:
            #with Exception as e:
            print(f'Exception occurred: {e}')
            break

        i+=1
