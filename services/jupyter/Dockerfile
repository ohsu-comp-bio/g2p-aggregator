
FROM python:2.7

RUN mkdir -p /server
WORKDIR /server

RUN apt-get update
RUN apt-get install -y autoconf automake libtool curl make g++ unzip vim


RUN pip install pip --upgrade  \
  && pip install ga4gh  \
  && pip install jupyter  \
  && pip install bokeh \
  && pip install pandas


RUN git clone https://github.com/BD2KGenomics/bioapi-examples.git


WORKDIR /server
RUN pip install elasticsearch
RUN pip install plotly
RUN pip install ipywidgets
RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension

CMD jupyter notebook --notebook-dir=/server/bioapi-examples --ip=0.0.0.0 --NotebookApp.token=  --no-browser
