import os
import sys
import httpx
import logging
from bot_func import Bot

PATH = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.dirname(PATH))

PERMISSION = 5

HELP = """\
Get a random post from subreddit.
Usage: reddit <name of subreddit> [hot/new/random/rising/top/controversial]
"""

REDDIT_BASEURL = "https://www.reddit.com"
REDDIT_SUBREDDIT_URL = REDDIT_BASEURL + "/r/{subreddit}/{sort}/.json"


async def main(message, **kwargs):
    cmd = message.content.split()[1:]
    if len(cmd) < 1:
        raise ValueError("You have to specify the subreddit to search.")
    elif len(cmd) > 2:
        raise ValueError("Too many arguments")
    elif len(cmd) == 2 and not cmd[1] in ["hot", "new", "random", "rising", "top", "controversial"]:
        raise ValueError("Wrong sort type")

    subreddit = cmd[0]
    if len(cmd) == 1:
        sort = "random"
    else:
        sort = cmd[1]
    async with httpx.AsyncClient() as client:
        r = await client.get(
            REDDIT_SUBREDDIT_URL.format(subreddit=subreddit, sort=sort),
            headers={"User-Agent": "Kyoko_Kirigiri_Bot"}
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
                    embed.set_image(url=post_data['preview']['images'][0]['source']['url'])
                else:
                    embed.set_image(url=post_data['url'])
            yield embed
            return
    except:
        if data['data']['dist'] == 0:
            raise RuntimeError("That subreddit does not exist.")
        logging.info(data)
        raise RuntimeError("Unknown Error occured!")
