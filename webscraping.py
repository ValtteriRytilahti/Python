import requests
from bs4 import BeautifulSoup


# Get todays and tomorrows electricity prices
def electricity():
    page = requests.get("https://www.herrfors.fi/fi/spot-hinnat/")
    soup = BeautifulSoup(page.content, "html.parser")
    
    prices_today = [float(price.text.replace("\n", "").replace(" ", "")) for price in soup.findAll(class_="today s-price")]
    prices_tomorrow = [float(price.text.replace("\n", "").replace(" ", "")) for price in soup.findAll(class_="tomorrow s-price")]
    
    output = "Time     | Today's Price | Tomorrow's Price\n"
    output += "-----------------------------------------\n"
    for i in range(len(prices_today)):
        hour = f"{i:02d}-{(i+1)%24:02d}"
        output += f"{hour}    | {prices_today[i]}          | {prices_tomorrow[i]}\n"
        
    return output

# fetch n most recent news from mtv
def news(n):
    base = "https://www.mtvuutiset.fi/uusimmat/uutiset"
    page = requests.get(base)
    soup = BeautifulSoup(page.content, "html.parser")
    #find div with class latest-listing-time-first
    
    target_div = soup.find(class_="latest-listing-time-first")
    news_table = target_div.find("ul")
    news_list = news_table.findAll("li")
    
    output = ""
    
    for i in range(n):
        data = news_list[i]
        # get time
        time = data.find(class_="time").text.strip()

        # get news title (p tag)
        tittle = data.find("p")
        # get link
        link =  base + data.find("a")["href"]
        
        output += f"{time} {tittle.text.strip()}\n{link}\n\n"
    
    return output


def weather(city: str):
    
    url = f"https://www.foreca.fi/Finland/{city}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    
    target = soup.find(id="obs_3d")    
    
    # get current temperature
    current_temp = target.find(class_="temp").text.strip()
    return current_temp