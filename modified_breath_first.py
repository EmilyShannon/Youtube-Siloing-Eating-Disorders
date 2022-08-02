from genericpath import exists
import json
from unittest import result
from nbformat import write

from selenium_stealth import stealth
import anytree.search
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
from anytree import Node, AnyNode, NodeMixin, RenderTree, AbstractStyle, ContStyle, AsciiStyle
from anytree.exporter import JsonExporter
from collections import deque
import asyncio
import numpy as np
import os
import random
import sys
import uuid
import getpass
import pandas as pd
import csv
from selenium.webdriver.common.keys import Keys

class vid_scraper:
    def __init__(self, path_driver):
                self.path = path_driver
            #    self.profile_path = profile_path
                self.driver = self.create_chrome_driver()
             #   print("Driver created successfully")
                self.homepage = []
                self.depth = 0
                self.seed_url = None
            #    self.history = history
                self.max_wait = None
            #    self.trial_id = None
                self.num_recommendations = None
            #    self.username = None
            #    self.password = None
                self.tree = None
    def collect_data(self, url: str, ads: bool):

            length = self.get_length()

            self.driver.execute_script('window.scrollTo(0, 540)')

            title = self.get_title()
            creator = self.get_creator()
            description = self.get_description()
            dates = self.get_date()
            views = self.get_views()

            number_comments = self.get_num_comments()

            url = url
            id = self.video_url_to_id(url)

            likes, dislikes = self.get_likes_dislikes()

            # tags = self.get_tags(soup=soup)
            top_3_comments = self.get_top_comments() 
            ads = ads

            video = {
                'title': title,
                'content creator': creator,
                'description': description,
                'date': dates,
                'views': views,
                'comments': number_comments,
                'top_3_comment' : top_3_comments,
                'likes': likes,
                'dislikes': dislikes,
                # 'tags':tags,
                'video_length': length,
                'url': url,
                'ad': ads,
                'id': id
            }

            return video
    def get_top_comments(self):
        try:
            comments = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.ID, 'comment')))
            top_comments = [comments[i].text for i in range(0,3)]
            return "Comment 1: " + top_comments[0] + ", Comment 2: " + top_comments[1] + ", Comment 3: " + top_comments[2]
                
        except:
            return "Error found"
    def get_num_comments(self) -> str:
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="count"]/yt-formatted-string/span[1]')))
            element = element.text
            return element
        except:
            return 'Error found'

    def video_url_to_id(self, url) -> str:
        s = url.split('=')
        return s[1]

    def get_tags(self, soup):
        # open("index.html", "w").write(response.html.html)
        # initialize the result
        try:
            tags = ', '.join([meta.attrs.get("content") for meta in soup.find_all(
                "meta", {"property": "og:video:tag"})])
            return tags
        except:
            return 'Error found'

    def get_likes_dislikes(self) -> str:
        try:
            result = [i.get_attribute("aria-label") for i in self.driver.find_elements(by= By.XPATH, value= '//yt-formatted-string[@id="text"]') if i.get_attribute("aria-label") != None]

            likes = [i for i in result if (
                    'like' in i) and ('dislike' not in i)]
            dislikes = [i for i in result if ' dislike' in i]

            return likes[0] if (len(likes) != 0) else 'Unavailable', dislikes[0] if (
                        len(dislikes) != 0) else ' Unavailable'
        except:
            return 'Error found'

    def get_title(self) -> str:
        try:
            #return self.driver.find_element(by= By.XPATH, value='///*[@id="container"]/h1/yt-formatted-string').text
            return self.driver.find_elements(by= By.XPATH, value= '//*[@id="container"]/h1/yt-formatted-string')[0].text
        except:
            return 'Error found'

    def get_creator(self) -> str:
        try:
            return self.driver.find_elements(by= By.XPATH, value= '//*[@id="text"]/a')[0].text
        except:
            return 'Error found'

    def get_views(self) -> str:
        try:
            return self.driver.find_elements(by= By.XPATH, value= '//*[@id="count"]/ytd-video-view-count-renderer/span[1]')[0].text
        except:
            return 'Error found'

    def get_description(self) -> str:
        try:
            description = self.driver.find_elements(by= By.XPATH, value= '//*[@id="description"]/yt-formatted-string')[0].text
            #more_button = self.driver.find_element(by=By.XPATH, value= '//*[@id="more"]')
            #This button is making the error
            #more_button.click()
            #rest = self.driver.find_element(by= By.XPATH, value='//*[@id="description"]/yt-formatted-string/span[5]').text
            return description
        except:
            return 'Error found'

    def get_date(self) -> str:
        try:
            return self.driver.find_elements(by= By.XPATH, value= '//*[@id="info-strings"]/yt-formatted-string')[0].text
        except:
            return 'Error found'

    def get_video_recommendations(self, parent_url: str, main_tab, current_tab) -> list:
        self.driver.switch_to.window(current_tab)
        #print('     -recommended', end='')
        recommended_videos = []
        x = 0
        # find the video in the tree
        node = anytree.search.find(self.tree,
                                   filter_=lambda node: node.id == parent_url)
        path = '//*[@id="related"]/ytd-watch-next-secondary-results-renderer//*[@id="thumbnail"]'
        recommendations = self.driver.find_elements(by= By.XPATH, value= path)
        for i in recommendations:
            video_url = i.get_attribute('href')

            # only add the videos not seen before
            if (anytree.search.find(self.tree, filter_=lambda node: node.id == video_url) == None) and not (
                    video_url in recommended_videos) and not (video_url == None):
                recommended_videos.append(video_url)

                # add recommended videos as children
                AnyNode(id=video_url, parent=node, video=None, title=None)
                x += 1
            else:
                continue
            if (x == self.num_recommendations):
                break

        # figure out depth of the new node for the homepage_snapshot
        node = self.tree
        depth = 0
        while len(node.children) != 0:
            node = node.children[len(node.children) - 1]
            depth += 1

        # since we fill the tree
        if depth > self.depth:
            videos = self.homepage_snapshot(main_tab)
            self.homepage.append(videos)
            self.depth += 1

        return recommended_videos

    def get_by_xpath(self, xpath):
        try:
            return self.driver.find_element(by= By.XPATH, value= xpath)
        except:
            return 'Error found'
    def homepage_snapshot(self, main_tab):
        print('     -homepage')
        self.driver.switch_to.window(main_tab)
        time.sleep(2)
        # reload YouTube homepage
        self.driver.get('https://www.youtube.com/')
        time.sleep(3)
        # will contain list of 20 ish videos of the homepage
        elements = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="contents"]/ytd-rich-grid-row//*[@id="contents"]//*[@id="thumbnail"]')))
        videos = [i.get_attribute('href') for i in elements]

        print('         -success')
        return videos

    def geometric_series_calc(self, num_reco: int, depth: int) -> int:
            x = 0
            for i in range(0, depth):
                x = x + num_reco ** i
            return x
    def video_processing(self, url: str, main_tab: str, current_tab: str, res: list, index: int):
            print('video processing')
            try:
                self.driver.switch_to.window(current_tab)
                self.driver.get(url)
                # wait for the video to be loaded
                time.sleep(1)
                # skip the data protection button if it appears
                try:
                    self.driver.find_elements(by=By.XPATH, value='//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/span')[0].click()
                except:
                    # skip the data protection button if it appears
                    try:
                        self.driver.find_elements(by=By.XPATH, value= '/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[2]/div[2]/div[5]/div[2]/ytd-button-renderer[2]/a/tp-yt-paper-button/yt-formatted-string')[0].click()
                    except:
                        pass
                    pass
                # skip ad
                time.sleep(2)
                ad = None
                while (self.check_ad() == True):
                    ad = True
                    self.skip_ad()
                    time.sleep(2)
                # change to just check whether the video is playing or not (ie. if the big button is discoverable & no ads)
                if (ad == None):
                    self.start_video()

                # collect the features
                video = self.collect_data(url=url, ads=ad)
                # watch the video for a little, simulate a person

                #Don't need to watch the video b/c just collecting data
                # try:
                #     await asyncio.sleep(min(video['video_length'], self.max_wait))
                # except:
                #     video['video_length'] = None

                # get the recommended videos
                recommended = self.get_video_recommendations(parent_url=url, main_tab=main_tab, current_tab = current_tab)

                self.driver.switch_to.window(current_tab)
                self.driver.close()
                self.driver.switch_to.window(main_tab)

                res[index] = (video, recommended)
            except:
                res[index] = ('Error found', 'Error found')

            print(f'     -video processing: {video["title"]} by {video["content creator"]}, {video["video_length"]}')
            
            
    def start_video(self):
        # click on the button to start if the video is not playing (ie. if there were no ads before it)
        try:
            element = self.driver.find_element(by= By.XPATH, value= "//button[@class='ytp-large-play-button ytp-button']")
            element.click()
        except ElementNotInteractableException:
            pass

    def check_ad(self) -> bool:
            ads = self.driver.find_elements(by= By.CSS_SELECTOR, value= 'button[id^=visit-advertiser] > span.ytp-ad-button-text')
            if (len(ads) == 0):
                return False
            else:
                return True

    def skip_ad(self):
        time.sleep(5)
        # wait for the end of the advertisement
        try:
            # first make sure it can be skipped by finding the ad text button
            element = self.driver.find_elements(by= By.XPATH, value= '//*[contains(@id, "ad-text:")]')
            for i in element:
                # my code works for both french YouTube and anglohpone YouTube
                if (i.text == 'Skip Ads' or i.text == 'Skip Ad' or i.text == "Passer les annonces" or i.text == "Ignorer l'annonce"):
                    self.driver.find_elements(by= By.XPATH, value= '//*[@class="ytp-ad-skip-button ytp-button"]')[0].click()
                    break
        except TimeoutException:
            pass

    def get_length(self):
        try:
            return self.driver.execute_script("return document.getElementById('movie_player').getDuration()")
        except:
            return "Error found"

    def run_scraper(self, url_seed: str, max_wait: int, 
                  #  username: str, 
                  #  password: str, 
                    num_reco: int, depth: int,
                    #videos_parallele: int,
                    trial_id: str
                    ):
        
        print('     -running scraper')
        queue = deque([url_seed])
        root = AnyNode(id=url_seed, parent=None, video=None, title=None)
        self.tree = root
        self.max_wait = max_wait
       # self.username = username
       # self.password = password
        self.num_recommendations = num_reco

        main_window = self.driver.window_handles[-1]

        # main_window = self.login(main_tab=main_window,
        #                             username=self.username,
        #                             password=self.password)
        # main_window = self.delete_history(main_tab=main_window)

        # will have reloaded right before this call
        self.homepage.append(self.homepage_snapshot(main_tab=main_window))

        num_limit = self.geometric_series_calc(num_reco=num_reco, depth=depth)
        videos_watched = []

        iteration = 0
        while ((num_limit - len(videos_watched)) != 0):
            #self.driver.quit()

            # restart driver and login to speed up the process
            #self.driver = self.create_chrome_driver()
            main_window = self.driver.window_handles[-1]
            # main_window = self.login(main_tab=main_window,
            #                             username=self.username,
            #                             password=self.password)

            print(f'----Iteration {iteration}----')
            iteration = iteration + 1

            # array of video urls to watch
            tasks = []
            # determines how many videos will be watched at the same time
            to_watch = min(
                #videos_parallele, 
                len(queue),
                            num_limit - len(videos_watched))

            for i in range(0, to_watch):
                x = queue.popleft()
                tasks.append(x)
                videos_watched.append(x)

            # this array will receive the results of the scraping
            results = [None for i in tasks]

            #This will fill in results
            self.video_handling(url_list=tasks,main_tab=main_window, results=results)
         
            #video_processing(tasks, main_window, current_tab: str, res: list, index: int)
            
            for r in results:
                if r[0] != 'Error found':
                    node = None
                    # find the node with the url since it is stored in the tree before it is watched
                    if (root.video == None):
                        root.video = r[0]
                        root.title = r[0]['title']
                        node = root
                    else:
                        for n in anytree.LevelOrderIter(root):
                            if (n.id == r[0]['url']):
                                node = n
                                node.title = r[0]['title']
                                node.video = r[0]
                            else:
                                continue
                    for i in r[1]:
                        queue.append(i)
            print('')
        # check whether you need to refresh here or not
        self.homepage.append(self.homepage_snapshot(main_tab=main_window))

        #print(RenderTree(self.tree, style=ContStyle()))
        # ---Save results to a CSV file----
        print('     -writing to file')
        path_to_directory = f'{os.getcwd()}/Breadth_{keyword}'

        # put homepage in directory
        for i in range(0, len(self.homepage)):

            #Try adding a mkdir command to make this work
            path_to_file = f'{path_to_directory}/homepage/{keyword}_homepage_{i}_{trial_id}.txt'
            
            #If the directory doesn't exist then create it
            if(not exists(f'{path_to_directory}/homepage')):
                os.mkdir(f'{path_to_directory}/homepage')
            
            with open(path_to_file, 'w+') as outfile:
                for element in self.homepage[i]:
                    if isinstance(element, str):
                        outfile.write(element + '\n')
            outfile.close()

        # put tree into file
        if(not exists(f'{path_to_directory}/tree')):
            os.mkdir(f'{path_to_directory}/tree')
        
        path_to_file = f'{path_to_directory}/tree/{keyword}_tree_{trial_id}.txt'
        exporter = JsonExporter(indent=2, sort_keys=True)
        with open(path_to_file, 'w+') as outfile:
            exporter.write(root, outfile)
        outfile.close()

    def video_handling(self, url_list: list, main_tab: str, results: list):
        # print('videos_handling')
        tasks = []
        for url, i in zip(url_list, list(range(0, len(url_list)))):
            # open new tab and pass it for new video to watch
            self.driver.execute_script("window.open('');")
            new_tab = self.driver.window_handles.pop()

            tasks.append(self.video_processing(url=url, main_tab=main_tab, current_tab=new_tab, res=results, index=i))
        #return tasks


    def create_chrome_driver(self):
            options = webdriver.ChromeOptions()
            # print('Creating options')
            options.add_argument("start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument("--mute-audio")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-web-security")
            options.add_argument("--lang=en-US")
            options.add_argument('window-size=1920,1080')
        # options.add_argument(f"user-data-dir={self.profile_path}")
            options.add_argument(f"profile-directory=Default")

            # comment out in order to see the scraper interacting with webpages
            options.add_argument('--headless')
            s = Service(self.path)
            #print("Before return statement in create chrome driver")
            try:
             #   print("create_chrome_driver ran w/o exception")
                return webdriver.Chrome(service=s, options=options)
            except:
              #  print("create_chrome_driver ran w/ exception")
                return webdriver.Chrome(executable_path=self.path, options=options)

