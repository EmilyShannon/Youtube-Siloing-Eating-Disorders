#Using the tumblr API to get post information
import pytumblr

#Collect posts under a given tag and print their urls
def get_all_notes(client, tag:str):
    
    #This will baically track how many posts we've already seen
    offset = 0
    response = client.tagged(tag, limit=20, 
    #offset=offset, 
    notes_info = True)
    
    if not response:
        print('Could not get tagged posts')
        return
    #For every post, get the tags and notes
    for post in response:
        if('id' in post):
            tags_notes = [post['tags'], client.notes(post['blog'], post['id'])]
            yield tags_notes
        else:
            print("Can't find ID for post")
    #Increment the offset to not repeat the posts 
    #offset += 20

#Need to get an API key first
client = pytumblr.TumblrRestClient('API KEY HERE')

tag=''

with open(f'{tag}-posts.txt', 'w') as file:
    for notes in get_all_notes(client, tag):
        print(notes, file=file)