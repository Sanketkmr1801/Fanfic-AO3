from ao3 import search
import requests
import pickle
import discord
import os
from dotenv import load_dotenv
from img import getImg

load_dotenv(dotenv_path="token.env")
token = os.getenv("DISCORD_BOT_TOKEN")

temp_tags = []
current_tags = []
test_tags = ["Angst", "Happy Ending"]
cur_page_no = 1
img_urls = getImg()
# save the array to a file
def seed_tags(tags):
    save_tags(tags)

def save_tags(tags):
    with open('tags.pkl', 'wb') as f:
        pickle.dump(tags, f)
def save_img_count(img_count):
    with open("img_count.pkl", 'wb') as f:
        pickle.dump(img_count, f)
# seed_tags(test_tags)
# load the array from the file
def load_tags():
    with open('tags.pkl', 'rb') as f:
        loaded_array = pickle.load(f)
        return loaded_array

def load_img_count():
    try:
        with open('img_count.pickle', 'rb') as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return 0
    
current_tags = load_tags()
print(current_tags)
#Get Works
async def get_works(message, pageNo):
    base_url = "https://archiveofourown.org"
    global img_urls 
    img_count
    query_tags = ",".join(current_tags)
    soup, url = search(language="en", page=pageNo, tags=query_tags, tag_id="Lán Zhàn | Lán Wàngjī*s*Wèi Yīng | Wèi Wúxiàn")
    works = soup.find_all('li', {'class': 'work'})
    total_length = 0
    count = 0
    img_count = load_img_count()
    await message.channel.send(f"```{url}```")
    for work in works:
        msg_tag = ""
        count += 1
        work_detail = work.find("h4").find_all("a")
        work_url = base_url + work_detail[0]["href"]
        author_url = base_url + work_detail[1]["href"]
        summary = work.find("blockquote", {"class": "userstuff summary"})
        required_tags = work.find_all("span", {"class": "text"})
        required_tags_txt = ""
        for rtag in required_tags:
            required_tags_txt += rtag.get_text().strip() + "\t\t\t\t|\t\t\t\t"
        if(summary == None): continue
        summary = summary.get_text().strip()
        tags = work.find_all("a", {'class': "tag"})

        if(len(work_detail) < 2): continue
        name = work_detail[0].get_text()
        author = work_detail[1].get_text()
        print(name, "by", author)
        for tag in tags:
            tag = tag.get_text()
            # if(len(tag) > 20): continue
            print(tag, end=" | ")
            msg_tag += tag + " | "
        
        print(summary)
        print("\n\n\n")
        print("VALUE OF COUNT IS ", count)
        if(count >= 1):
            count = 0
            embed = discord.Embed(title=f"{name}", url=work_url, color=0xcfc0d4, description=required_tags_txt + "\n\n" + msg_tag)
            embed.set_author(name=f"by {author}", url = author_url)
            embed.set_image(url=img_urls[img_count % len(img_urls)])
            img_count += 1
            await message.channel.send(embed=embed)
            await message.channel.send(f"```{summary}``` ``` ```")
            msg = "```"

    save_img_count(img_count)
    await message.channel.send(f"```You were on page number {pageNo}```")

#Get AutoComplete Tags
def get_tags(term):
    tag_arr = []
    print(term)
    url = "https://archiveofourown.org/autocomplete/tag"
    params = {
        "term": term
    }
    res = requests.get(url=url, params=params)
    tags = res.json()
    for tag in tags:
        tag_arr.append(tag["id"])
        # print(tag["id"], end=",")

    return tag_arr

def tag_msg(tags):
    msg = "```"
    for i in range(len(tags)):
        msg += f"{i + 1}. {tags[i]}\n"
    msg += "```"
    return msg

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global temp_tags
    global cur_page_no
    global current_tags

    if message.author == client.user: return

    if (message.content[0] == "!"):

        command = message.content.split(" ")[0]
        args = message.content.split(" ")[1:]
        print(command, args)
        
        if(command == "!t" and len(args) == 0):
            await message.channel.send(tag_msg(current_tags))
            print(temp_tags)

        if(command == "!t" and len(args) != 0):
            term_tags = get_tags(" ".join(args))
            await message.channel.send(tag_msg(term_tags))
            temp_tags = term_tags
            print(temp_tags)

        if(command == "!ta" and len(args) != 0):
            for tag_idx in args:
                tag_idx = int(tag_idx) - 1
                if((tag_idx >= len(temp_tags)) or tag_idx < 0): continue
                if(temp_tags[tag_idx] in current_tags): continue
                current_tags.append(temp_tags[tag_idx])
                
            save_tags(current_tags)
            await message.channel.send(tag_msg(current_tags))

        if(command == "!tr" and len(args) != 0):
            for i in range(len(args)):
                args[i] = int(args[i])
            args.sort(reverse = True)
            for tag_idx in args:
                tag_idx = int(tag_idx) - 1
                if((tag_idx >= len(current_tags)) or tag_idx < 0): continue
                current_tags.pop(tag_idx)

            save_tags(current_tags)
            await message.channel.send(tag_msg(current_tags))

        if(command == "!w"):
            pageNo = cur_page_no
            if(len(args) != 0):
                pageNo = args[0]
                cur_page_no = int(pageNo)
            await get_works(message, pageNo)
            cur_page_no += 1


client.run(token=token)
