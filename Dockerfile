ARG DST=/usr/src/app/

FROM python:3.11.9 as runtime_stage
ARG DST
COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY src/ ${DST}src/
COPY artifacts/ ${DST}artifacts/

WORKDIR ${DST}

CMD ["python3", "src/main.py"]