#!/usr/bin/env python
# coding: utf-8

# In[483]:


import uuid
import requests
import configparser
from praw import Reddit
import discord
import nest_asyncio
import os
from datetime import datetime


# In[484]:


CONFIG_FILENAME="config.ini"
nest_asyncio.apply()


# In[485]:


def read_config(filename, section):
    config = configparser.ConfigParser()
    config.read(filename)
    config = config[section]
    return dict(config.items())

def is_image_or_gif(url):
    extensions = ('.jpg', '.jpeg', '.png', '.gif')
    return url.endswith(extensions)

def is_from_gfycat(url):
    return 'gfycat' in url

def extract_video_url_if_video(media):
    if media is not None and isinstance(media, dict):
        reddit_video = media.get('reddit_video')
        if reddit_video is not None:
            fallback_url = reddit_video.get('fallback_url')
            return fallback_url
    return None

def escape_characters(title):
    characters = ('<', '>', ":", '"', '/', '\\', '|', "?", '*')
    names = ('CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9'
              'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9')
    char_escape = lambda char: char not in characters
    title = "".join(filter(char_escape, title)).strip()
    if len(title) == 0 or title.upper() in names:
        title = "random title " + str(uuid.uuid4())
    title = title[0:240]
    return title

def create_dict(title, url, extension):
    return {'title': title, 'url': url, 'extension': extension}

def handle_gfycat(title, url):
    title = escape_characters(title)
    url += ".gif"
    extension = ".gif"
    return create_dict(title, url, extension)

def handle_image_or_gif(title, url):
    title = escape_characters(title)
    extension = '.' + url.split('.')[-1]
    return create_dict(title, url, extension)

def handle_video(title, url):
    title = escape_characters(title)
    extension = '.mp4'
    return create_dict(title, url, extension)

def save_submission(extracted_submission):
    with open (extracted_submission.get('title') + extracted_submission.get('extension'), 'wb') as file:
        file.write(requests.get(extracted_submission.get('url')).content)


# In[486]:


class RedditSubmissionsReader():
    def __init__(self):
        self.read_config()
        self.reddit_client = Reddit(client_id=self.client_id, client_secret=self.client_secret, user_agent=self.user_agent)        
    
    def read_config(self):
        reddit_config = read_config(filename=CONFIG_FILENAME, section='REDDIT')
        self.client_id = reddit_config.get('client_id')
        self.client_secret = reddit_config.get('client_secret')
        self.user_agent = reddit_config.get('user_agent')
        self.subreddit = reddit_config.get('subreddit')
        self.category = reddit_config.get('category').lower()
        self.limit = int(reddit_config.get('limit'))
    
    def get_submissions(self):
        subreddit = self.reddit_client.subreddit(self.subreddit)
        if self.category == 'new':
            submissions = subreddit.new(limit=self.limit) if self.limit is not None else subreddit.new()
        elif self.category == 'rising':
            submissions = subreddit.rising(limit=self.limit) if self.limit is not None else subreddit.rising()
        elif self.category == 'top':
            submissions = subreddit.top(limit=self.limit) if self.limit is not None else subreddit.top()
        else:
            submissions = subreddit.hot(limit=self.limit) if self.limit is not None else subreddit.hot()
        return self.extract_submissions_data(submissions)
        
    def extract_submissions_data(self, submissions):
        extracted_submissions = []
        for submission in submissions:
            if submission.over_18:
                continue
            title = submission.title
            url = submission.url
            media = submission.media
            if is_from_gfycat(url):
                extracted_submissions.append(handle_gfycat(title, url))
            elif is_image_or_gif(url):
                extracted_submissions.append(handle_image_or_gif(title, url))
            else:
                video_url = extract_video_url_if_video(media)
                if video_url is not None:
                    extracted_submissions.append(handle_video(title, video_url))
        return extracted_submissions


# In[487]:


def send_submissions_to_discord():
    discord_client = discord.Client(intents=discord.Intents.default())
    discord_config = read_config(filename=CONFIG_FILENAME, section='DISCORD')
    reddit_config = read_config(filename=CONFIG_FILENAME, section='REDDIT')
    async def send():
        channel = discord.utils.get(discord_client.get_all_channels(), name=discord_config.get('guild'))
        log = f'''Getting submissions from r/{reddit_config.get('subreddit')} category: {reddit_config.get('category')}'''
        if reddit_config.get('limit') is not None:
           log +=  f''' limit: {reddit_config.get('limit')}'''
        print(log)
        submissions_reader = RedditSubmissionsReader()
        submissions = submissions_reader.get_submissions()
        print(f'''Sending reddit submissions to channel {discord_config.get('guild')}''')
        for submission in submissions:
            await channel.send(submission.get('title'))
            await channel.send(submission.get('url'))
        print('Sent all reddit submissions')

    @discord_client.event
    async def on_ready():
        print(f'Discord client {discord_client.user} is ready')
        await send()
        
    discord_client.run(discord_config.get('token'))


# In[491]:


def save_submissions_locally():
    reddit_config = read_config(filename=CONFIG_FILENAME, section='REDDIT')
    log = f'''Getting submissions from r/{reddit_config.get('subreddit')} category: {reddit_config.get('category')}'''
    if reddit_config.get('limit') is not None:
       log +=  f''' limit: {reddit_config.get('limit')}'''
    print(log)
    submissions_reader = RedditSubmissionsReader()
    submissions = submissions_reader.get_submissions()
    print('Saving reddit submissions')
    dir_name = str(datetime.now())
    dir_name = dir_name.replace(':', ',')
    os.mkdir(dir_name)
    os.chdir(dir_name)
    for submission in submissions:
        try:
            save_submission(submission)
        except Exception as e:
            print(e)
    print('Saved all reddit submissions')
    os.chdir('..')  


# In[492]:


if __name__ == '__main__':
   send_submissions_to_discord()

