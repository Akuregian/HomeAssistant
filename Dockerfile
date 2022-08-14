FROM python:3

WORKDIR /home/HomeAutomation

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["./Wireless_Arduino_Communication/Sender.cpp"]
CMD ["python", "./run.py"]

