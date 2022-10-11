import csv
import enum
import json
import praw
from requests import Session
import os

#Start the session using oauth keys
session = Session()
reddit = praw.Reddit(
    client_id="hRkZ4kLCrusBj5LQA779mA",
    client_secret="QpyLvbF5OlSroY-zLLMn3Bx8R9TVag",
    password="LypsylBlu3",
    user_agent="youtube-siloing-eating-disorders personal use script by u/Feeling_Rip_1307, https://github.com/EmilyShannon/Youtube-Siloing-Eating-Disorders",
    username="Feeling_Rip_1307",
)

with open('subreddits-list.txt', 'r', encoding='utf-8') as subs_list, open('neutral_subreddits_list.txt', 'r', encoding='utf-8') as neutral_subs_list:
    subs_list = subs_list.readlines()
    neutral_subs_list = neutral_subs_list.readlines()
    
    
    for sub_name in subs_list:
        
        try:
            #Strip the name of newline character
            sub_name = sub_name.strip()
            #Get the subreddit we want to search
            sub = reddit.subreddit(sub_name)

            #Get the newest 1000 posts on the subreddit
            posts = sub.new(limit=1000)

            #Get that subreddit's flair template (list of flairs in the sub) and get their text
            flair_template = sub.flair.link_templates
            flair_list = [flair['id'] for flair in flair_template]
            flair_list_text = [flair['text'] for flair in flair_template]
            print('Sub: ', sub_name, '// Flairs: ', flair_list_text)

            #Make a json file for each subreddit
            with open(f'{os.getcwd()}\\redditPostInfo\\{sub_name}_post_info.json', 'w', encoding='utf-8') as json_file:
                sub_info = []
                #writer = csv.writer(csv_file)
                
                #Go through the posts gathered and see if they have a flair
                for i, post in enumerate(posts):
                    #print(i, ': ', post.title )
                    
                    #Need to filter out posts w pics or videos; only want text
                    #Exclude surveys
                    if(post.is_self == True and 'survey' not in post.title.lower()):
                        
                        #Check the ones with flair first - clearer indicator
                        if(post.link_flair_text is not None):
                            #The flairs listed here are based on those in specific subreddits on the list 
                            if(post.link_flair_text.lower() in ['trigger warning', 'tw: numbers', 'oh no', 'fatphobia', 'strugging', 'vent', 'just venting', 'tw', 'cw']):
                                # print('Title: ', post.title, '\n')
                                # print('Flair: ', post.link_flair_text, '\n')
                                # print('Text: ', post.selftext)
                                label = 'Disordered'
                                
                            elif(post.link_flair_text.lower() in ['recovery win','recovery support', 'recovery', 'sanity', 'recovery story', 'recovery wins!', 'recovery progress', 'celebration', 'recovery related', 'wins']):
                                label = 'Recovery'
                            
                            #For recovery related flairs that have an emoji in them
                            elif(any(x in post.link_flair_text.lower() for x in ['encouragement', 'healing', 'success'])):
                                label = 'Recovery'
                            else:
                                continue

                        #Different cases to indicate that it is triggering content: trigger warning in the flair, in the text or in the title
                        elif((any(x in post.title.lower() for x in ['tw', 'cw', 'trigger warning'])) or (any(x in post.selftext.lower() for x in ['tw', 'cw', 'trigger warning']))):
                            
                            # print('Title: ', post.title, '\n')
                            # print('Text: ', post.selftext)
                            label = 'Disordered'
                            # post_info = [label, [post.title, post.selftext]]
                            # sub_info.append(post_info)

                        
                        #Get some neutral subs too    
                        else:
                            continue
                    
                    #Write the information of that post to the info for that subreddit
                    post_info = {label: post.title + '  ' + post.selftext}
                    #json.dump(post_info, json_file)
                    sub_info.append(post_info)
                
                    
                #Write all collected posts to the json for that sub
                json_file.write(str(sub_info))
        
        except Exception as e:
            print(f'Exception on {sub_name}: {e}')

    #Doing the same but for subreddits that I deem to be about food/exercise/body image but that don't revolve around eating disorders
    for sub_name in neutral_subs_list:
        
        try:
            #Strip the name of newline character
            sub_name = sub_name.strip()
            #Get the subreddit we want to search
            sub = reddit.subreddit(sub_name)

            #Get the newest 1000 posts on the subreddit
            posts = sub.new(limit=1000)
        
            with open(f'{os.getcwd()}\\redditPostInfo\\{sub_name}_post_info.json', 'w', encoding='utf-8') as json_file:
                sub_info = []
                #writer = csv.writer(csv_file)
                
                #Go through the posts gathered and see if they have a flair
                for i, post in enumerate(posts):
                    
                    #Need to filter out posts w pics or videos; only want text
                    #Filter out surveys
                    if((post.is_self == True) and ('survey' not in post.title.lower())):
                        #Check the ones with flair first - clearer indicator
                        if(post.link_flair_text is not None):
                            #The flairs listed here are based on those in specific subreddits on the list 
                            if(post.link_flair_text.lower() in ['trigger warning', 'tw: numbers', 'oh no', 'fatphobia', 'strugging', 'vent', 'just venting', 'tw', 'cw']):
                                # print('Title: ', post.title, '\n')
                                # print('Flair: ', post.link_flair_text, '\n')
                                # print('Text: ', post.selftext)
                                label = 'Disordered'
                                
                            elif(post.link_flair_text.lower() in ['recovery win','recovery support', 'recovery', 'sanity', 'recovery story', 'recovery wins!', 'recovery progress', 'celebration', 'recovery related', 'wins']):
                                label = 'Recovery'
                            
                            #For recovery related flairs that have an emoji in them
                            elif(any(x in post.link_flair_text.lower() for x in ['encouragement', 'healing', 'success'])):
                                label = 'Recovery'
                            else:
                                continue
                        #print('post.is_self == True')
                        #Some posts talk about weight or disordered eating and have a trigger warning. 
                        elif(any(x in post.title.lower() for x in ['cw', 'tw', 'trigger warning'])) or (any(x in post.selftext.lower() for x in ['cw', 'tw', 'trigger warning'])):
                            label='Disordered'
                    
                        #Otherwise we'll consider it neutral
                        else:
                            #print('Neutral')
                            label = 'Neutral'
                        
                        #Write the information of that post to the info for that subreddit
                        post_info = {label: post.title + '  ' + post.selftext}
                        
                        sub_info.append(post_info)
                    else:
                        continue
                    
                #Write all collected posts to the json for that sub
                json_file.write(str(sub_info))
                    
        except Exception as e:
            print(f'Exception on {sub_name}: {e}')

                

                    