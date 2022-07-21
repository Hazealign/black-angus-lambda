#!/bin/sh

mkdir -p bin/
curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-57/stable-headless-chromium-amazonlinux-2.zip > headless-chromium.zip
unzip headless-chromium.zip -d bin/
rm headless-chromium.zip

curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
unzip chromedriver.zip -d bin/
rm chromedriver.zip
