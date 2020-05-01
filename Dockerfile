FROM ubuntu:14.04

RUN apt-get update -y
RUN apt-get install -y --fix-missing build-essential 
RUN apt-get install -y --fix-missing gcc 
RUN apt-get install -y --fix-missing python-dev 
RUN apt-get install -y --fix-missing python-pip 
RUN apt-get install -y --fix-missing libmysqlclient-dev 
RUN apt-get install -y --fix-missing git  
RUN apt-get install -y --fix-missing wget 
RUN apt-get install -y --fix-missing unzip 
RUN apt-get install -y --fix-missing firefox
RUN apt-get install -y --fix-missing xvfb 
RUN apt-get install -y --fix-missing tar

RUN apt-get update -y
RUN apt-get install -y --fix-missing curl
RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz
RUN mkdir -p /usr/local/gcloud
RUN tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz
RUN /usr/local/gcloud/google-cloud-sdk/install.sh
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

WORKDIR /app

ENV PATH="/app:${PATH}"

COPY unsubscribe/geckodriver.sh /app/geckodriver.sh
RUN sh /app/geckodriver.sh

RUN pip install setuptools==44 -U
COPY unsubscribe/requirements.txt /app/requirements.txt
RUN pip install --upgrade --ignore-installed six==1.10.0
RUN pip install -r /app/requirements.txt

RUN pip install --upgrade --ignore-installed google-cloud-logging==1.15.0


RUN pip install --upgrade --ignore-installed  google-cloud-core==1.3.0
RUN pip install --upgrade --ignore-installed google-api-core==1.17.0
RUN pip install --upgrade --ignore-installed google-api-python-client==1.7.4



COPY unsubscribe/source/ /app/
COPY auth /auth/

ENV GOOGLE_APPLICATION_CREDENTIALS="/auth/hosting-2718-53999677960d.json"

ENV PYTHONPATH /app/

RUN echo "$(cat /app/main.py)\nmainMaster()" > /app/main.py

ENTRYPOINT ["python"]

CMD ["main.py"]

# cp unsubscribe/Dockerfile* .; docker build  -t latest .; docker tag latest gcr.io/hosting-2718/unsubmaster; docker push gcr.io/hosting-2718/unsubmaster;


# docker run gcr.io/hosting-2718/unsubmaster;