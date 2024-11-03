from notion_client import Client, errors
from requests import Response
import json

class Tag():
    def __init__(self, tag_name: str):
        self._tag_name = tag_name
        self._tag_color = self.get_tag_color()

    def get_tag_color(self) -> str:
        tag = self._tag_name
        if tag == "SR":
            return "brown"
        elif tag == "SRv6":
            return "orange"
        elif tag == "SR-MPLS":
            return "yellow"
        elif tag == "fail over":
            return "pink"
        elif tag == "PM":
            return "blue"
        elif tag == "epe":
            return "light gray"
        else:
            return "gray"
        
class NotionClient:
    def __init__(self, token):
        self._token = token
        self.client = Client(auth=self._token)

    def retrieve_database(self, database_id: str) -> Response:
        return self.client.databases.retrieve(database_id)
    
    def get_database_properties(self,
                            database_id: str
                            ) -> dict:
        """
        データベースのプロパティ名とプロパティのタイプを辞書にして返します
        """
        properties = {}
        json_data = self.retrieve_database(database_id)
        for name, value in json_data['properties'].items():
            properties[name] = {'id': value.get('id'),
                                'type': value.get('type')
                                }
        return properties
    
    def read_notion_database(self, database_id):
        response = self.client.databases.query(
            **{
                "database_id": database_id,
            }
        )
        return response

    def list_property_values(self,
                                database_id: str,
                                property_name: str
                                ) -> list:
        """
        データベースの指定したプロパティの値のリストを返します
        """
        properties = self.get_database_properties(database_id)
        if not property_name in properties:
            print(f'properties should be selected in {list(properties.keys())}')
            return []
        
        page_objects = self.list_database_page_object(database_id)
        obj_list = []
        for obj in page_objects:
            obj_list.append(obj[property_name])

        return obj_list
    
    def list_paper_title(self, database_id: str) -> list:
        paper_title_objs = self.list_property_values(database_id, 'Title')
        papaer_titles = []
        for obj in paper_title_objs:
            papaer_titles.append(obj['title'][0]['plain_text'])
        return papaer_titles

    
    def list_database_page_object(self, database_id: str) -> list:
        """
        データベースのページオブジェクトをリストにして全て返します
        """
        db_info = self.read_notion_database(database_id)['results']
        pages = []
        for row in db_info:
            page = {'Title': row['properties']['Title'], 'Tag': row['properties']['Tag'], 'URL': row['properties']['URL'], 'File': row['properties']['File']}
            pages.append(page)
        return pages
    
    def create_properties(self, url: str, title: str, tags: list):
        c_tags = []
        for tag_name in tags:
            c_tag = Tag(tag_name)
            c_tags.append({"name": c_tag._tag_name, "color": c_tag._tag_color})
    
        properties = {
            "URL": {
                "rich_text": [
                    {
                        "text": {
                            "content": url
                        }
                    }
                ]
            },
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "Tag": {
                "multi_select": c_tags
            }
        }

        return properties
    
    def create_properties_from_paper_info(self, paper_info: list) -> list:
        properties = []
        for paper in paper_info:
            property = self.create_properties(paper["url"], paper["title"], paper["tags"])
            properties.append(property)
        return properties
    
    def upload_paper_info(self, database_id: str, paper_info: list):
        properties = self.create_properties_from_paper_info(paper_info)
        print("success: create properties")

        try:
            for property in properties:
                page = self.client.pages.create(
                    **{
                        "parent": {"database_id": database_id},
                        "properties": property
                    }
                )
        except errors.APIResponseError as error:
            if error.code == errors.APIErrorCode.ObjectNotFound:
                print("database_id may be not correct")
            else:
                # Other error handling code
                print(f"target properties:{properties}")

