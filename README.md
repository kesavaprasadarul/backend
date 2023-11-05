# backend
Contains the implementation for backend based on fastapi.

>**Table of Contents**
>  1. [Development](#development) </br>


## Development

### Prerequisites**:
- install Docker
- install [poetry](https://pypi.org/project/poetry/)
- run `poetry install`

### START/RUN
**RECOMMENDED** </br>
Run `docker compose up`.

*MANUALLY* </br>
Go to `src/backend` and run `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` to start fastapi app manually.
Additionally you have to start a postgresql container like specified in docker-compose.yml but manually.


### Run all checks
To run all formatting tools and checks, just run at the root of this repository:
```shell
poetry run ./scripts/run-all-checks.sh
```
