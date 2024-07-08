import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse
import argparse
from time import sleep


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError()


def download_txt(url, payload, filename, folder='books/'):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    filename = sanitize_filename(filename)
    os.makedirs(folder, exist_ok=True)

    check_for_redirect(response)
    filepath = f'{os.path.join(folder, filename)}.txt'
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
    book_image_url = soup.find(class_='bookimage').find('img')['src']
    image_url = urljoin('https://tululu.org/b{}/'.format(book_num), book_image_url)
    parsed_url = urlparse(image_url)

    comments = soup.find(id='content').find_all(class_='black')
    all_comments = [comment.text for comment in comments]

    genres = soup.find(id='content').find('span', class_='d_book').find_all('a')
    all_genres = [genre.text for genre in genres]

    book = {
        'book_name': book_name,
        'book_img': parsed_url.path,
        'comments': all_comments,
        'genre': all_genres,
        'image_url': image_url
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
        book_url = 'https://tululu.org/b{}/'.format(book_num)
        download_book_url = 'https://tululu.org/txt.php'
        payload = {'id': book_num}

        try:
            book_response = requests.get(book_url)
            book_response.raise_for_status()
            check_for_redirect(book_response)
            book = parse_book_page(book_num, book_response)
            filepath = download_txt(download_book_url, payload, book['book_name'])

            book_image_name = os.path.basename(book['book_img'])
            book_image_path = download_image(book['image_url'], book_image_name)

        except requests.exceptions.HTTPError:
            print(f'Книги с номером {book_num} не существует')
            continue

        except requests.exceptions.ConnectionError:
            print('Отсутствует подключение к интернету')
            sleep(5)
            continue
