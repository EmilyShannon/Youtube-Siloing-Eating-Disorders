import pytumblr

#Collect posts under a given tag and print their urls
def get_all_posts(client, tag:str):
    #offset = None
    #Using offset to only view posts older than the last one seen
    response = client.tagged(tag, limit=20)
    # before=offset)
    
    for post in response:
        
        if('photos' not in post):
            #Get the image sources
            if('body' in post):
                body = post['body']
                body = body.split('<')
                body = [b for b in body if 'img src=' in b]
                if(body):
                    body = body[0].split('"')
                    print(body[1])
                    yield body[1]
                else:
                    yield
        else:
            print(post['photos'][0]['original_size']['url'])
            yield post['photos'][0]['original_size']['url']

    #
   # offset = response[-1]['timestamp']
  #  print(offset)

#Need to get an API key first
client = pytumblr.TumblrRestClient('API KEY HERE')

tag=''

with open(f'{tag}-posts.txt', 'w') as file:
    for post in get_all_posts(client, tag):
        print(post, file=file)