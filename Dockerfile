FROM python:3.10-rc

RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache memory_profiler

