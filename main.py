import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, urlsplit, unquote


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


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(num_book, response):
    response.raise_for_status()
    check_for_redirect(response)
    book_info = {}
    soup = BeautifulSoup(response.text, 'lxml')
    book_and_author = soup.find('table').find(class_='ow_px_td').find('h1')
    book_and_author_text = book_and_author.text
    splited_book_and_author_text = book_and_author_text.split(' :: ')
    book_name = str(num_book)+'. '+splited_book_and_author_text[0].strip()
    book_info['Название'] = book_name
    book_image = soup.find(class_='bookimage').find('img')['src']
    imagepath = urljoin('https://tululu.org/', book_image)
    parsed_url = urlparse(imagepath)
    book_image_name = os.path.basename(parsed_url.path)
    book_image = download_image(imagepath, book_image_name)
    book_info['Картинка книги'] = book_image

    comments = soup.find(id='content').find_all(class_='black')
    comments_list = []
    for comment in comments:
        comment_text = comment.text
        comments_list.append(comment_text)
    book_info['Комментарии'] = comments_list

    genres = soup.find(id='content').find('span', class_='d_book').find_all('a')
    genres_list = []
    for el in genres:
        genre = el.text
        genres_list.append(genre)
    book_info['Жанр'] = genres_list
    return book_info


for num_book in range(1, 11):
    url_for_book_info = 'https://tululu.org/b{}/'.format(num_book)
    url_for_download_book = 'https://tululu.org/txt.php?id={}'.format(num_book)
    response_for_book_info = requests.get(url_for_book_info)

    try:
        filepath = download_txt(url_for_download_book, parse_book_page(num_book, response_for_book_info)['Название'])

        imagepath = urljoin('https://tululu.org/', parse_book_page(num_book, response_for_book_info)['Картинка книги'])
        parsed_url = urlparse(imagepath)
        book_image_name = os.path.basename(parsed_url.path)
        book_image = download_image(imagepath, book_image_name)

    except requests.exceptions.HTTPError:
        continue
