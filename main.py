import requests
import os


os.makedirs("books", exist_ok=True)

for num_book in range(1, 11):
    url = 'https://tululu.org/txt.php?id='+str(num_book)
    response = requests.get(url)
    response.raise_for_status()
    filename = 'books/book'+str(num_book)+'.txt'
    with open(filename, 'wb') as file:
        file.write(response.content)
