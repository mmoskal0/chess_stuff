FROM public.ecr.aws/lambda/python@sha256:ac758b6345b677eb6e72c2cd0f71c182eca773da5db1e17835a4ffef46dbc997 as build

RUN pip install requests websocket-client chess

COPY commands ./commands
COPY crawlers ./crawlers
COPY eco_formatted.json ./
CMD [ "main.handler" ]