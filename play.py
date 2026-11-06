from os import environ

from dotenv import load_dotenv
from opensearchpy import OpenSearch

load_dotenv()  # values already set in the shell win over .env

LOCAL = environ.get("LOCAL")
INDEX = environ.get("INDEX")

os = OpenSearch(LOCAL)

# search
r = os.search(
    index=INDEX,
    body={"query": {"match": {"location.current.city": "Amsterdam"}}, "size": 3},
)
for hit in r["hits"]["hits"]:
    print(hit["_id"], hit["_source"]["name"])


# # change one profile
# os.update(index=INDEX, id="<doc-id>", body={"doc": {"openToWork": True}})

# # delete one profile
# os.delete(index=INDEX, id="<doc-id>")

# # add a new profile
# os.index(index=INDEX, id="test-1", body={"name": "Test Person", "location": {"current": {"country": "Netherlands"}}})
