FROM python:3.9-buster

# Fix OpenSSH issue (stderr is not closed on backgrounded)
RUN echo "deb http://deb.debian.org/debian buster-backports main" | tee --append /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -t buster-backports -y --reinstall --no-install-recommends openssh-client \
    && rm -rf /var/lib/apt/lists/*

# environment settings
ENV PYTHONIOENCODING=UTF-8
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY ./requirements.txt .

RUN \
  python -m pip install --no-cache-dir --upgrade pip setuptools && \
  pip install --no-cache-dir -r requirements.txt

COPY ./src ./

EXPOSE 8000

CMD [ "gunicorn" ]