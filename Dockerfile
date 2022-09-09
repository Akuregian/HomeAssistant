FROM python:3

WORKDIR /home/HomeAssistant

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/home/HomeAssistant/app/RaspberryPi_GPIO"

COPY . .

CMD ["python", "./app/run.py"]


