import os
from pathlib import Path
from dotenv import load_dotenv
from opensearchpy import OpenSearch, helpers

# Values already set in the shell win over .env
HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

REMOTE = os.environ.get("OPENSEARCH_URL")
LOCAL = os.environ.get("LOCAL")
INDEX = os.environ.get("INDEX")
COUNTRY = os.environ.get("COUNTRY")
SIZE = int(os.environ.get("SIZE"))  # -1 = all
SLIM = os.environ.get("SLIM", "1") == "1"  # 1 = drop large fields

user = os.environ["OPENSEARCH_USERNAME"]
pw = os.environ["OPENSEARCH_PASSWORD"]

remote = OpenSearch(
    REMOTE, http_auth=(user, pw), timeout=120, max_retries=5, retry_on_timeout=True
)
local = OpenSearch(LOCAL, timeout=120)

query = {"match": {"location.current.country": COUNTRY}}
body = {"query": query}
if SLIM:
    body["_source"] = {
        "excludes": ["experiences.companyDescription", "experiences.companyLogo"]
    }

total = remote.count(index=INDEX, body={"query": query})["count"]
print(f"Matching documents on remote: {total}")
print("Copying ALL documents" if SIZE < 0 else f"Copying up to {SIZE} documents")

if not local.indices.exists(index=INDEX):
    local.indices.create(
        index=INDEX,
        body={"settings": {"index.codec": "best_compression", "number_of_replicas": 0}},
    )
local.indices.put_settings(index=INDEX, body={"index.mapping.total_fields.limit": 5000})


def actions():
    n = 0
    for hit in helpers.scan(remote, index=INDEX, query=body, size=2000, scroll="5m"):
        yield {"_index": INDEX, "_id": hit["_id"], "_source": hit["_source"]}
        n += 1
        if 0 <= SIZE <= n:
            return


ok = failed = 0
for success, info in helpers.streaming_bulk(
    local, actions(), chunk_size=2000, raise_on_error=False
):
    if success:
        ok += 1
        if ok % 10000 == 0:
            print(f"{ok} copied ...")
    else:
        failed += 1
        if failed <= 5:
            print("Failed:", info)

local.indices.refresh(index=INDEX)
print(f"Done. Copied {ok}, failed {failed}.")
print("Local count:", local.count(index=INDEX)["count"])
