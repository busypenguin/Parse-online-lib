import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse
import argparse


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError()


def download_txt(url, payload, filename, folder='books/'):
    response = requests.get(url, params=payload)
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


def parse_book_page(book_num, response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_and_author = soup.find('table').find(class_='ow_px_td').find('h1')
    book_and_author_text = book_and_author.text
    splited_book_and_author_text = book_and_author_text.split(' :: ')
    book_name = (f'{book_num}. {splited_book_and_author_text[0].strip()}')
    book_image_path = soup.find(class_='bookimage').find('img')['src']
    imagepath = urljoin('https://tululu.org/', book_image_path)
    parsed_url = urlparse(imagepath)

    comments = soup.find(id='content').find_all(class_='black')
    all_comments = []
    for comment in comments:
        comment_text = comment.text
        all_comments.append(comment_text)

    genres = soup.find(id='content').find('span', class_='d_book').find_all('a')
    all_genres = []
    for el in genres:
        genre = el.text
        all_genres.append(genre)

    book = {
        'Название': book_name,
        'Картинка книги': parsed_url.path,
        'Комментарии': all_comments,
        'Жанр': all_genres,
    }
    return book


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Программа скачивает книги по их ID'
    )
    parser.add_argument("--start_id", help="ID первой книги", type=int, default=1)
    parser.add_argument("--end_id", help="ID последней книги", type=int, default=10)
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id

    for book_num in range(start_id, end_id+1):
        url_for_book = 'https://tululu.org/b{}/'.format(book_num)
        url_for_download_book = 'https://tululu.org/txt.php'
        payload = {'id': book_num}
        response_for_book = requests.get(url_for_book)
        response_for_book.raise_for_status()

        try:
            check_for_redirect(response_for_book)
            book = parse_book_page(book_num, response_for_book)
            filepath = download_txt(url_for_download_book, payload, book['Название'])

            image_url = urljoin('https://tululu.org', book['Картинка книги'])
            parsed_url = urlparse(image_url)
            book_image_name = os.path.basename(parsed_url.path)
            book_image_path = download_image(image_url, book_image_name)

        except requests.exceptions.HTTPError and requests.exceptions.HTTPError and requests.exceptions.ConnectionError:
            continue
