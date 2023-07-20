FROM python:latest
# Or any preferred Python version.

WORKDIR /project

ADD getSchedule.py .
ADD credentials.json .
ADD secrects.py .
ADD token.json .
ADD crontab .


# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99


# upgrade pip
RUN pip install --upgrade pip

RUN pip install selenium
RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

RUN crontab crontab

#CMD ["python", "./getSchedule.py"] 
CMD ["crond", "-f"]
#CMD ["bash"]
# Or enter the name of your unique directory and parameter set.