import pandas as pd
import curl_cffi
from lxml import etree
import logging

logger = logging.getLogger(__name__)


def get_dom(arg_link):
    """Get DOM from URL with retry logic"""
    for attempt in range(5):
        try:
            response = curl_cffi.get(
                arg_link, 
                timeout=60, 
                impersonate='chrome',
                # Note: Remove proxy for production or use environment variable
                # proxy="http://ocapgizs-US-rotate:araohu409l9t@p.webshare.io:80"
            )
            if response.status_code == 200:
                dom = etree.fromstring(response.content, parser=etree.HTMLParser())
                return dom
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {arg_link}: {e}")
            if attempt == 4:  # Last attempt
                logger.error(f"Failed to fetch {arg_link} after 5 attempts")
    return None


def get_from_xpath(arg_dom, arg_xpath):
    """Extract single text from DOM using xpath"""
    try:
        result = arg_dom.xpath(arg_xpath)
        return result[0].strip() if result else ""
    except:
        return ""


def get_all_results(arg_dom, arg_xpath):
    """Extract all text results from DOM using xpath"""
    try:
        result = arg_dom.xpath(arg_xpath)
        return [x.strip() for x in result if len(x.strip())]
    except:
        return []


# Technology News Scrapers
def scrape_tech_techcrunch():
    """Scrape technology news from TechCrunch"""
    dom = get_dom("https://techcrunch.com/latest/?offset=30")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'loop-card--post-type-post')]"):
        row_data = {
            "title": get_from_xpath(each_res, ".//h3/a//text()"),
            "link": get_from_xpath(each_res, ".//h3/a/@href"),
            "image": get_from_xpath(each_res, ".//figure/img/@src"),
            "source": "TechCrunch",
            "category": "technology"
        }
        if row_data["title"]:
            data.append(row_data)
    return data


def scrape_tech_theverge():
    """Scrape technology news from The Verge"""
    dom = get_dom("https://www.theverge.com/tech")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'hp1qhq3')]//div[contains(@class,'duet--content-cards--content-card _1u')]"):
        image_url = get_from_xpath(each_res, ".//img/@srcset")
        if image_url:
            image_url = image_url.split(',  https://platform.theverge.com')[-1].split('?')[0]
        
        row_data = {
            "title": get_from_xpath(each_res, ".//a/text()"),
            "link": "https://www.theverge.com" + get_from_xpath(each_res, ".//a[contains(@class,'_1lkmsmo0')]/@href"),
            "image": image_url,
            "source": "The Verge",
            "category": "technology"
        }
        if row_data["title"]:
            data.append(row_data)
    return data


# Economy News Scrapers
def scrape_economy_indianexpress():
    """Scrape economy news from Indian Express"""
    dom = get_dom("https://indianexpress.com/section/business/economy/")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'articles ')]"):
        image_url = get_from_xpath(each_res, ".//img/@data-src")
        if image_url:
            image_url = image_url.split('?')[0]
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h2/a/text()"),
            "link": get_from_xpath(each_res, ".//h2/a/@href"),
            "image": image_url,
            "source": "Indian Express",
            "category": "economy"
        }
        if row_data["title"]:
            data.append(row_data)
    return data


def scrape_economy_economictimes():
    """Scrape economy news from Economic Times"""
    dom = get_dom("https://economictimes.indiatimes.com/markets/stocks/news")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'eachStory')]"):
        image_url = get_from_xpath(each_res, ".//img/@src")
        if image_url:
            image_url = image_url.split('?')[0].replace(',width-160,height-120,', ',width-640,height-480,')
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h3/a/text()"),
            "link": "https://economictimes.indiatimes.com" + get_from_xpath(each_res, ".//h3/a/@href"),
            "image": image_url,
            "source": "Economic Times",
            "category": "economy"
        }
        if row_data["title"]:
            data.append(row_data)
    return data


# Sports News Scrapers
def scrape_sports_indianexpress():
    """Scrape sports news from Indian Express"""
    dom = get_dom("https://indianexpress.com/article/sports/")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'articles ')]"):
        image_url = get_from_xpath(each_res, ".//img/@src")
        if image_url:
            image_url = image_url.split('?')[0]
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h2/a/text()"),
            "link": get_from_xpath(each_res, ".//h2/a/@href"),
            "image": image_url,
            "source": "Indian Express",
            "category": "sports"
        }
        if row_data["title"]:
            data.append(row_data)
    return data


def scrape_sports_hindustantimes():
    """Scrape sports news from Hindustan Times"""
    dom = get_dom("https://www.hindustantimes.com/sports")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@data-vars-storytype,'story') and contains(@class,'listView')]"):
        image_url = get_from_xpath(each_res, ".//img/@data-src")
        if image_url:
            image_url = image_url.split('?')[0].replace('/148x111/', '/550x309/')
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h2/a/text()"),
            "link": get_from_xpath(each_res, ".//h2/a/@href"),
            "image": image_url,
            "source": "Hindustan Times",
            "category": "sports"
        }
        if row_data["title"]:
            data.append(row_data)
    return data


