# Adapted from Miki Tebeka's: http://pythonwise.blogspot.com/2015/04/docker-miniconda-perfect-match.html

FROM ubuntu:14.04

MAINTAINER  user@gmailgroup.com

# System packages 
RUN apt-get update && apt-get install -y curl

# Install miniconda to /miniconda
RUN curl -LO https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
RUN bash Miniconda2-latest-Linux-x86_64.sh -p /miniconda2 -b
RUN rm Miniconda2-latest-Linux-x86_64.sh
ENV PATH=/miniconda2/bin:${PATH}
RUN conda update -y conda

# Python packages from conda
RUN conda install -y flask flask-login

# Python packages from Pip
RUN pip install flask_httpauth
RUN pip install sendmail
RUN pip install email

# Make required directories
RUN mkdir -p /anaplanconnect/lib
RUN mkdir /java
RUN mkdir /logs
RUN mkdir /certificates

# Add required runtimes
COPY AnaplanClient.sh /anaplanconnect/
COPY anaplan-connect-1-3-3-3.jar /anaplanconnect/
COPY /lib/* /anaplanconnect/lib/
COPY jre-8u112-linux-x64.tar.gz /java/

# Change permissions on AnaplanClient.sh
RUN chmod +x ./anaplanconnect/AnaplanClient.sh

# Expand JRE
RUN tar -xvzf /java/jre-8u112-linux-x64.tar.gz -C /java
RUN rm /java/jre-8u112-linux-x64.tar.gz

# Setup application
COPY managed-integration-services.py /
COPY getvar.py /
COPY automationhelper.py /
COPY anaplanapi.py /
COPY sendmail.py /
COPY *.cer /certificates/

ENTRYPOINT ["/miniconda2/bin/python", "/managed-integration-services.py"]
EXPOSE 5001 
