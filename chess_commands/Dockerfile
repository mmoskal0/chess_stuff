FROM public.ecr.aws/lambda/python:3.11

RUN pip install requests websocket-client chess emoji-country-flag

COPY main.py ./
COPY commands ./commands
COPY crawlers ./crawlers
COPY eco_formatted.json ./
CMD [ "main.handler" ]