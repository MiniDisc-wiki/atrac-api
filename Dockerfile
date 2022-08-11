FROM python:slim

ENV WINEPREFIX="/wine32" 
ENV WINEARCH=win32 
RUN dpkg --add-architecture i386
RUN apt-get update
RUN apt-get install -y wine32 wine:i386 --no-install-recommends
RUN apt-get clean
RUN /usr/bin/wine wineboot | true
COPY psp_at3tool.exe .
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir /uploads
COPY main.py .

CMD python3 main.py
