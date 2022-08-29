FROM python:3

WORKDIR /home/HomeAssistant

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/home/HomeAssistant/app/RaspberryPi_GPIO"

COPY . .

CMD ["python3", "-m webbrowser -t 'http://192.168.1.250:5001/'"]

CMD ["python", "./app/run.py"]


