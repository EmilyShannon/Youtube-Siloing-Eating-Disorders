from datetime import datetime
import os
import time
import pytumblr
import json as js

#Collect posts under a given tag
def get_all_notes_and_tags(client, 
                            tag:str,   
                            #count:int,
                            #all_unique_tags:list
                            ):
    global count
    global all_unique_tags
    #make a loop to be able to get more posts, about 500 per tag
    for i in range(24):

        min_timestamp=0

        #Get 20 posts with the given tag before the given timestamp

        #Initialize the list of posts using the default (current) timestamp
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


#Setting up

#Make a list of all unique tags to keep feeding the function
#There's one in there as a seed 
all_unique_tags = ['thinspo']

os.chdir("YOUR PATH\\tumblrPostInfo")

#This is the index along the list. Don't reset it since we want to keep moving within the list
i=0

#Authentication
client = pytumblr.TumblrRestClient('YOUR KEYS)

while i<len(all_unique_tags):

    try:

        #Tracks how many requests have been sent to the server. Reset on each run
        count = 0

        #print('On tag: ', i)
        #print('Length of list: ', len(all_unique_tags))
        
        #Only send 1000 requests per hpur
        while count<1000:

            #The list will expand as we go
            tag=all_unique_tags[i]

            #Check if it's already been done
            if tag!='thinspo' and os.path.exists(f'{os.getcwd()}\\{tag}-posts.json') and os.path.getsize(f'{os.getcwd()}\\{tag}-posts.json') != 0:
                #If yes, go to the next tag
                i+=1
                continue
            else:
                
                try: 
                    #Make a json file for each tag
                    with open(f'{tag}-posts.json', 'w', encoding='utf-8') as file:
                        
                        #Overall list that will be written to the file
                        posts_info=[]

                        #Get the time that the function is called at
                        initial_time = datetime.now()
                        print('before get all notes')
                        #This works b/c of using yield
                        for notes in get_all_notes_and_tags(client, tag):
                            if(notes == 'too many requests'):   
                                raise TooManyRequestsError

                            else:
                                #Add the info to the list of post info for that tag
                                posts_info.append(notes)
                        
                        print('after get all notes')
                        #Write the list of posts to the json file
                        js.dump(posts_info, file)
                        
                        final_time = datetime.now()
            
                        print('Num of requests sent: ' + str(count))
                        
                        print('Time passed: ' + str(final_time-initial_time))
                    
                    #Move onto the next tag
                    print(f'{tag} done')
                    i+=1

                    #Wait for one minute between tags b/c of 300 calls/min limit
                    print('Pausing for one minute')
                    time.sleep(60)

                except TooManyRequestsError:

                    #If there are too many requests, wait an hour to 
                    print('Number of requests sent: ', count)
                    print('Sent too many requests. Wait for a bit.')
                    break

                    
                except Exception as e:
                    #Display the error
                    print(f'Exception occurred: {e}')

                    #Find out whether it's the tags liSst giving this error
                    
                    print('While on index ', i)
                    print('Length pf list: ', len(all_unique_tags))
                    break

        
        print('taking an hour break at ', datetime.now())
        #Sleep for an hour to reset the request rate
        time.sleep(3600)

    except Exception as e:
        print(f'Exception occurred (in outer loop): {e}')
        break
