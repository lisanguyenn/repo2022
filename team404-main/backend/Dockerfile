FROM python:3.9.15

ARG UID=1000
ARG GID=1000

RUN groupadd -g "${GID}" python \
  && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" python

USER root
RUN apt-get update -qq && apt-get install vim -qqq

LABEL MAINTAINER="Team404"
LABEL GitHub="https://github.com/BigDataForSanDiego/team404"
LABEL version="0.0"

SHELL ["/bin/bash", "-c"]

ARG CLOUD_SDK_VERSION=402.0.0
ENV GCLOUD_HOME=/home/ubuntu/google-cloud-sdk

ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"

RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
    && mkdir -p "${GCLOUD_HOME}" \
    && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
    && "${GCLOUD_HOME}/install.sh" \
       --bash-completion=false \
       --path-update=false \
       --usage-reporting=false \
       --quiet \
    && rm -rf "${TMP_DIR}" \
    && gcloud --version


COPY requirements.txt .
COPY kroger_api_ingest.py .

USER python

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python", "./kroger_api_ingest.py"]