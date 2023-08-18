#Make a csv file to store tags and reply text
import csv
import ast
import os

#Will have TumblrPostsInfo folder from running TumblrScraper
directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tumblr_posts_info")
os.chdir(directory)

for file in os.listdir(directory):
    
    filename = os.fsdecode(file)
    
    size = os.path.getsize(filename)
    
    if(filename.endswith(".json") and size != 0):
        
            
            with open(f"seed_{os.path.splitext(filename)[0]}_tags.csv", 'a', encoding='utf-8') as csv_file:
                try:
                    writer = csv.writer(csv_file)
                   
                    #Open the file where the tagged posts notes are stored
                    with open(filename, 'r', encoding='utf-8') as json_file:
                        
                        #Read the list of dictionaries
                        posts = ast.literal_eval(json_file.read())

                        #Pick out the tags and reply text (if any)
                        for post in posts: 

                            #Save the tags and note text to a csv file
                            tags = ast.literal_eval(post['tags'])

                            #Attempt to solve 'utf-8' codec can't encode characters in position X: surrogates not allowed
                            for tag in tags:
                                if('\\ud' in tag):
                                    tags.remove(tag)
                            try:
                                
                                #Write to the CSV
                                writer.writerow(tags)
                               
                            except:
                                print("couldn't write line")

                except Exception as e:

                    print(f'exception occured: {e}')
                    continue