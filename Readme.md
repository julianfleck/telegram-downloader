# A Simple Telegram Channel/Chat History Downloader

This script allows you to retrieve the history of a Telegram channel and save it as JSON. Before running the script, ensure you have the required packages installed as specified in the `requirements.txt` file.

Currently only text chats are supported. If you have a Telegram premium account, feel free to implement the `transcribe_audio_message()` function in `history.py`. I haven’t implemented it yet, because I’m cheap and didn’t want to sign up for a premium account :)

## Setup
1. Obtain `api_id` and `api_hash` by creating an app on Telegram. You can obtain these by creating an app on [Telegram](https://my.telegram.org/apps).
2. Set up local variables or environment variables for `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`.

## Usage
Run the script with the following command line inputs:
- `chat_name`: The name of the chat for which you want to get the history
- `--api_id`: Your API ID (if not set, the script will try to use the `TELEGRAM_API_ID` environment variable)
- `--api_hash`: Your API hash (if not set, the script will try to use the `TELEGRAM_API_HASH` environment variable)
- `--file`: The ID of the channel for which you want to get the history
- `--limit`: The maximum number of posts to retrieve
- `--offset_date`: The date from which the history should be retrieved
- `-v`, `--verbose`: Print verbose output

The script will save the channel history in a JSON file named `history.json`.

## Instructions
1. Ensure required packages are installed.
2. Set up `api_id` and `api_hash`.
3. Run the script with the necessary command line inputs.