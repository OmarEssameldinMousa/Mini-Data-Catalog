FROM python:3.11-slim as builder 

WORKDIR app/

COPY requirements.txt .

RUN pip install --prefix=/install -r requirements.txt 

FROM python:3.11-slim as runtime 

RUN apt-get update && apt-get install -y curl --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR app/

COPY --from=builder /install /usr/local

COPY . .

EXPOSE 8000

RUN chmod +x entrypoint.sh

CMD [ "./entrypoint.sh" ]

