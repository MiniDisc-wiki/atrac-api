FROM python:3.11-slim AS ffmpeg-builder
WORKDIR /root
ENV ARCH=x86_64
RUN apt-get update && apt-get install -y yasm git curl lbzip2 build-essential
RUN git clone https://github.com/acoustid/ffmpeg-build.git
RUN echo "FFMPEG_CONFIGURE_FLAGS+=(--enable-encoder=pcm_s16le --enable-muxer=wav --enable-filter=loudnorm --enable-filter=aresample --enable-filter=replaygain --enable-filter=volume --enable-filter=atrim)" >> ffmpeg-build/common.sh
RUN ffmpeg-build/build-linux.sh
RUN mv ffmpeg-build/artifacts/ffmpeg-*-linux-gnu/bin/ffmpeg .

FROM python:3.11-slim AS encoder-buider
WORKDIR /root
RUN dpkg --add-architecture i386
RUN apt-get update
RUN apt-get install -y libc6:i386 libc6-dev:i386 git bsdextrautils nasm binutils
RUN git clone https://github.com/asivery/atrac3-encoder-linux.git
WORKDIR /root/atrac3-encoder-linux
COPY psp_at3tool.exe .
RUN bash ./convert.sh

FROM python:3.11-slim
COPY --from=ffmpeg-builder /root/ffmpeg /usr/bin/ffmpeg
COPY --from=encoder-buider /root/atrac3-encoder-linux/psp_at3tool.exe.elf /usr/bin/at3tool
RUN chmod +x /usr/bin/at3tool
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir /uploads
COPY *.py ./

EXPOSE 5000
ENTRYPOINT ["uvicorn"]
CMD ["main:api", "--host", "0.0.0.0", "--port", "5000"]