def get_search_results(keyword:str, driver):
    
    #Get the link for each vid
    try:
        element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="thumbnail"]'))
        )
        #Search for the keyword and scroll 
        search= driver.find_element_by_name("search_query")
        search.send_keys(keyword)
        search.send_keys(Keys.RETURN)
    

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, "filter-menu")))
        driver.execute_script('window.scrollTo(0, 540)')
        initial_vids = driver.find_elements(By.ID, "video-title")
        links = [vid.get_attribute("href") for vid in initial_vids]

        #open the current list in append mode
        with open(f"{os.getcwd()}\\{keyword}_seeds.txt", 'a') as file:
            
            for link in links:

                #write the link to the file
                if(str(link)!="None"):
                    try:
                        file.write('\n')
                        file.write(str(link))
                    except:
                        print(f"couldn't write to file: {keyword}_seeds.txt")

            file.close()
            
    except:
        print(f"couldn't open file: {keyword}_seeds.txt")       

    return f"{os.getcwd()}\\{keyword}_seeds.txt"

#Main
#Make a driver, get initial videos
keywords = ['anorexia', 'anorexia nervosa', 'binge', 'binge eating disorder', 'binge eating', 'bulimia', 'binge and purge', 'restrictive eating', 'diabulimia', 'extreme workout']

