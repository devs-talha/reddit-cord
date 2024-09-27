# RedditCord

**RedditCord** is a Python-based bot that fetches images from specified subreddits and posts them directly to your Discord server. This tool allows you to automate the process of sharing content from Reddit with your Discord community.

## Features

- **Subreddit Integration:** Fetches images from any subreddit of your choice.
- **Discord Integration:** Automatically posts the fetched images to a specified Discord channel.
- **Configurable:** Easy setup through a configuration file, allowing you to customize the subreddits and Discord channels.
- **Asynchronous Execution:** Efficient handling of requests using asynchronous programming.

## Installation

To get started with RedditCord, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/devs-talha/reddit-cord.git
   cd reddit-cord
   ```

2. **Install the required dependencies:**

   Make sure you have Python 3.8+ installed, then run:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The bot is configured using a `config.ini` file. Here’s an example of how to set it up:

```ini
[REDDIT]
client_id=your_reddit_client_id
client_secret=your_reddit_client_secret_key
user_agent=bot user agent
subreddit=aww
category=hot
limit=1000

[DISCORD]
token=your_discord_bot_token
guild=aww
```

## Usage

Once configured, you can run the bot with:

```bash
python reddit_submissions.py
```

The bot will start fetching images from the specified subreddit and posting them to your Discord channel.

## Contributions

Feel free to fork this repository, open issues, or submit pull requests to contribute to **RedditCord**.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
