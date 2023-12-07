from concurrent.futures import ThreadPoolExecutor, wait
from queue import Queue

from lxml.etree import HTML
from requests import get

visited_pages = set()
visited_articles = set()

pages_queue = Queue()
articles_queue = Queue()


def query_to_url(query: str) -> str:
    return f"https://www.lrytas.lt/search?q={query}"


def process_page(page_url: str):
    try:
        response = get(page_url)
        tree = HTML(response.text)
        for page_link in tree.xpath(
                "//a[contains(@class, 'LPagination__button')]/@href"
        ):
            page_url = "https://www.lrytas.lt" + page_link
            if page_url not in visited_pages:
                pages_queue.put(page_url)
                visited_pages.add(page_url)
        for article_link in tree.xpath("//a[@class='LPostContent__anchor']/@href"):
            article_url = "https://www.lrytas.lt" + article_link
            if article_url not in visited_articles:
                visited_articles.add(article_url)
                articles_queue.put(article_url)

    except Exception:
        print("Error retrieving url")


if __name__ == "__main__":
    process_page(query_to_url("rytas"))
    with ThreadPoolExecutor(10) as pool:
        futures = [pool.submit(process_page, query_to_url("rytas"))]
        while wait(futures):
            while not pages_queue.empty():
                page = pages_queue.get()
                futures.append(pool.submit(process_page, page))
