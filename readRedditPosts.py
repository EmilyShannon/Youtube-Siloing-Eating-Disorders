import glob
import pandas as pd
import os
import csv
import ast
import json
#Not gonna start each line with a label this way, put into lists
# df = pd.read_csv('redditPostInfo\\AnorexiaNervosa_post_info.csv')
# print(df)
directory = os.fsencode("C:\\Users\\User\\Downloads\\redditPostInfo")
os.chdir(directory)

for file in os.listdir(directory):
    
    filename = os.fsdecode(file)
    
    size = os.path.getsize(filename)
    
    csv_name = f"{os.path.splitext(filename)[0]}.csv"

    #If the json file isn't empty and we haven't already made a csv from it, then create one
    if(filename.endswith(".json") and size != 0):
    #and (not os.path.exists(csv_name)):
        with open(f"{os.path.splitext(filename)[0]}.csv", 'w', encoding='utf-8') as csv_file:
            try:
                #lines = []

                writer = csv.writer(csv_file)
                writer.writerow(['Label', 'Text'])
                #Open the file where the tagged posts notes are stored
                with open(filename, 'r', encoding='utf-8') as json_file:
                    
                    #Read the list of dictionaries
                    posts_string = json_file.read()
                    posts = ast.literal_eval(posts_string)

                    for post in posts:
                        label = list(post.keys())[0]
                        text = list(post.values())[0]

                        line = [label, text]
                    
       
                        
                        try:
                            
                            writer.writerow(line)
                            
                        except:

                            print("couldn't write line")

            except Exception as e:

                if("'utf-8' codec can't encode characters in position" in str(e)):
                    pass
                
                else:
                    print(f'exception occured: {e}')
                
                continue

#Finally, combine all of those into one csv file 
files = os.path.join("C:\\Users\\User\\Downloads\\redditPostInfo", "*_post_info.csv")
files = glob.glob(files)
df = pd.concat(map(pd.read_csv, files), ignore_index=True)

with open("C:\\Users\\User\\Downloads\\redditPostInfo\\all_reddit_posts_info.csv", 'w', encoding='utf-8') as file:
    print(df.groupby('Label').size())
    writer = csv.writer(file)
    writer.writerow(df.head())
    writer.writerows(df.values)