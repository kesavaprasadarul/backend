FROM ubuntu:noble AS system
# Set environment variables (adjust as needed)
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB

# **Explicitly set ENV variables BEFORE starting PostgreSQL**
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=fastapi
ENV POSTGRES_SERVER=db

ARG PORTAL_HOME=/opt/backend
ARG PYTHON_PATH=${PORTAL_HOME}/bin

COPY scripts/install-python.sh /tmp/

# Install Python
RUN chmod +x /tmp/install-python.sh && /tmp/install-python.sh
WORKDIR ${PORTAL_HOME}
COPY requirements.txt ${PORTAL_HOME}/

# Create a virtual environment
RUN python3.11 -m venv ${PYTHON_PATH}
ENV PATH="${PYTHON_PATH}:$PATH"

FROM system AS base

# # Install PIP dependencies with the environment activated
RUN . ${PYTHON_PATH}/bin/activate && pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# # Install PIP dependencies, no environment is created
# RUN pip install --no-cache-dir --upgrade -r requirements.txt --break-system-packages

FROM base AS fastapi-app

ARG PORTAL_HOME=/opt/backend
ARG PYTHON_PATH=${PORTAL_HOME}/bin
ENV PATH="${PYTHON_PATH}:$PATH"

# Set environment variables (adjust as needed)
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB

# **Explicitly set ENV variables BEFORE starting PostgreSQL**
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=fastapi
ENV POSTGRES_SERVER=db

# set workdir toseri backend package
WORKDIR ${PORTAL_HOME}

# copy source code of the app:
COPY src/ ${PORTAL_HOME}/
COPY src/backend/ ${PORTAL_HOME}/backend/
COPY src/backend/app/ ${PORTAL_HOME}/backend/app/

# add venv binaries to path:
ENV PATH="${PORTAL_HOME}/bin:$PATH"
COPY backup_20240602 /tmp/
COPY scripts/run_restore.sh /tmp/
RUN chmod +x /tmp/run_restore.sh
COPY scripts/wait_db_start.sh /tmp/
RUN chmod +x /tmp/wait_db_start.sh
#set working directory to backend
WORKDIR ${PORTAL_HOME}

COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# CMD alembic upgrade head && /tmp/run_restore.sh && uvicorn main:app --host
CMD /tmp/run_restore.sh && uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 80 --workers 4
