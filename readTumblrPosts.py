#Make a csv file to store tags and reply text
import csv
import ast
import os

#Will have TumblrPostsInfo folder from running TumblrScraper
directory = os.fsencode("C:\\Users\\User\\Downloads\\tumblrPostInfo")
os.chdir(directory)

for file in os.listdir(directory):
    
    filename = os.fsdecode(file)
    
    size = os.path.getsize(filename)
    
    if(filename.endswith(".json") and size != 0):
        
            
            with open(f"C:\\Users\\User\\Downloads\\tumblrPostInfo\\{os.path.splitext(filename)[0]}.csv", 'a', encoding='utf-8') as csv_file:
                try:
                    writer = csv.writer(csv_file)
                   
                    #Open the file where the tagged posts notes are stored
                    with open(filename, 'r', encoding='utf-8') as json_file:
                        
                        #Read the list of dictionaries
                        posts = ast.literal_eval(json_file.read())

                        #Pick out the tags and reply text (if any)
                        for post in posts: 
                            
                            post_notes = []

                            #Save the tags and note text to a csv file
                            tags = ast.literal_eval(post['tags'])

                            #There may be multiple of these though
                            notes = ast.literal_eval(post['notes'])
                            
                            #There is a list of notes, followed by other information that we do not need
                            notes = notes['notes']

                            for note in notes:
                                
                                #Only want the notes with reply text, not the likes and reblogs
                                if 'reply' in note['type']:
                                    # print('file: ', filename)
                                    # print('found a reply:' + note['reply_text'])
                                    post_notes.append(note['reply_text'])
 

                            #Attempt to solve 'utf-8' codec can't encode characters in position X: surrogates not allowed
                            for tag in tags:
                                if('\\ud' in tag):
                                    tags.remove(tag)

                            for note in post_notes:
                                if('\\ud' in note):
                                    post_notes.remove(tag)
                            
                            #We now have the tags and response text
                            line = [tags, post_notes]

                            try:
                                
                                #Write to the CSV
                                writer.writerow(line)
                               
                            except:
                                print("couldn't write line")

                except Exception as e:

                    print(f'exception occured: {e}')
                    continue