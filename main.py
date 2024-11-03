import os, glob
from dotenv import load_dotenv
import pprint
from module import NotionClient
from module import YamlParser


def main():
    load_dotenv()

    file_name = os.getenv("FILE_PATH")
    parser = YamlParser(file_name)
    data = parser.read_config_file()
    
    

    token = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DB_ID")

    client = NotionClient(token = token)

    client.upload_paper_info(database_id, data)

main()

