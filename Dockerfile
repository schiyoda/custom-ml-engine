FROM python:3.6-slim

COPY run_server.py /home/jovyan/
COPY requirements.txt /home/jovyan/
COPY models /home/jovyan/models

RUN pip install -r /home/jovyan/requirements.txt

EXPOSE 5000

CMD cd /home/jovyan && python /home/jovyan/run_server.py