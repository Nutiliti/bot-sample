FROM node:16.17 AS builder
WORKDIR /app
# Install latest stable Chrome
# https://gerg.dev/2021/06/making-chromedriver-and-chrome-versions-match-in-a-docker-image/
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | \
  tee -a /etc/apt/sources.list.d/google.list && \
  wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | \
  apt-key add - && \
  apt-get update && \
  apt-get install -y google-chrome-stable google-chrome-beta xvfb libxss1 python3 python3-pip sudo libxtst-dev libpng++-dev

COPY ./bots/pdfDownloaderNode/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# Install the Chromedriver version that corresponds to the installed major Chrome version
# https://blogs.sap.com/2020/12/01/ui5-testing-how-to-handle-chromedriver-update-in-docker-image/
RUN google-chrome --version | grep -oE "[0-9]{1,10}.[0-9]{1,10}.[0-9]{1,10}" > /tmp/chromebrowser-main-version.txt
RUN wget --no-verbose -O /tmp/latest_chromedriver_version.txt https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$(cat /tmp/chromebrowser-main-version.txt)
RUN wget --no-verbose -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/$(cat /tmp/latest_chromedriver_version.txt)/chromedriver_linux64.zip && rm -rf /opt/selenium/chromedriver && unzip /tmp/chromedriver_linux64.zip -d /opt/selenium && rm /tmp/chromedriver_linux64.zip && mv /opt/selenium/chromedriver /opt/selenium/chromedriver-$(cat /tmp/latest_chromedriver_version.txt) && chmod 755 /opt/selenium/chromedriver-$(cat /tmp/latest_chromedriver_version.txt) && ln -fs /opt/selenium/chromedriver-$(cat /tmp/latest_chromedriver_version.txt) /usr/bin/chromedriver

RUN npm install --global pnpm@7
COPY pnpm-lock.yaml ./bots/pdfDownloaderNode/.npmrc ./
RUN pnpm fetch
COPY . .

RUN pnpm -r install --filter pdf-downloader-node... --prefer-offline
RUN pnpm --filter pdf-downloader-node^... build

ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

RUN echo "pnpm build && pnpm start" > /root/.bash_history
WORKDIR /app/bots/pdfDownloaderNode
# Run command
CMD ["/bin/bash", "./run.sh"]
