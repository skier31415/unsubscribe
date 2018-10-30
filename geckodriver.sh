#wget -N https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -P /app/
#dpkg -i --force-depends /app/google-chrome-stable_current_amd64.deb
#apt-get -f install -y
#dpkg -i --force-depends /app/google-chrome-stable_current_amd64.deb


#wget -N http://chromedriver.storage.googleapis.com/2.27/chromedriver_linux64.zip -P /app/
#unzip /app/chromedriver_linux64.zip -d /app/
#rm /app/chromedriver_linux64.zip
#chmod +x /app/chromedriver


wget -N https://github.com/mozilla/geckodriver/releases/download/v0.22.0/geckodriver-v0.22.0-linux64.tar.gz -P /app/

tar -xvzf /app/geckodriver-v0.22.0-linux64.tar.gz

