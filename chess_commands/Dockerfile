FROM public.ecr.aws/lambda/python@sha256:ac758b6345b677eb6e72c2cd0f71c182eca773da5db1e17835a4ffef46dbc997 as build

RUN pip install requests websocket-client chess

#COPY entrypoint.sh /
COPY main.py chrome.py ./
COPY commands ./commands
COPY crawlers ./crawlers
COPY eco_formatted.json ./
#ENV DISPLAY=:99
CMD [ "main.handler" ]
#ENTRYPOINT ["/entrypoint.sh"]