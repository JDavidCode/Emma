import requests
from bs4 import BeautifulSoup

class BBC_NEWS:
    def __init__(self) -> None:
        pass
    
    def search_new(self, query=str):
        q = query.replace(" ", "+")
        response = requests.get(f"https://www.bbc.co.uk/search?q={q}")
    
    def get_new_content(self, url):
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the web page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the main element with role="main"
            main_element = soup.find('main', {"role": "main"})
            
            # Initialize variables for title and image
            title = None
            image = None
            content = ""
            
            # Find the title within the main element
            if title is None:
                title_element = main_element.find('h1', class_="e1p3vdyi0")
                if title_element:
                    title = title_element.text.strip()

            # Find the image within the main element
            if image is None:
                figure = main_element.find('figure')
                if figure:
                    image_divs = figure.find_all('div')
                    for image_div in image_divs:
                        img = image_div.find('img')
                        if img:
                            image = img['src']

            # Find all paragraphs within the main element
            paragraphs = main_element.find_all('p')
            for paragraph in paragraphs:
                content += paragraph.text.strip() + '\n'

            # Return the data as a dictionary
            data = {
                'Título': title,
                'Imagen': image,
                'Contenido': content
            }
            return data

        else:
            print('No se pudo acceder a la página web.')
            return None

if __name__ == "__main__":
    # Obtain the URL of a BBC article
    url = "https://www.bbc.com/mundo/articles/c3gw2mgj9r8o"
    bbc = BBC_NEWS()
    
    # Scrape the article
    article_data = bbc.get_new_content(url)

    if article_data:
        # Print the article data
        for key, value in article_data.items():
            print(f'{key}: {value}')
