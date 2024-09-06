from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET

class HTMLParser:
    def __init__(self, xmlriver_url):
        self.xmlriver_url = xmlriver_url

    def extract_h2_titles(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        h2_titles = [h2.text for h2 in soup.find_all('h2')]
        h2_titles = [title.replace('\xa0', ' ').replace('\r', '').replace('\n', '').replace('\t', '') for title in h2_titles]
        return h2_titles

    def extract_meta_titles(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        meta_titles = [title.text for title in soup.find_all('title')]
        meta_titles = [title.replace('\xa0', ' ').replace('\r', '').replace('\n', '').replace('\t', '') for title in meta_titles]
        return meta_titles

    def parse_google_results(self, query, links, parse_meta_titles):
        url = f'{self.xmlriver_url}&query={query}'

        try:
            response = requests.get(url)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                count = 0
                for group in root.findall(".//group"):
                    url = group.find(".//url").text
                    links.append(url)
                    count += 1
                    if count >= 5:
                        break

                h2_titles = []
                for link in links:
                    try:
                        response = requests.get(link)
                        if response.status_code == 200:
                            h2_titles.extend(self.extract_h2_titles(response.content))
                            parse_meta_titles.extend(self.extract_meta_titles(response.content))
                    except requests.exceptions.RequestException:
                        print(f"Не удалось получить контент страницы: {link}")
                        continue
                return h2_titles, parse_meta_titles, links
        except Exception as e:
            print(f"Произошла ошибка при выполнении запроса: {e}")
            return [], [], []
