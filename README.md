# Local copy of Avery OpenSearch data (Netherlands)

Gives you your own local OpenSearch with a copy of the Dutch profiles from
`avery-may-2026`, so you can query and modify data freely without touching production.

The remote OpenSearch account is in `.env`, so nobody has to type it in. Treat this folder as a secret and don't commit it or share it outside the team.

## Files

| File                   | What it is                                                     |
| ---------------------- | -------------------------------------------------------------- |
| `docker-compose.yml` | Starts the local OpenSearch (port 9201) and optional web UI    |
| `pull_nl.py`         | Copies Dutch profiles from the remote index into the local one |
| `play.py`            | Small examples of searching and changing local data            |
| `.env`               | Default settings and the remote account                        |

## What you need

- Docker Desktop (running)
- Node.js: `brew install node`
- elasticdump: `npm install -g elasticdump`
- Python packages: `uv pip install -r requirements.txt`

## 1. Start the local database

```bash
docker compose up -d
```

Wait ~30 seconds, then check:

```bash
curl localhost:9201
```

## 2. Copy the data

```bash
uv run pull_nl.py
```

It uses the remote account from `.env` without asking, then copies
**100,000** Dutch profiles by default. Takes a few minutes and prints progress every 10,000.

Options (set them in `.env`, or per run as below, which overrides `.env`):

| Command                               | What it does                                             |
| ------------------------------------- | -------------------------------------------------------- |
| `uv run pull_nl.py`                 | 100k docs, without large company description/logo fields |
| `SIZE=500000 uv run pull_nl.py`     | 500k docs                                                |
| `SIZE=-1 uv run pull_nl.py`         | All ~7.9M Dutch docs (hours, tens of GB)                 |
| `SLIM=0 uv run pull_nl.py`          | Keep all fields                                          |
| `COUNTRY=Belgium uv run pull_nl.py` | Another country                                          |

For a full copy: give Docker at least 4 GB memory and enough disk
(Docker Desktop → Settings → Resources) and keep the laptop plugged in.

### Check

```Shell
curl "localhost:9201/avery-may-2026/_count"
```

## 3. Use it

```bash
uv run play.py
```

## Stop / remove

```bash
docker compose stop        # stop, keep data
docker compose down -v     # remove everything, including the local data
```

## Start over / clean up

bash

```bash
curl -X DELETE "localhost:9201/avery-may-2026"   # delete local index, then run pull_nl.py again
docker compose stop                               # stop, keep data
docker compose down -v                            # remove everything, including local data
```

## Notes

- This is real personal data (names, emails, LinkedIn). Keep it on an encrypted
  laptop (FileVault), don't share exports outside approved company storage, and
  delete it (`docker compose down -v`) when you no longer need it.
- Port 9201 already in use? Change `"9201:9200"` in `docker-compose.yml` and set
  `LOCAL=http://localhost:<new-port>` in `.env`.
- Mapping step says no permission? The script continues and OpenSearch
  auto-detects the fields, which is fine for local work.
