import pandas as pd
from curl_cffi import requests
from lxml import etree
import logging
from tqdm import tqdm
import time
from datetime import datetime
import re
from dateutil import parser

# Configure colorful logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """Print an attractive banner for the news scraper"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    🤖 AI NEWS SCRAPER 🤖                    ║")
    print("║              Intelligent News Aggregation System            ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    print(f"{Colors.OKCYAN}🌐 Scraping from 12 premium news sources across 6 categories{Colors.ENDC}")
    print(f"{Colors.OKGREEN}📊 Real-time progress tracking with beautiful visualizations{Colors.ENDC}")
    print(f"{Colors.WARNING}⚡ Powered by AI and modern web scraping technology{Colors.ENDC}\n")

def log_scraper_start(source_name, category, url):
    """Log the start of scraping from a source"""
    print(f"{Colors.OKBLUE}🔍 Scraping {Colors.BOLD}{source_name}{Colors.ENDC}{Colors.OKBLUE} | {category.title()} News{Colors.ENDC}")
    logger.info(f"Starting scrape: {source_name} ({category})")

def log_scraper_result(source_name, article_count, success=True):
    """Log the result of scraping"""
    if success and article_count > 0:
        print(f"{Colors.OKGREEN}✅ {source_name}: {article_count} articles found{Colors.ENDC}")
        logger.info(f"Success: {source_name} - {article_count} articles")
    elif success and article_count == 0:
        print(f"{Colors.WARNING}⚠️  {source_name}: No articles found{Colors.ENDC}")
        logger.warning(f"No articles: {source_name}")
    else:
        print(f"{Colors.FAIL}❌ {source_name}: Scraping failed{Colors.ENDC}")
        logger.error(f"Failed: {source_name}")

def log_final_summary(total_articles, categories_stats, sources_stats):
    """Log the final scraping summary"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    📊 SCRAPING SUMMARY 📊                   ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 Total Articles Scraped: {total_articles}{Colors.ENDC}\n")
    
    print(f"{Colors.OKCYAN}{Colors.BOLD}📂 By Category:{Colors.ENDC}")
    for category, count in categories_stats.items():
        print(f"   📰 {category.title()}: {Colors.OKGREEN}{count}{Colors.ENDC} articles")
    
    print(f"\n{Colors.OKCYAN}{Colors.BOLD}🌐 By Source:{Colors.ENDC}")
    for source, count in sources_stats.items():
        print(f"   🏢 {source}: {Colors.OKGREEN}{count}{Colors.ENDC} articles")
    
    print(f"\n{Colors.WARNING}💾 Data saved to CSV file for analysis{Colors.ENDC}")
    print(f"{Colors.OKBLUE}🌟 Articles ready for AI processing and insights{Colors.ENDC}\n")


def get_dom(arg_link):
    """Get DOM from URL with retry logic"""
    for attempt in range(5):
        try:
            response = requests.get(
                arg_link, 
                timeout=60, 
                impersonate='chrome',
                # Note: Remove proxy for production or use environment variable
                proxy="http://ocapgizs-US-rotate:araohu409l9t@p.webshare.io:80"
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


def format_datetime(datetime_str):
    """Format datetime string to unified format: '6 Oct 2025, 16:42'"""
    if not datetime_str or not datetime_str.strip():
        return ""
    
    try:
        # Parse the datetime string
        dt = parser.parse(datetime_str, fuzzy = True)
        # Format to desired format: "6 Oct 2025, 16:42"
        return dt.strftime("%-d %b %Y, %H:%M")
    except:
        # If parsing fails, try to clean and return original
        return datetime_str.strip()


# Technology News Scrapers
def scrape_tech_techcrunch():
    """Scrape technology news from TechCrunch"""
    source_name = "TechCrunch"
    category = "technology"
    url = "https://techcrunch.com/latest/?offset=30"
    
    log_scraper_start(source_name, category, url)
    
    dom = get_dom(url)
    if dom is None:
        log_scraper_result(source_name, 0, False)
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'loop-card--post-type-post')]"):
        datetime_str = get_from_xpath(each_res, ".//time[@class='loop-card__meta-item loop-card__time wp-block-tc23-post-time-ago']/@datetime") or ""
        datetime_str = format_datetime(datetime_str)
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h3/a//text()"),
            "link": get_from_xpath(each_res, ".//h3/a/@href"),
            "image": get_from_xpath(each_res, ".//figure/img/@src"),
            "source": source_name,
            "category": category,
            "datetime": datetime_str
        }
        if row_data["title"]:
            data.append(row_data)
    
    log_scraper_result(source_name, len(data), True)
    return data


def scrape_tech_theverge():
    """Scrape technology news from The Verge"""
    dom = get_dom("https://www.theverge.com/tech")
    if dom is None:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'hp1qhq3')]//div[contains(@class,'duet--content-cards--content-card _1u')]"):
        datetime_str = get_from_xpath(each_res, ".//time/@datetime") or ""
        datetime_str = format_datetime(datetime_str)
        
        image_url = get_from_xpath(each_res, ".//img/@srcset")
        if image_url:
            image_url = image_url.split(',  https://platform.theverge.com')[-1].split('?')[0]
        
        row_data = {
            "title": get_from_xpath(each_res, ".//a/text()"),
            "link": "https://www.theverge.com" + get_from_xpath(each_res, ".//a[contains(@class,'_1lkmsmo0')]/@href"),
            "image": image_url,
            "source": "The Verge",
            "category": "technology",
            "datetime": datetime_str
        }
        if row_data["title"]:
            data.append(row_data)
    return data


# Economy News Scrapers
def scrape_economy_indianexpress():
    """Scrape economy news from Indian Express"""
    dom = get_dom("https://indianexpress.com/section/business/economy/")
    if dom is None:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'articles ')]"):
        datetime_str = get_from_xpath(each_res, ".//div[@class='date']/text()") or ""
        datetime_str = format_datetime(datetime_str)
        
        image_url = get_from_xpath(each_res, ".//img/@data-src")
        if image_url:
            image_url = image_url.split('?')[0]
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h2/a/text()"),
            "link": get_from_xpath(each_res, ".//h2/a/@href"),
            "image": image_url,
            "source": "Indian Express",
            "category": "economy",
            "datetime": datetime_str
        }
        if row_data["title"]:
            data.append(row_data)
    return data


def scrape_economy_economictimes():
    """Scrape economy news from Economic Times"""
    dom = get_dom("https://economictimes.indiatimes.com/markets/stocks/news")
    if dom is None:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'eachStory')]"):
        datetime_str = get_from_xpath(each_res, ".//time[@class='date-format']/@data-time") or get_from_xpath(each_res, ".//time[@class='date-format']/text()") or ""
        datetime_str = format_datetime(datetime_str)
        
        image_url = get_from_xpath(each_res, ".//img/@src")
        if image_url:
            image_url = image_url.split('?')[0].replace(',width-160,height-120,', ',width-640,height-480,')
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h3/a/text()"),
            "link": "https://economictimes.indiatimes.com" + get_from_xpath(each_res, ".//h3/a/@href"),
            "image": image_url,
            "source": "Economic Times",
            "category": "economy",
            "datetime": datetime_str
        }
        if row_data["title"]:
            data.append(row_data)
    return data


# Sports News Scrapers
def scrape_sports_indianexpress():
    """Scrape sports news from Indian Express"""
    dom = get_dom("https://indianexpress.com/article/sports/")
    if dom is None:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'articles ')]"):
        datetime_str = get_from_xpath(each_res, ".//div[@class='date']/text()") or ""
        datetime_str = format_datetime(datetime_str)
        
        image_url = get_from_xpath(each_res, ".//img/@src")
        if image_url:
            image_url = image_url.split('?')[0]
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h2/a/text()"),
            "link": get_from_xpath(each_res, ".//h2/a/@href"),
            "image": image_url,
            "source": "Indian Express",
            "category": "sports",
            "datetime": datetime_str
        }
        if row_data["title"]:
            data.append(row_data)
    return data


def scrape_sports_hindustantimes():
    """Scrape sports news from Hindustan Times"""
    dom = get_dom("https://www.hindustantimes.com/sports")
    if dom is None:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@data-vars-storytype,'story') and contains(@class,'listView')]"):
        datetime_str = get_from_xpath(each_res, ".//div[@class='dateTime secTime ftldateTime']/text()") or get_from_xpath(each_res, "@data-vars-story-time") or ""
        datetime_str = format_datetime(datetime_str)
        
        image_url = get_from_xpath(each_res, ".//img/@data-src")
        if image_url:
            image_url = image_url.split('?')[0].replace('/148x111/', '/550x309/')
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h2/a/text()"),
            "link": get_from_xpath(each_res, ".//h2/a/@href"),
            "image": image_url,
            "source": "Hindustan Times",
            "category": "sports",
            "datetime": datetime_str
        }
        if row_data["title"]:
            data.append(row_data)
    return data


# Politics News Scrapers
def scrape_politics_economictimes():
    """Scrape politics news from Economic Times"""
    dom = get_dom("https://economictimes.indiatimes.com/news/politics")
    if dom is None:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'botplData flt')]"):
        datetime_str = get_from_xpath(each_res, ".//time[@class='date-format']/@data-time") or get_from_xpath(each_res, ".//time[@class='date-format']/text()") or ""
        datetime_str = format_datetime(datetime_str)
        
        image_url = get_from_xpath(each_res, ".//img/@data-original")
        if image_url:
            image_url = image_url.split('?')[0].replace(',width-160,height-120', ',width-640,height-480')
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h3/a/text()"),
            "link": "https://economictimes.indiatimes.com" + get_from_xpath(each_res, ".//h3/a/@href"),
            "image": image_url,
            "source": "Economic Times",
            "category": "politics",
            "datetime": datetime_str
        }
        if row_data["title"]:
            data.append(row_data)
    return data


def scrape_politics_nytimes():
    """Scrape politics news from NY Times"""
    dom = get_dom("https://www.nytimes.com/section/politics")
    if dom is None:
        return []
    
    data = []
    for each_res in dom.xpath("//li[contains(@class,'css-18yolpw')]"):
        
        datetime_str = "-".join(get_from_xpath(each_res, ".//a[h3]/@href").replace("/interactive", "").split('/')[1:4]) or ""
        datetime_str = format_datetime(datetime_str)
        
        image_url = get_from_xpath(each_res, ".//img/@src")
        if image_url:
            image_url = image_url.split(', ')[-1].split('?')[0].replace('-square320', '-square640')
        row_data = {
            "title": get_from_xpath(each_res, ".//a/h3/text()"),
            "link": "https://www.nytimes.com" + get_from_xpath(each_res, ".//a[h3]/@href"),
            "image": image_url,
            "source": "New York Times",
            "category": "politics",
            "datetime": datetime_str
        }
        if row_data["title"]:
            data.append(row_data)
    return data


# Lifestyle News Scrapers
def scrape_lifestyle_indianexpress():
    """Scrape lifestyle news from Indian Express"""
    dom = get_dom("https://indianexpress.com/article/lifestyle/")
    if dom is None:
        return []
    
    data = []
    for each_res in dom.xpath("//div[contains(@class,'articles ')]"):
        datetime_str = get_from_xpath(each_res, ".//div[@class='date']/text()") or ""
        datetime_str = format_datetime(datetime_str)
        
        image_url = get_from_xpath(each_res, ".//img/@data-src")
        if image_url:
            image_url = image_url.split('?')[0]
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h2/a/text()"),
            "link": get_from_xpath(each_res, ".//h2/a/@href"),
            "image": image_url,
            "source": "Indian Express",
            "category": "lifestyle",
            "datetime": datetime_str
        }
        if row_data["title"]:
            data.append(row_data)
    return data


def scrape_lifestyle_foxnews():
    """Scrape lifestyle news from Fox News"""
    dom = get_dom("https://www.foxnews.com/health")
    if dom is None:
        return []
    
    data = []
    for each_res in dom.xpath("//article[contains(@class,'article')]"):
        datetime_str = get_all_results(each_res, ".//span[contains(@class,'time')]//text()") or ""
        image_url = get_from_xpath(each_res, ".//img/@src")
        if image_url:
            image_url = image_url.split('?')[0].replace('/348/196/', '/720/405/')
        
        link = "https://www.foxnews.com" + get_from_xpath(each_res, ".//h4/a/@href")
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h4/a/text()"),
            "link": link,
            "image": image_url,
            "source": "Fox News",
            "category": "lifestyle",
            "datetime": datetime_str
        }
        
        if row_data["title"] and "/health/" in link:
            data.append(row_data)
    df = pd.DataFrame(data)
    df.drop_duplicates('link', ignore_index = True, inplace = True)
    df = df[df["datetime"].apply(lambda x : len(x) != 0)]
    df['datetime'] = df['datetime'].apply(lambda x : format_datetime(x[0]))
    return df.to_dict('records')


# Entertainment News Scrapers
def scrape_entertainment_indianexpress():
    """Scrape entertainment news from Indian Express"""
    dom = get_dom("https://indianexpress.com/section/entertainment/")
    if dom is None:
        return []
    
    data = []
    for each_res in dom.xpath("//article[contains(@class,'myie-articles')]"):
        datetime_str = get_from_xpath(each_res, ".//div[@class='my-time']/text()") or ""
        datetime_str = format_datetime(datetime_str)
        
        image_url = get_from_xpath(each_res, ".//img/@data-src")
        if image_url:
            image_url = image_url.split('?')[0]
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h2/a/text()"),
            "link": get_from_xpath(each_res, ".//h2/a/@href"),
            "image": image_url,
            "source": "Indian Express",
            "category": "entertainment",
            "datetime": datetime_str
        }
        if row_data["title"]:
            data.append(row_data)
    return data


def scrape_entertainment_variety():
    """Scrape entertainment news from Variety"""
    dom = get_dom("https://variety.com/v/film/")
    if dom is None:
        return []
    
    data = []
    for each_res in dom.xpath("//li/article"):
        datetime_str = get_from_xpath(each_res, ".//time[contains(@class,'c-timestamp')]/text()") or ""
        datetime_str = format_datetime(datetime_str)
        
        image_url = get_from_xpath(each_res, ".//img/@src")
        if image_url:
            image_url = image_url.split('?')[0]
        
        link = get_from_xpath(each_res, ".//h3/a/@href")
        
        row_data = {
            "title": get_from_xpath(each_res, ".//h3/a/text()"),
            "link": link,
            "image": image_url,
            "source": "Variety",
            "category": "entertainment",
            "datetime": datetime_str
        }
        
        if row_data["title"] and "variety.com" in link and '/film/' in link and ", " in datetime_str:
            data.append(row_data)
    return data


def scrape_all_news():
    """Main function to scrape all news from all sources with progress tracking"""
    print_banner()
    
    scraped_data = []
    
    scrapers = [
        ("TechCrunch", "Technology", scrape_tech_techcrunch),
        ("The Verge", "Technology", scrape_tech_theverge),
        ("Indian Express", "Economy", scrape_economy_indianexpress),
        ("Economic Times", "Economy", scrape_economy_economictimes),
        ("Indian Express", "Sports", scrape_sports_indianexpress),
        ("Hindustan Times", "Sports", scrape_sports_hindustantimes),
        ("Economic Times", "Politics", scrape_politics_economictimes),
        ("NY Times", "Politics", scrape_politics_nytimes),
        ("Indian Express", "Lifestyle", scrape_lifestyle_indianexpress),
        ("Fox News", "Lifestyle", scrape_lifestyle_foxnews),
        ("Indian Express", "Entertainment", scrape_entertainment_indianexpress),
        ("Variety", "Entertainment", scrape_entertainment_variety),
    ]
    
    print(f"{Colors.HEADER}🚀 Starting news aggregation from {len(scrapers)} sources...{Colors.ENDC}\n")
    
    # Progress bar for overall scraping
    with tqdm(total=len(scrapers), desc="📰 Scraping Progress", 
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} sources [{elapsed}<{remaining}]",
              colour="green") as pbar:
        
        for source_name, category, scraper_func in scrapers:
            try:
                # Update progress bar description
                pbar.set_description(f"🔍 Scraping {source_name}")
                
                # Add small delay for visual effect
                time.sleep(0.5)
                
                # Run the scraper
                data = scraper_func()
                scraped_data.extend(data)
                
                # Update progress bar
                pbar.update(1)
                
            except Exception as e:
                log_scraper_result(source_name, 0, False)
                logger.error(f"Error in {scraper_func.__name__}: {e}")
                pbar.update(1)
    
    # Calculate statistics
    categories_stats = {}
    sources_stats = {}
    
    for article in scraped_data:
        # Category stats
        cat = article['category']
        categories_stats[cat] = categories_stats.get(cat, 0) + 1
        
        # Source stats
        src = article['source']
        sources_stats[src] = sources_stats.get(src, 0) + 1
    
    # Display final summary
    log_final_summary(len(scraped_data), categories_stats, sources_stats)
    
    return scraped_data


def save_to_csv(data, filename="scraped_data.csv"):
    """Save scraped data to CSV file with enhanced logging in data folder"""
    if data:
        print(f"\n{Colors.WARNING}💾 Saving {len(data)} articles to CSV file...{Colors.ENDC}")
        
        # Create data directory path (Railway persistent storage)
        import os
        if os.path.exists("/app/data"):
            # Railway persistent volume
            data_dir = "/app/data"
        else:
            # Local development - get current working directory and add data folder
            current_dir = os.getcwd()
            data_dir = os.path.join(current_dir, "data")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_with_time = f"news_scrape_{timestamp}.csv"
        full_path = os.path.join(data_dir, filename_with_time)
        
        with tqdm(total=1, desc="📁 Writing CSV", colour="blue") as pbar:
            df = pd.DataFrame(data)
            df.to_csv(full_path, index=False)
            pbar.update(1)
        
        print(f"{Colors.OKGREEN}✅ Successfully saved to: {full_path}{Colors.ENDC}")
        logger.info(f"Saved {len(data)} articles to {full_path}")
        return full_path
    else:
        print(f"{Colors.FAIL}❌ No data to save{Colors.ENDC}")
        return False


if __name__ == "__main__":
    """Main execution block for running the scraper standalone"""
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("🚀 AI News Scraper - Standalone Mode")
    print("=" * 50)
    print(f"{Colors.ENDC}")
    
    start_time = datetime.now()
    print(f"{Colors.OKCYAN}📅 Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")
    
    # Run the complete scraper
    scraped_data = scrape_all_news()
    
    # Save to CSV
    if scraped_data:
        csv_file = save_to_csv(scraped_data)
        
        # Calculate execution time
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 SCRAPING COMPLETED SUCCESSFULLY! 🎉{Colors.ENDC}")
        print(f"{Colors.OKCYAN}⏱️  Total execution time: {duration.total_seconds():.1f} seconds{Colors.ENDC}")
        print(f"{Colors.WARNING}📂 Data saved as: {csv_file}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}🌟 Ready for AI processing and website integration!{Colors.ENDC}\n")
    else:
        print(f"{Colors.FAIL}❌ No articles were scraped. Please check your internet connection.{Colors.ENDC}")