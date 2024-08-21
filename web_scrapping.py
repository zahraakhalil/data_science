import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass,asdict
import json
import os


@dataclass
class Article:
    url: str
    post_id: int
    title: str
    keywords: list
    thumbnail: str
    publication_date: str
    last_updated_date: str
    author: str
    content:str


class parseHandling:


    def __init__(self, url: str):
        self.url = url

    def getAllUrl(self,url):
        try:
            page = requests.get(url)
            pageContent = page.content
            soup = BeautifulSoup(pageContent, "lxml")
            fullPage = soup.find_all("loc")
            allArticleUrl=[]
            for page in fullPage:
                allArticleUrl.append(page.text)
            return allArticleUrl
        except Exception as e:
            print(f"Site parser Failed : {e} ")
            return []

    def getArticleUrl(self,url):
        try:
            page = requests.get(url)
            pageContent = page.content
            soup = BeautifulSoup(pageContent, "lxml")
            fullPage = soup.find_all("loc")
            allArticleUrl = []
            for page in fullPage:
                allArticleUrl.append(page.text)
            return allArticleUrl
        except Exception as e:
            print(f"Article Parser Failed : {e}")


class ArticleScraper:
    def __init__(self):
        self.session = requests.Session()

    def scrapeArticle(self, url):
        try:
            session = requests.Session()
            response = session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            metadata_script = soup.find('script', type='application/ld+json')
            metadata = json.loads(metadata_script.string)
            s=""
            print(s)
            article = Article(
                url=url,
                post_id=metadata.get('post_id'),
                title=metadata.get('headline'),
                keywords=metadata.get('keywords'),
                thumbnail=metadata.get('image'),
                publication_date=metadata.get('datePublished'),
                last_updated_date=metadata.get('dateModified'),
                author=metadata.get('author').get('name'),
                content=' '.join(p.get_text() for p in soup.find_all('p'))
            )
            return article
        except Exception as e:
            print(f"Failed to scrape article at {url}: {e}")
            return None

class FileUtility:
    def __init__(self, output_directory):
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)

    def save_to_json(self, articles, year, month):
        filename = f'articles_{year}_{month}.json'
        file_path = os.path.join(self.output_directory, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([asdict(article) for article in articles], f, ensure_ascii=False, indent=4)


def main():

    pageUrl = "https://www.almayadeen.net/sitemaps/all.xml"
    parseHandler=parseHandling(pageUrl)
    scraperObj = ArticleScraper()
    file_utility = FileUtility(output_directory='Json_Files')

    allMonthlyUrl = parseHandler.getAllUrl(pageUrl)
    if not allMonthlyUrl:
        print("No Monthly Url Found!")
        return
    article_scrapped = 0
    maxArticleToScrap = 10000

    for url in allMonthlyUrl:
        articlesUrl = parseHandler.getArticleUrl(url)

        year_month = url.split('-')[-2:]
        year = year_month[0]
        month = year_month[1].replace('.xml', '')
        articlesList=[]
        for articleUrl in articlesUrl:
            if article_scrapped >= maxArticleToScrap:
                break
            data_scraped = scraperObj.scrapeArticle(articleUrl)
            if data_scraped:
                article_scrapped += 1
                articlesList.append(data_scraped)
                file_utility.save_to_json(articlesList, year, month)
                print(f"{data_scraped.title} is the {article_scrapped} article")



if __name__ == "__main__":
    main()