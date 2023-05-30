from bs4 import BeautifulSoup
import aiohttp
from notion_client import AsyncClient
import asyncio
import url_parser
from discord.ext import commands
from os import environ

class WebCrawler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = asyncio.get_event_loop()
        self.notion_token = environ.get("NOTION_TOKEN")
        self.notion_db_url = environ.get("DB_ID")
        self.client = AsyncClient(auth=self.notion_token)

        self.crawled = []
        self.sites = asyncio.Queue()
        
        self.bg_task = self.bot.loop.create_task(self.scheduled_task())

    async def scheduled_task(self):

        await self.bot.wait_until_ready()
        links = await self.get_links_from_notion()

        self.initial = "https://news.ycombinator.com/"
        self.crawled = links
        print(self.crawled)
        words = [
            "figma",
            "gpt",
            "pricing",
            "free trial",
            "discord",
            "supercharge",
            "productivity",
        ]

        await self.sites.put(self.initial)
        await self.crawl_website(words)

    async def crawl_website(self, words):
        print("Running scheduled web crawling task...")
        while True:
            url = await self.sites.get()
            async with aiohttp.ClientSession() as session:
                try:
                    if url not in self.crawled:
                        async with session.get(url) as response:
                            self.crawled.append(url)
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, "html.parser")
                                for word in words:
                                    if word in soup.get_text().lower() and url != self.initial:
                                        print(
                                            f"Found the word '{word}' on {url} and saved to Notion database."
                                        )

                                        desc = "Not Found"
                                        meta = soup.find("meta", {"name": "description"}, content=True)
                                        if meta:
                                            desc = meta["content"] #type: ignore

                                        await self.save_to_notion(
                                            url, word, soup.title.string, desc
                                        )
                                        break

                                # Find all links on the webpage and crawl them recursively
                                links = [
                                    a["href"] for a in soup.find_all("a", href=True)
                                ]
                                for link in links:
                                    if link:
                                        try:
                                            parsed = url_parser.parse_url(link)
                                            link = f"{parsed['domain']}.{parsed['top_domain']}"
                                            if not link.endswith("edu"):
                                                insert = f"https://{link}"
                                                await self.sites.put(insert)
                                        except:
                                            pass

                except Exception as e:
                    print(type(e))
                    print(f"An error occurred while crawling {url}: {e}")

    async def get_links_from_notion(self):
        notion_db = await self.client.databases.query(self.notion_db_url)

        links = []
        for link in notion_db["results"]:
            url = link["properties"]["URL"]["url"]
            if url and url.startswith("http"):
                links.append(url)

        return links

    async def save_to_notion(self, url, word, title, desc):
        await self.client.pages.create(
            parent={"database_id": self.notion_db_url},
            properties={
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": title,
                            },
                        },
                    ],
                },
                "URL": {"url": url},
                "Category": {
                    "rich_text": [
                        {
                            "text": {
                                "content": word.title(),
                            },
                        },
                    ],
                },
                "Description": {
                     "rich_text": [
                        {
                            "text": {
                                "content": desc.title(),
                            },
                        },
                    ],
                }
            },
        )

def setup(bot):
    bot.add_cog(WebCrawler(bot))