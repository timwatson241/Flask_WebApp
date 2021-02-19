
FROM python:3.7
RUN mkdir app
COPY requirements.txt /app/

RUN pip install --requirement /app/requirements.txt
COPY . /app/

EXPOSE 8888
CMD python app/app.py

