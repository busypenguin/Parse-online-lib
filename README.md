# Парсер книг с сайта tululu.org

Проект создан для автоматического скачивания книг в предверии поездки на дачу. Нужно только скачать репозиторий, установить зависимости (requirements.txt) и можно запускать программу!

### Как установить

Установить необходимые библиотеки можно, написав в терминале:

``` pip install -r requirements.txt ```

### Аргументы

Можно также выбирать, какую по счёту добавления в библиотеку, книгу вы хотите скачать. Для этого нужно написать в терминале:

```python3 main.py --start_id  20 --end_id 30 ```,

где ``` start_id ```-- это с какого ID скачивать, а  ``` end_id ``` -- по какой.


Также, можете скачать первые 10 книг, написав в терминале команду:

``` python3 main.py ```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).