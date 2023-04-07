from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

def getImg():
    url = "https://modao-zushi.fandom.com/wiki/Animation/Gallery"
    img_urls = []
    response = requests.get(url=url)
    soup = BeautifulSoup(response.content, "lxml")
    imgs = soup.find_all("img", {"class" : "thumbimage"})
    for img in imgs:
        imgUrl = img["src"]
        if imgUrl.startswith("https"): 
            print(imgUrl)
            url_without_scale = imgUrl.split("/scale-to-width-down/")[0]
            new_url = url_without_scale + "?cb=" + imgUrl.split("?cb=")[1]
            print(new_url)
            img_urls.append(new_url)
    
    return img_urls