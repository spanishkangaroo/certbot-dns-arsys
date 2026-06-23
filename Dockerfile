FROM certbot/certbot:latest

COPY . /src
RUN pip install --no-cache-dir /src

ENTRYPOINT ["certbot"]
