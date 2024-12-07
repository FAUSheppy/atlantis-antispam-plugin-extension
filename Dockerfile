FROM debian:bookworm-slim

RUN apt update -y
RUN apt install -y spamassassin
RUN apt install -y python3 python-is-python3 python3-pip python3-waitress

COPY req.txt /
RUN python -m pip install -r /req.txt --break-system-packages

COPY spamassasin/bayes /etc/spamassassin/bayes
COPY spamassasin/local.cf /etc/spamassassin/local.cf

RUN mkdir /app
WORKDIR /app
RUN echo 11
COPY server/*.py /app/

EXPOSE 5000/tcp

ENTRYPOINT ["waitress-serve"]
CMD ["--host", "0.0.0.0", "--port", "5000", "--call", "app:createApp" ]
