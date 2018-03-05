FROM python:2.7
COPY *.* ./
RUN pip install -r requirements.txt
CMD python app.py --swagger_host $SWAGGER_HOST --elastic $ES
