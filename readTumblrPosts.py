#Make a csv file to store tags and reply text
import csv
import json as js
import ast

with open("C:\\Users\\User\\Downloads\\tumblrPostInfo\\thinspo-posts.csv", 'a', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)

    #Open the file where the tagged posts notes are stored
    with open("C:\\Users\\User\\Downloads\\tumblrPostInfo\\thinspo-posts.json", 'r', encoding='utf-8') as file:
        
        #Read posts from the list,but each is a json dictionary
        posts=js.load(file)

        #Pick out the tags and reply text (if any)
        for post in posts: 

            post_notes = []

            #Save the tags and note text to a csv file
            tags = post['tags']

            #There may be multiple of these though
            notes = post['notes']
            notes = ast.literal_eval(notes)
           
            #This is just taking string chars
            for note in notes['notes']:
                
                #Only want the notes with reply text, not the likes and reblogs
                if 'reply' in note['type']:
                    #print('found a reply:' + note['reply_text'])
                    post_notes.append(note['reply_text'])
            
            line = [tags, post_notes]
            #Write to the CSV
            writer.writerow(line)