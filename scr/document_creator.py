import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime


class DocumentCreator:
    def __init__(self, service_account_key_path, folder_id):
        self.service_account_key_path = service_account_key_path
        self.folder_id = folder_id
        self.creds = self.get_credentials()
        self.service = build('docs', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    def get_credentials(self):
        if os.path.exists(self.service_account_key_path):
            print(f"service_account_key_path {self.service_account_key_path}")
            return service_account.Credentials.from_service_account_file(self.service_account_key_path)
        else:
            raise FileNotFoundError("Service account key file not found.")

    def utf16len(self, s):
        return len(s.encode('utf-16-le')) // 2

    def clean_text(self, text):
        return text.strip()

    def create_document_and_write_to_file(self, topic, output_my_headers, parse_meta_titles, parse_h2, links):
        topic = self.clean_text(topic)
        output_my_headers = self.clean_text(output_my_headers)
        parse_meta_titles = [self.clean_text(title) for title in parse_meta_titles]
        parse_h2 = [self.clean_text(h2) for h2 in parse_h2]
        links = [self.clean_text(link) for link in links]

        body = {
            'title': topic.capitalize()
        }
        doc = self.service.documents().create(body=body).execute()
        document_id = doc.get('documentId')
        print(f'Создан новый документ: {doc.get("title")}')

        title_section = f"Title: {topic.capitalize()}\n\nTitle в выдаче:\n{'\n'.join(parse_meta_titles)}\n\n"
        content_section = f"Содержание текста\n{output_my_headers}\n\n"
        competitors_section = f"У конкурентов:\n{'\n'.join(parse_h2)}\n"
        technical_requirements_section = "Технические требования\nОбъем текста от X слов. Объем может быть больше или меньше, главное – раскрыть тему полностью, но без воды.\nУникальность по text.ru от 85%.\nИзбегаем речевого мусора, канцеляритов и вводных слов.\n"
        examples_section = f"Примеры текстов:"

        pattern = title_section + content_section + competitors_section + technical_requirements_section + examples_section

        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1
                    },
                    'text': f"{pattern}"
                }
            }
        ]

        # Отладочные принты
        # print(f'Pattern length: {self.utf16len(pattern)}')
        # print(f'Title section length: {self.utf16len(title_section)}')
        # print(f'Content section length: {self.utf16len(content_section)}')
        # print(f'Competitors section length: {self.utf16len(competitors_section)}')
        # print(f'Technical requirements section length: {self.utf16len(technical_requirements_section)}')
        print(f'Examples section length: {self.utf16len(examples_section)}')
        #
        # print(f'Pattern: {pattern}')
        # print(f'Title section: {title_section}')
        # print(f'Content section: {content_section}')
        # print(f'Competitors section: {competitors_section}')
        # print(f'Technical requirements section: {technical_requirements_section}')
        print(f'Examples section: {examples_section}')

        # Добавляем буллеты
        start_index = self.utf16len(pattern[:pattern.index("Title в выдаче:") + len("Title в выдаче: ")])
        end_index = start_index + self.utf16len('\n'.join(parse_meta_titles))

        print(f'Title в выдаче start_index: {start_index}, end_index: {end_index}')

        requests.append({
            'createParagraphBullets': {
                'range': {
                    'startIndex': start_index + 1,
                    'endIndex': end_index
                },
                'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
            }
        })

        start_index = self.utf16len(pattern[:pattern.index("У конкурентов:") + len("У конкурентов: ")]) + 1
        end_index = start_index + self.utf16len('\n'.join(parse_h2))

        print(f'У конкурентов start_index: {start_index}, end_index: {end_index}')

        requests.append({
            'createParagraphBullets': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
            }
        })

        pattern_length = self.utf16len(pattern)
        list_items = links

        # Вставка ссылок
        for item in list_items:
            requests.append({
                'insertText': {
                    'location': {
                        'index': pattern_length
                    },
                    'text': f"\n{item}\n",
                }
            })
            pattern_length += self.utf16len(item) + 1

        # Обновление стилей заголовков
        headings = ["Содержание текста", "У конкурентов:", "Технические требования", "Примеры текстов:"]
        for heading in headings:
            start_index = self.utf16len(pattern[:pattern.index(heading)])
            end_index = start_index + self.utf16len(heading)
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start_index + 1,
                        'endIndex': end_index + 1
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_2',
                    },
                    'fields': 'namedStyleType'
                }
            })

        # Подсветка текста
        start_index = self.utf16len(pattern[:pattern.index("Объем текста от X слов.") + len("Объем текста от ") + 1])
        end_index = start_index + 1
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index,
                },
                'textStyle': {
                    'backgroundColor': {
                        'color': {
                            'rgbColor': {'red': 0.98, 'green': 0.97, 'blue': 0.55}
                        }
                    }
                },
                'fields': 'backgroundColor'
            }
        })

        start_index = self.utf16len(pattern[:pattern.index("Title:") + len("Title: ")]) + 1
        end_index = start_index + self.utf16len(topic)
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index,
                },
                'textStyle': {
                    'backgroundColor': {
                        'color': {
                            'rgbColor': {'red': 0.98, 'green': 0.97, 'blue': 0.55}
                        }
                    }
                },
                'fields': 'backgroundColor'
            }
        })

        # Выполнение запросов на обновление документа
        self.service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        file_id = doc['documentId']
        print(f'Текст успешно записан в документ: {topic}')

        file = self.drive_service.files().get(fileId=file_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        file = self.drive_service.files().update(fileId=document_id, addParents=self.folder_id,
                                                 removeParents=previous_parents,
                                                 fields='id, parents').execute()
        link = f"https://docs.google.com/document/d/{file.get('id')}"

        try:
            df = pd.read_excel('result_links.xlsx')
        except FileNotFoundError:
            df = pd.DataFrame(columns=['Тема', 'Ссылка'])

        current_date = datetime.now().strftime('%d.%m.%Y')

        new_row = {'Тема': topic, 'Ссылка': link, 'Дата': current_date}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        df.to_excel('result_links.xlsx', index=False)

        print(f"Статья «{topic}» — {link}")
        return topic, link
