#!/usr/bin/env python3

# Script to get the history of a telegram channel.
# Before running this script, make sure to install the following packages:
# pip install telethon

# In order to set up telethon, you need to obtain the following:
# 1. api_id: You can obtain this by creating an app on telegram: https://my.telegram.org/apps
# 2. api_hash: You can obtain this by creating an app on telegram: https://my.telegram.org/apps

# The script accepts the following input parameters:
# 1. CHANNEL_ID: The ID of the channel for which you want to get the history
# 2. LIMIT: The maximum number of posts to retrieve
# 3. OFFSET_DATE: The date from which the history should be retrieved
# 4. OFFSET_ID: The ID of the message from which the history should be retrieved
# 5. MAX_ID: The maximum ID of the message to be retrieved
# 6. MIN_ID: The minimum ID of the message to be retrieved

# All dates are in the format of YYYY-MM-DD.
# All IDs are in the format of 123456789.

# The script will save the history in a file called history.json in the same directory.
# The file will contain the history of the channel in JSON format.

import os
import argparse
import json
import asyncio

import logging
from rich import inspect, print
from rich.logging import RichHandler
from rich.console import Console

from telethon import TelegramClient
from telethon import functions
import telethon.tl.types

# Set up a handler to print the logs to the console
console = Console()

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Get the history of a telegram channel.')

# Add the arguments
parser.add_argument('chat_name', type=str, help='The name of the chat for which you want to get the history', nargs=1)

parser.add_argument('--api_id', type=int, help='Your API ID', default=os.getenv('TELEGRAM_API_ID'))
parser.add_argument('--api_hash', type=str, help='Your API hash', default=os.getenv('TELEGRAM_API_HASH'))
parser.add_argument('--file', type=str, help='The ID of the channel for which you want to get the history', default="telegram_history-<channel_name>")
parser.add_argument('--limit', type=int, help='The maximum number of posts to retrieve', default=10000)
parser.add_argument('--offset_date', type=str, help='The date from which the history should be retrieved', default='1970-01-01')
parser.add_argument('-v', '--verbose', action='store_true', help='Print verbose output', default=False)

# Parse the arguments
args = parser.parse_args()

# Set up logging 
# If verbose is set, log level is INFO, otherwise log level is WARNING
log_level = logging.INFO if args.verbose else logging.WARNING

