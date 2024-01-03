import os
from ebooklib import epub
from bs4 import BeautifulSoup
import zipfile
import re


def list_epub_files(folder_path):
    # Получение списка файлов формата .epub в указанной папке
    epub_files = [file for file in os.listdir(folder_path) if file.endswith('.epub')]
    return epub_files


def print_book_content(file_path):
    chapter_titles = []

    with zipfile.ZipFile(file_path, 'r') as zip_file:
        for file_info in zip_file.infolist():
            with zip_file.open(file_info) as file:
                # Изменим режим на бинарный
                content = file.read()
                soup = BeautifulSoup(content, 'html.parser')

                # Извлечение текста из заголовков глав
                for header_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    chapter_titles.append(header_tag.text.strip())

    return chapter_titles


def split_epub(input_file, split_size):
    # Загрузка файла ePub
    book = epub.read_epub(input_file)

    # Получение базового имени файла (без расширения)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Создание папки для сохранения разделенных файлов
    output_folder = f'{base_name}_split'
    os.makedirs(output_folder, exist_ok=True)

    # Индекс текущей главы
    current_chapter = 1
    current_part = 1

    # Инициализация новой книги
    new_book = epub.EpubBook()

    # Проход по всем элементам книги
    for item in book.get_items_of_type(epub.EpubHtml):
        # Извлечение текста из главы
        chapter_text = item.content.decode('utf-8')

        # Добавление главы в новую книгу
        new_chapter = epub.EpubHtml(title=item.title, file_name=f'{base_name}_{current_part}.xhtml')
        new_chapter.content = chapter_text
        new_book.add_item(new_chapter)

        # Увеличение индекса главы
        current_chapter += 1

        # Если достигнуто максимальное количество глав в части, сохраняем книгу и создаем новую
        if current_chapter % split_size == 0:
            # Сохранение новой книги
            output_file = os.path.join(output_folder, f'{base_name}_{current_part}.epub')
            epub.write_epub(output_file, new_book)

            # Увеличение индекса части и создание новой книги
            current_part += 1
            new_book = epub.EpubBook()

    # Сохранение последней части, если необходимо
    if current_chapter % split_size != 0:
        output_file = os.path.join(output_folder, f'{base_name}_{current_part}.epub')
        epub.write_epub(output_file, new_book)

    print(f'Книга разделена на {current_part} частей.')


# Получение папки, в которой находится программа
folder_path = os.path.dirname(os.path.abspath(__file__))

# Получение списка файлов .epub в папке
epub_files = list_epub_files(folder_path)

if not epub_files:
    print('В текущей папке нет файлов формата .epub.')
else:
    print('Доступные файлы для разделения:')
    for i, file in enumerate(epub_files, 1):
        print(f'{i}. {file}')

    # Получение выбора пользователя
    choice = int(input('Введите номер файла для разделения: '))

    # Вывод содержания или заголовков глав выбранной книги
    selected_file = epub_files[choice - 1]
    file_path = os.path.join(folder_path, selected_file)


    # Пример использования
    titles = print_book_content(file_path)

    # Вывод заголовков глав
    for title in titles:
        print(f' - {title}')

    # Получение ввода пользователя для количества глав в одной части
    split_size = int(input('Введите количество глав в одной части: '))

    # Проверка корректности выбора пользователя
    if 1 <= choice <= len(epub_files):
        selected_file = epub_files[choice - 1]
        file_path = os.path.join(folder_path, selected_file)

        # Пример использования
        split_epub(file_path, split_size)
    else:
        print('Некорректный выбор файла.')
