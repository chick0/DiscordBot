import os
import sys
import httpx
import logging

from bot_func import Bot

PATH = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.dirname(PATH))

PERMISSION = 5

HELP = """\
Get a random post from shrimping.
Usage: shrimp
"""

REDDIT_BASEURL = "https://www.reddit.com"
REDDIT_SUBREDDIT_URL = REDDIT_BASEURL + "/r/{subreddit}/{sort}/.json"


async def main(message, **kwargs):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            REDDIT_SUBREDDIT_URL.format(
                subreddit="shrimping",
                sort="random"
            ),
            headers={
                "User-Agent": "Kyoko_Kirigiri_Bot"
            }
        )

    r.raise_for_status()
    data = r.json()
    try:
        try:
            post_data_s = data[0]["data"]["children"]
        except KeyError:
            post_data_s = data["data"]["children"]

        for post_data in [x['data'] for x in post_data_s]:
            if post_data['stickied']:
                continue

            post_url = REDDIT_BASEURL + post_data['permalink']
            post_title = post_data['title']
            embed = await Bot.get_embed(
                title=post_title,
                desc=post_data['selftext'],
                sender=message.author,
                url=post_url
            )

            if not post_data['is_self']:
                if post_data['is_video']:
                    embed.set_image(
                        url=post_data['preview']['images'][0]['source']['url']
                    )
                else:
                    embed.set_image(
                        url=post_data['url']
                    )
            yield embed
            return
    except:
        logging.info(data)
        raise RuntimeError("Unknown Error occurred!")
