DElETE Later:  
      connections being used (GPIO.BCM Notations):  
            nrf24l01 -> Vcc, GND, 08, 17, 10, 09, 11  
            


Flow:  
```
      HTML Files: Displays Page Elements  
                       |  
                       v  
      Flask API: Interacts with HTML Files and Communicates with RESTful API  
      
```  

## ********************************** RaspberryPi Setup **********************************

1) Download the Raspi Pi Imager, Then Select Ubunto Server 32 or 64 bit, download this too a SD Card. I used UBUNTU 64 Bit Operating System.
  **NOTE**: If You want to avoid using a Monitor and Keyboard to set up the WIFI connection on the Raspberry Pi:  
  ```
            1. Press Control+Shift+X on the Raspberry Imager  
            2. Enable SSH  
            3. Enable WiFi, then Add Wifi SSID and Password, with the lan country code set to 'US'  
            4. SKIP TO PART 4 
  ```
2) Boot the Raspi and Login:
  [Defualt Username and Passwords]
    - Username: ubunto
    - password: ubunto

3) At this point, You should have Ubuntu Server installed, BUT not connected to the wifi if you didnt hook it up too ethernet.
  - To solve this:
      - Navigate 'cd /etc/netplan' where there should be a '50-cloud-init.yaml' file. [Open this File using Vim]
      - Under 'version: 2', start adding the following to connect wirelessly through Wifi
      ```yaml
      wifis:
        wlan0:
          dhcp4: true
          optional: true
          access-points:
            "NameOfWirelessRouter":
              password: "Password"
      ```
   - 'sudo reboot' and it should have connected to your wireless router.

4) Connect Using SSH
    - Download Putty to ssh into RaspverryPi by connecting to the Raspi via IP Address or use visual studio code Remote-SSH plugin.
    - To Obtain the IP Address of the Pi: Login into your router and find Raspberry Pi.

5) Configure and setup GITHUB
    - ``` git init ``` in the directory you want to link to the repository
    - Set up user Information: 
      ```
       git config --global user.email "you@example.com"
       git config --global user.name "Your Name"
      ```
    - Generate SSH Key:``` ssh-keygen -t rsa ``` then add the key ``` ssh-add ```
    - Copy this Key ``` cat id_rsa.pub ``` - located in ~/home/pi/.ssh
    - Open Github: Settings -> SSH Key -> "Add New Key" -> Paste the id_rsa Key

## ********************************* Installing Packages *********************************

1) First, Lets setup Docker on our raspberryPi
      - update/upgrade: ``` sudo apt update && sudo apt upgrade -y ```
      - Install Docker:  ```  sudo apt-get install \
                              apt-transport-https \
                              ca-certificates \
                              curl \
                              gnupg \
                              lsb-release 
                        ```  
      - Add Dockers Official GPG Key: ``` curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg  ```
      - IF YOU CHOSE A 64 BIT OPERATING SYSTEM, SUCH AS UBUNTU 64 BIT -> Then setup a stable repository for arm64:   ```  
                                    echo \
                                    "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
                                    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 
                              ```
      - Install Docker Engine: ``` sudo apt-get update
                                   sudo apt-get install docker-ce docker-ce-cli containerd.io 
                              ```
      - Verify Install: ``` Docker Version ```
      - Add permission to User to run Docker Commands: ``` sudo usermod -aG docker $USER ```  
      - Next install Docker Compose: ``` sudo curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose ```
      - Install Docker Compose ARM64: ``` sudo curl -L --fail https://github.com/AppTower/docker-compose/releases/download/latest/run.sh -o /usr/local/bin/docker-compose ```
      - Apply Executbale permissions to binary: ``` sudo chmod +x /usr/local/bin/docker-compose ```
      - Verify Docker Compose Install: ``` docker-compose --version ```
      - ``` sudo reboot ```

2) Next, Lets create the directory structure for Docker
      - * Strucutre: Docker(file) -> docker-compose.yml -> builds image -> runs container *
      - Create a 'DockerFile': ``` sudo vim Dockerfile ```
            - Add the following to the Dockerfile:
      ```yaml
      FROM python:3

      WORKDIR /home/HomeAutomation

      COPY requirements.txt ./
      RUN pip install --no-cache-dir -r requirements.txt

      COPY . .

      CMD ["python", "./run.py"]

      ```
      - **WORKDIR** : Your projects working directory  
      - **COPY** : Copy requirements.txt folder then run an install on them  
      - **CMD** : runs 'python ./run.py' in the terminal

      ```
      - Create the './run.py' file used in the terminal command ``` sudo vim run.py ```  
      - Create a docker-compose.yml file: Add the following

      ```yaml
           version: '3.4'

            services:
                  device_registry: 
                        build: . 
                        volumes:
                              - .:/home/HomeAutomation/
                        ports:
                              - 5001:5001
                        privileged: True
      ```
      - lastly, create the ``` requirements.txt ``` file. Add All Python Libraries to here.
      - build the docker container to apply an changes: ``` docker-compose build ```
      - then run the docker container: ``` docker-compose up ```