# Politics News Scrapers
def scrape_politics_economictimes():
    """Scrape politics news from Economic Times"""
    dom = get_dom("https://economictimes.indiatimes.com/news/politics")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'botplData flt')]"):
        image_url = get_from_xpath(each_res, ".//img/@data-original")
        if image_url:
            image_url = image_url.split('?')[0].replace(',width-160,height-120', ',width-640,height-480')
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h3/a/text()"),
            "link": "https://economictimes.indiatimes.com" + get_from_xpath(each_res, ".//h3/a/@href"),
            "image": image_url,
            "source": "Economic Times",
            "category": "politics"
        }
        if row_data["title"]:
            data.append(row_data)
    return data


def scrape_politics_nytimes():
    """Scrape politics news from NY Times"""
    dom = get_dom("https://www.nytimes.com/section/politics")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//li[contains(@class,'css-18yolpw')]"):
        image_url = get_from_xpath(each_res, ".//img/@src")
        if image_url:
            image_url = image_url.split(', ')[-1].split('?')[0].replace('-square320', '-square640')
        
        row_data = {
            "title": get_from_xpath(each_res, ".//a/h3/text()"),
            "link": "https://www.nytimes.com" + get_from_xpath(each_res, ".//a[h3]/@href"),
            "image": image_url,
            "source": "New York Times",
            "category": "politics"
        }
        if row_data["title"]:
            data.append(row_data)
    return data


# Lifestyle News Scrapers
def scrape_lifestyle_indianexpress():
    """Scrape lifestyle news from Indian Express"""
    dom = get_dom("https://indianexpress.com/article/lifestyle/")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'articles ')]"):
        image_url = get_from_xpath(each_res, ".//img/@data-src")
        if image_url:
            image_url = image_url.split('?')[0]
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h2/a/text()"),
            "link": get_from_xpath(each_res, ".//h2/a/@href"),
            "image": image_url,
            "source": "Indian Express",
            "category": "lifestyle"
        }
        if row_data["title"]:
            data.append(row_data)
    return data


def scrape_lifestyle_foxnews():
    """Scrape lifestyle news from Fox News"""
    dom = get_dom("https://www.foxnews.com/health")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//article[contains(@class,'article')]"):
        image_url = get_from_xpath(each_res, ".//img/@src")
        if image_url:
            image_url = image_url.split('?')[0].replace('/348/196/', '/720/405/')
        
        link = "https://www.foxnews.com" + get_from_xpath(each_res, ".//h4/a/@href")
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h4/a/text()"),
            "link": link,
            "image": image_url,
            "source": "Fox News",
            "category": "lifestyle"
        }
        
        if row_data["title"] and "/health/" in link:
            data.append(row_data)
    return data


# Entertainment News Scrapers
def scrape_entertainment_indianexpress():
    """Scrape entertainment news from Indian Express"""
    dom = get_dom("https://indianexpress.com/section/entertainment/")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//article[contains(@class,'myie-articles')]"):
        image_url = get_from_xpath(each_res, ".//img/@data-src")
        if image_url:
            image_url = image_url.split('?')[0]
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h2/a/text()"),
            "link": get_from_xpath(each_res, ".//h2/a/@href"),
            "image": image_url,
            "source": "Indian Express",
            "category": "entertainment"
        }
        if row_data["title"]:
            data.append(row_data)
    return data


def scrape_entertainment_variety():
    """Scrape entertainment news from Variety"""
    dom = get_dom("https://variety.com/v/film/")
    if not dom:
        return []
    
    data = []
    for each_res in dom.xpath("//li/article"):
        image_url = get_from_xpath(each_res, ".//img/@src")
        if image_url:
            image_url = image_url.split('?')[0]
        
        link = get_from_xpath(each_res, ".//h3/a/@href")
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h3/a/text()"),
            "link": link,
            "image": image_url,
            "source": "Variety",
            "category": "entertainment"
        }
        
        if row_data["title"] and "variety.com" in link:
            data.append(row_data)
    return data


def scrape_all_news():
    """Main function to scrape all news from all sources"""
    scraped_data = []
    
    scrapers = [
        scrape_tech_techcrunch,
        scrape_tech_theverge,
        scrape_economy_indianexpress,
        scrape_economy_economictimes,
        scrape_sports_indianexpress,
        scrape_sports_hindustantimes,
        scrape_politics_economictimes,
        scrape_politics_nytimes,
        scrape_lifestyle_indianexpress,
        scrape_lifestyle_foxnews,
        scrape_entertainment_indianexpress,
        scrape_entertainment_variety,
    ]
    
    for scraper in scrapers:
        try:
            data = scraper()
            scraped_data.extend(data)
            logger.info(f"Successfully scraped {len(data)} articles from {scraper.__name__}")
        except Exception as e:
            logger.error(f"Error in {scraper.__name__}: {e}")
    
    return scraped_data


def save_to_csv(data, filename="scraped_data.csv"):
    """Save scraped data to CSV file"""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(data)} articles to {filename}")
        return True
    return False


if __name__ == "__main__":
    # For standalone testing
    logging.basicConfig(level=logging.INFO)
    scraped_data = scrape_all_news()
    save_to_csv(scraped_data)