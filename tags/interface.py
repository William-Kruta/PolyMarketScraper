from .local import TagsDB
from .web import fetch_tag_id
from helper import get_data


def get_tag_id(
    db_path: str, tag_name: str = "", tag_id: str = "", force_update: bool = False
):
    db = TagsDB(db_path)
    params = {"tag_name": tag_name, "tag_id": tag_id}
    data = get_data(
        db._read_tags_data,
        params,
        fetch_tag_id,
        params,
        db._insert_tags_data,
        force_update=force_update,
    )
    print(data)