FORMAT = "%(message)s"
logging.basicConfig(
    level=log_level, 
    format=FORMAT, 
    datefmt="[%X]", 
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger('rich')

if isinstance(args.chat_name, list):
    args.chat_name = ' '.join(args.chat_name)

if args.verbose:
    log.info(f"Checking API connection for {args.chat_name}")
    log.info(f"API ID: {args.api_id}")
    log.info(f"API Hash: {args.api_hash}")


# Check if TELEGRAM_API_ID and TELEGRAM_API_HASH are supplied
if not args.api_id and not args.api_hash:
    # Check local variables
    if 'TELEGRAM_API_ID' in locals() and 'TELEGRAM_API_HASH' in locals():
        args.api_id = TELEGRAM_API_ID
        args.api_hash = TELEGRAM_API_HASH

    # Check environment variables
    elif 'TELEGRAM_API_ID' in os.environ and 'TELEGRAM_API_HASH' in os.environ:
        args.api_id = int(os.environ['TELEGRAM_API_ID'])
        args.api_hash = os.environ['TELEGRAM_API_HASH']

    # If TELEGRAM_API_ID and TELEGRAM_API_HASH are still not found, exit with an error message
    else:
        log.error("TELEGRAM_API_ID and TELEGRAM_API_HASH not found. Please provide them as arguments or set them as local variables or environment variables.\n")
        parser.print_help()
        exit(1)


# Use the arguments to create a TelegramClient
client = TelegramClient('anon', args.api_id, args.api_hash)

async def check_api_connection():
    async with client:
        try:
            # Check if the client succeeded in connecting to the API by getting info about the user
            user = await client.get_me()
        except Exception as e:
            log.error(f"Error: {e}\nFailed to connect to the API. Make sure that your API_ID and API_HASH are correct.")
            exit(1)

# Function to get the history of a channel (channel_id, limit, offset_date, offset_id, max_id, min_id)
async def get_channel_history(channel_id, 
                             limit=args.limit, 
                             offset_date=args.offset_date
                             ):
    async with client:
        # Convert the string to a datetime object
        from datetime import datetime
        offset_date = datetime.strptime(args.offset_date, '%Y-%m-%d')
        log.info(f"Fetching history from {offset_date}")

        # Use the TelegramClient to get the history of the channel
        history = await client.get_messages(
            channel_id, 
            limit=limit, 
            offset_date=offset_date,
            reverse = True
        )
    return history


async def list_all_chats():
    async with client:
        chats = await client.get_dialogs()
        return chats

async def find_chat_by_name(chat_name):
    chats = await list_all_chats()
    found_chats = []
    for chat in chats:
        if chat_name in chat.name:
            found_chats.append(chat)
    if len(found_chats) > 1:
        print("More than one chat found. Please choose the chat to retrieve:")
        for i, chat in enumerate(found_chats):
            last_message = await get_messages_by_chat_id(chat.id, limit=1)
            last_message_text = last_message[0].text[:20].replace('\n', ' ').strip() if last_message else "No messages"
            print(f"[bold]{i+1}. {chat.name}[/bold] - Last message: {last_message_text}", end='\n')
        choice = int(input("\nEnter the number of the chat: "))
        chat = found_chats[choice - 1]
    else:
        chat = found_chats[0]
    return chat

async def get_messages_by_chat_id(chat_id, limit=100):
    async with client:
        messages = await client.get_messages(chat_id, limit=limit)
        return messages
    

# async def transcribe_audio_message(message_id, chat_id):
#     async with client:
#         result = await client(functions.messages.TranscribeAudioRequest(
#             msg_id=message_id,
#             peer=chat_id
#         ))
#         inspect(result)
#     return result.stringify()


loop = asyncio.get_event_loop()

async def main():

    check_api_connection()

    # select correct chat
    chat = await find_chat_by_name(args.chat_name)
    log.info(f"Selected chat: {chat.name}, id: {chat.id}")

    # retrieve history
    history = await get_channel_history(chat.id)

    # order history by date
    history = sorted(history, key=lambda x: x.date)
    messages = []

    for message_number, message in enumerate(history[:args.limit]):
        # determine type of sender object
        if isinstance(message.sender, telethon.tl.types.User):
            sender_type = "user"
            if message.sender.first_name and message.sender.last_name:
                sender_name = str(message.sender.first_name) + " " + str(message.sender.last_name)
            elif message.sender.first_name and not message.sender.last_name:
                sender_name = str(message.sender.first_name)
            elif not message.sender.first_name and message.sender.last_name:
                sender_name = str(message.sender.last_name)
            else:
                continue
        elif isinstance(message.sender, telethon.tl.types.Channel):
            sender_type = "channel"
            sender_name = str(message.sender.title)

        # check if message is voice message
        if message.voice:
            message_type = "voice"
        else:
            message_type = "text"

        message_date = message.date.strftime('%Y-%m-%d %H:%M:%S')

        formatted_message = {
            "message_id": message.id,
            "chat_name": chat.name,
            "date": message_date,
            "chat_id": message.chat_id,
            "message_type": message_type,
            "sender_type": sender_type,
            "sender_name": sender_name,
            "sender_username": message.sender.username,
            "sender_id": message.sender_id,
            "message": str(message.message),
            "views": message.views,
            "reply_to_msg_id": message.reply_to_msg_id,
        }

        # try format message as json
        try:
            json_message = json.dumps(formatted_message, indent=4)
            # add message to messages dictionary
            messages.append(formatted_message)
        except Exception as e:
            log.warning(f"Warning: {e}\nFailed to format message as JSON. Excluding message.")
            inspect(formatted_message)
            continue

    log.info(f"Finished fetching {len(messages)} messages.")

    # convert dict to json
    json_messages = json.dumps(messages, indent=4)

    log.info(f"Saving messages to {args.file}")
    try:
        with open(args.file, 'w') as f:
            f.write(json_messages)
    except Exception as e:
        log.error(f"Error: {e}\nFailed to save messages to file.")
        exit(1) 

loop.run_until_complete(main())