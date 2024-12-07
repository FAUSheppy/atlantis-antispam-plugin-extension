FROM bookworm-slim

RUN apt install -y spamassassin
RUN apt install -y python python-pip python-waitress

COPY req.txt /
RUN python -m pip install -r /req.txt

COPY spamassasin/bayes /etc/spamassasin/bayes
COPY spamassasin/local.cf /etc/spamassasin/local.cf

EXPOSE 5000/tcp

ENTRYPOINT ["waitress-serve"]
CMD ["--host", "0.0.0.0", "--port", "5000", "--call", "app:createApp" ]
