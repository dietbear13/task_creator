from flask import Flask, request, render_template, redirect, url_for
from scr import ConfigLoader, DocumentCreator, HTMLParser
from openpyxl import load_workbook
import logging
import os

app = Flask(__name__)
app.config['DEBUG'] = True  # Включаем режим отладки

logging.basicConfig(level=logging.DEBUG)

# Путь к конфигурационному файлу по умолчанию
DEFAULT_CONFIG_PATH = "C:\\Users\\dietb\\PycharmProjects\\Saiga_70B\\tasks_creator\\config.json"

# Словарь с именами и соответствующими ключами
KEYS = {
    "Миша": "C:\\Users\\dietb\\PycharmProjects\\Saiga_70B\\small-talk-ntfx-9398733134f9.json",  # замените "C:\\path\\to\\key1.json" на реальный путь к ключу
    "Паша": "C:\\path\\to\\key2.json"   # замените "C:\\path\\to\\key2.json" на реальный путь к ключу
}

def process_document(config, topics_input=None):
    logging.debug("Starting document processing")
    document_creator = DocumentCreator(config['service_account_key_path'], config['folder_id'])
    html_parser = HTMLParser(config['xmlriver_url'])

    logs = []

    if topics_input:
        logging.debug("Processing input topics")
        topics = topics_input.split('\n')
    else:
        logging.debug("Loading topics from file")
        wb = load_workbook(config['path'])
        sheet = wb.active
        topics = [cell.value for cell in sheet['A']]

    for topic in topics:
        if topic:
            my_h1 = topic.split(': ')[0]
            my_h2_titles = topic.split(': ')[1]
            my_h2_splited = my_h2_titles.split(', ')

            output_my_headers = f"H1 содержит «{my_h1.capitalize()}»\n"
            for my_h2_title in my_h2_splited:
                output_my_headers += f"H2: {my_h2_title.capitalize()}\n"

            parse_h2_titles, parse_meta_titles, links = html_parser.parse_google_results(topic.split(':')[0], [], [])
            topic, link = document_creator.create_document_and_write_to_file(my_h1, output_my_headers, parse_meta_titles, parse_h2_titles, links)
            logs.append(f"Статья «{topic}» — {link}")

    logging.debug("Document processing completed")
    return logs

@app.route('/')
def index():
    config_loader = ConfigLoader(DEFAULT_CONFIG_PATH)
    config = config_loader.get_config()
    return render_template('index.html', config=config, keys=KEYS)

@app.route('/generate', methods=['POST'])
def generate():
    logging.debug("Received request to generate document")
    logging.debug(f"Request method: {request.method}")
    logging.debug(f"Request form data: {request.form}")
    logging.debug(f"Request files: {request.files}")

    config_path = DEFAULT_CONFIG_PATH

    if 'config_file' in request.files and request.files['config_file'].filename != '':
        config_file = request.files['config_file']
        config_path = os.path.join("C:\\Users\\dietb\\PycharmProjects\\Saiga_70B\\tasks_creator", config_file.filename)
        config_file.save(config_path)

    # Получаем выбранное имя и используем соответствующий ключ
    selected_key = request.form.get('selected_key')
    service_account_key_path = KEYS.get(selected_key, KEYS["Миша"])

    config_loader = ConfigLoader(config_path)
    config = config_loader.get_config()
    config['service_account_key_path'] = service_account_key_path

    topics_input = request.form.get('topics')
    logs = process_document(config, topics_input)
    return render_template('index.html', config=config, logs=logs, keys=KEYS)

if __name__ == "__main__":
    app.run(debug=True)
