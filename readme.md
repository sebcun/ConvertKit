# ConvertKit

A file conversion tool available as a website, Discord bot, and Slack bot. Easily convert between different file formats with a plugin-based system. A simple framework for creating plugins can be found here:

## Demo

[Live Demo (website)](https://convertkit.sebcun.com)
[Discord Bot Demo](https://streamable.com/rqkvxc)
[Slack Bot Demo]()

## Setup

### Requirements

Install dependencies:

```bash
pip install flask discord.py python-dotenv slack-bolt requests pillow pdf2docx python-docx python-pptx
```

### Website

1. Run the Flask web app:

```py
python app.py
```

2. Visit http://localhost:5000 in your browser.

### Discord Bot

1. Create a .env file:

```
DISCORD_BOT_TOKEN=your_bot_token_here
```

2. Run the bot:

```py
python bot.py
```

3. Use /convert to upload and convert files, or /conversions to list available conversions.

### Slack Bot

1. Create a .env file:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
```

2. Run the bot:

```py
python slack.py
```

3. Use /convert to upload and convert files, or /conversions to list available conversions.
