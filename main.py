import os
from ebooklib import epub


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

    # Проход по всем элементам книги
    for item in book.get_items_of_type(epub.EpubHtml):
        # Извлечение текста из главы
        chapter_text = item.content.decode('utf-8')

        # Создание новой книги для каждой части
        if current_chapter == 1 or current_chapter % split_size == 1:
            new_book = epub.EpubBook()

        # Добавление главы в новую книгу
        new_chapter = epub.EpubHtml(title=item.title, file_name=f'{base_name}_{current_part}.xhtml')
        new_chapter.content = chapter_text
        new_book.add_item(new_chapter)

        # Если достигнуто максимальное количество глав в части, сохраняем книгу
        if current_chapter % split_size == 0:
            # Сохранение новой книги
            output_file = os.path.join(output_folder, f'{base_name}_{current_part}.epub')
            epub.write_epub(output_file, new_book)

            # Увеличение индекса части
            current_part += 1

        # Увеличение индекса главы
        current_chapter += 1

    # Сохранение последней части, если необходимо
    if current_chapter % split_size != 0:
        output_file = os.path.join(output_folder, f'{base_name}_{current_part}.epub')
        epub.write_epub(output_file, new_book)

    print(f'Книга разделена на {current_part} частей.')


def list_epub_files(folder_path):
    # Получение списка файлов формата .epub в указанной папке
    epub_files = [file for file in os.listdir(folder_path) if file.endswith('.epub')]
    return epub_files


# Получение ввода пользователя для папки с файлами ePub
folder_path = input('Введите путь к папке с файлами ePub: ')

# Получение списка файлов .epub в папке
epub_files = list_epub_files(folder_path)

if not epub_files:
    print('В указанной папке нет файлов формата .epub.')
else:
    print('Доступные файлы для разделения:')
    for i, file in enumerate(epub_files, 1):
        print(f'{i}. {file}')

    # Получение выбора пользователя
    choice = int(input('Введите номер файла для разделения: '))

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