path = "path to chrome driver executable"
s = Service(path)
max_wait = 30
num_reco = 3
depth = 3

for keyword in keywords:
    o=webdriver.ChromeOptions()
    o.binary_location = "path to chrome executable"
    o.add_argument("start-maximized")
    o.add_experimental_option("excludeSwitches", ["enable-automation"])
    o.add_experimental_option('useAutomationExtension', False)
    o.add_experimental_option('excludeSwitches', ['enable-logging'])
    o.add_argument("--mute-audio")
    o.add_argument("--allow-running-insecure-content")
    o.add_argument("--disable-web-security")
    o.add_argument("--lang=en-US")
    o.add_argument('window-size=1920,1080')
    o.add_argument('--headless')

    driver = webdriver.Chrome(options=o, service=s)
    stealth(driver,
                    user_agent='DN',
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )
    driver.get("https://www.youtube.com/")
    time.sleep(2)
    seed_file_path = get_search_results(keyword, driver)
    seed_file = open(seed_file_path, 'r')
    time.sleep(2)
    seeds = seed_file.read()
    seeds=seeds.split('\n')
    driver.quit()

    #Create te corrsponding folder
    if(not os.path.exists(f"{os.getcwd()}/Breadth_{keyword}")):
        os.mkdir(f"{os.getcwd()}/Breadth_{keyword}")
    #Avoid using an empty seed
    #clean up seeds
    seeds = [seed for seed in seeds if seed !='' and seed!="None"]
    for url_seed in range(0, min(len(seeds), 30)):
        if(seeds[url_seed]!="") and (seeds[url_seed]!="None"):
            output = None
            times = 0
            while output != 1:
                try:
                    ###############------=CHANGE PATH=------###############
                    # change this path to where you saved the Chromedriver
                    print('##################################\n##################################\n')
                    print(f'Creating the scraper for seed: {url_seed}')
                    scraper = vid_scraper(path_driver=path)
                    scraper.run_scraper(seeds[url_seed],
                                        max_wait=max_wait,
                                        # change username and password
                                        #username=username,
                                        #password=password,
                                        num_reco=num_reco,
                                        depth=depth,
                                        #videos_parallele=videos_parallele,

                                        # make your own trial_id
                                        trial_id=f'trial_{uuid.uuid4()}')
                            
                    scraper.driver.quit()
                    print('\n\nDone!')

                    output = 1
                    times += 1
                except Exception as e:
                    print('\n\nStarting again !')
                    #scraper.driver.quit()
                    if times > 5:
                        raise Exception(f'Multiple attempts to run the scraper failed. \nLast error was : {sys.exc_info()[2]}')
                    print(f'error: {e}\n{sys.exc_info()[2]}')


