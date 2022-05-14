# 1. Pull a Python image. For example, python:3.8 will do the job
FROM python:3.8
# 2. Adding trusting keys to apt for repositories, you can download and add them using the following command:
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -\
# 3. Add Google Chrome. Use the following command for that
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'\
# 4. Update apt:
    && apt-get -y update \
# 5. And install google chrome:
    && apt-get install -y google-chrome-stable \
# 6. Now you need to download chromedriver. First you are going to download the zipfile containing the latest chromedriver release:
    && wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip \
# 7. You downloaded the zip file, so you need to unzip it:
    && apt-get install -yqq unzip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
# 8. Copy your application in a Docker image
COPY . .
# 9. Install your requirements
RUN pip install -r requirements.txt
# 10. Run your application
CMD ["python", "file4.py"]