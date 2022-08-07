Flow:  
```
      HTML Files: Displays Page Elements  
                       |  
                       v  
      Flask API: Interacts with HTML Files and Communicates with RESTful API  
      
```  

## ************************************** RaspberryPi Setup **************************************

1) Download the Raspi Pi Imager, Then Select Ubunto Server 32 bit and download this too a SD Card  
  **NOTE**: If You want to avoid using a Monitor and Keyboard to set up the WIFI connection on the Raspberry Pi:  
  ```
            1. Press Control+Shift+X on the Raspberry Imager  
            2. Enable SSH  
            3. Enable WiFi, then Add Wifi SSID and Password, with the lan country code set to 'US'  
            4. SKIP TO PART 3.  
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
    - Download Putty to ssh into RaspverryPi by connecting to the Raspi via IP Address
    - To Obtain the IP Address of the Pi: Login into your server and find the connect raspi.
5) Configure and setup GITHUB
    - ``` git init ``` in the directory you want to link to the repository
    - Set up User Information: 
      ```
       git config --global user.email "you@example.com"
       git config --global user.name "Your Name"
      ```
    - Generate SSH Key:``` ssh-keygen -t rsa ``` then add the key ``` ssh-add ```
    - Copy this Key ``` cat id_rsa.pub ```
    - Open Github: Settings -> SSH Key -> "Add New Key" -> Paste the id_rsa Key

## ************************************** Installing Packages **************************************

1) First, Lets setup Docker on our raspberryPi
      - Install Docker:  ``` curl -sSL https://get.docker.com | sh ```  
      - Add permission to User to run Docker Commands: ``` sudo usermod -aG docker [USER] ```  
      - Reboot the Pi for changes to take effect.
      - Next we need to install Python3 and Pip3 to install ``` docker-compose ```
      - run the following commands: 
      ```   sudo apt-get install python3-pip
            sudo apt-get install libffi-dev libssl-dev 
            sudo apt install python3-dev
            sudo apt-get install -y python3 python3-pip
            sudo pip3 install docker-compose
            sudo apt-get upgrade
      ```
2) Next, Lets create the directory structure for docker
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
                              - 5000:5000
      ```
      - lastly, create the ``` requirements.txt ``` file. It can be left empty for now.
      - build the docker container to apply an changes: ``` docker compose build ```
      - then run the docker container: ``` docker compose up ```
