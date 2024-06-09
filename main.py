import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError()


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    response.raise_for_status()
    filename = sanitize_filename(filename)
    os.makedirs(folder, exist_ok=True)

    check_for_redirect(response)
    filepath = os.path.join(folder, filename)+'.txt'
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


for num_book in range(1, 11):
    url_for_book_name = 'https://tululu.org/b{}/'.format(num_book)
    url_for_download_book = 'https://tululu.org/txt.php?id={}'.format(num_book)
    response_for_book_name = requests.get(url_for_book_name)
    response_for_book_name.raise_for_status()
    
    soup = BeautifulSoup(response_for_book_name.text, 'lxml')
    book_and_author = soup.find('table').find(class_='ow_px_td').find('h1')
    book_and_author_text = book_and_author.text
    splited_book_and_author_text = book_and_author_text.split(' :: ')
    book_name = str(num_book)+'. '+splited_book_and_author_text[0].strip()

    try:
        filepath = download_txt(url_for_download_book, book_name)
    except requests.exceptions.HTTPError:
        continue
