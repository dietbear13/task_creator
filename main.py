from scr import ConfigLoader, DocumentCreator, HTMLParser
from openpyxl import load_workbook

def main():
    config_loader = ConfigLoader('config.json')
    config = config_loader.get_config()

    document_creator = DocumentCreator(config['service_account_key_path'], config['folder_id'])
    html_parser = HTMLParser(config['xmlriver_url'])

    output_my_headers = ""
    wb = load_workbook(config['path'])
    sheet = wb.active
    for cell in sheet['A']:
        topic = cell.value
        if topic:
            my_h1 = topic.split(': ')[0]
            my_h2_titles = topic.split(': ')[1]
            my_h2_splited = my_h2_titles.split(', ')

            output_my_headers += f"H1 содержит «{my_h1.capitalize()}»\n"
            for my_h2_title in my_h2_splited:
                output_my_headers += f"H2: {my_h2_title.capitalize()}\n"

            parse_h2_titles, parse_meta_titles, links = html_parser.parse_google_results(topic.split(':')[0], [], [])
            document_creator.create_document_and_write_to_file(my_h1, output_my_headers, parse_meta_titles, parse_h2_titles, links)

            output_my_headers = ""
            parse_h2_titles.clear()
            links.clear()
            parse_meta_titles.clear()

    print("Генерация завершена.")

if __name__ == "__main__":
    main()
