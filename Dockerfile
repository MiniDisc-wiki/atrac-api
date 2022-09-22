FROM python:slim

ENV WINEPREFIX="/wine32" 
ENV WINEARCH=win32 
ENV LOG_LEVEL=
RUN dpkg --add-architecture i386
RUN apt-get update
RUN apt-get install -y wine32 wine:i386 ffmpeg --no-install-recommends
RUN apt-get clean
RUN /usr/bin/wine wineboot | true
COPY psp_at3tool.exe .
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir /uploads
COPY *.py ./

EXPOSE 5000
ENTRYPOINT ["uvicorn"]
CMD ["main:api", "--host", "0.0.0.0", "--port", "5000"]
