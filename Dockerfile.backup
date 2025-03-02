####################################################################################################
#
# Multi-stage build for backend docker containers
# ==================================================
#
# STAGE 1: system
#   python system, install all packages, install poetry, copy stuff
#
# STAGE 2: fastapi-app
#   Final, poetry tooling installed, current poetry cache available. Used to _build_ backend and run
#   code checkers.
#
####################################################################################################

# globally shared vars:
ARG PORTAL_HOME=/opt/backend
ARG PORTAL_PYTHON=python3.11

# -------------------------------------
# Stage 1: system
# -------------------------------------
# create image based on ubuntu base image
FROM python:3.11 as system

RUN pip install poetry==1.8.5

ARG PORTAL_HOME
ARG PORTAL_PYTHON

WORKDIR ${PORTAL_HOME}

COPY poetry.toml poetry.lock pyproject.toml ${PORTAL_HOME}/

# create portal run environment:
RUN poetry export > requirements.txt && \
    $PORTAL_PYTHON -m venv $PORTAL_HOME && \
    $PORTAL_HOME/bin/pip install -U setuptools pip wheel && \
    $PORTAL_HOME/bin/pip install --no-cache-dir --upgrade -r requirements.txt


# -------------------------------------
# Stage 2: fastapi-app (FINAL)
# -------------------------------------
FROM system as fastapi-app

ARG PORTAL_HOME

# set workdir to backend package
WORKDIR ${PORTAL_HOME}

# copy venv from stage 3 "build"
COPY --from=system ${PORTAL_HOME} ${PORTAL_HOME}

# copy source code of the app:
COPY src/ ${PORTAL_HOME}/

# add venv binaries to path:
ENV PATH="${PORTAL_HOME}/bin:$PATH"
