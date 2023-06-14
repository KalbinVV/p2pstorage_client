FROM alpine

RUN apk add python3=~3.11
RUN apk add git

RUN git clone https://github.com/KalbinVV/p2pstorage_client.git
RUN git clone https://github.com/KalbinVV/p2pstorage_core.git

RUN mv p2pstorage_core/p2pstorage_core p2pstorage_client/

WORKDIR "/p2pstorage_client"

CMD ["python3.11", "main.py"]
