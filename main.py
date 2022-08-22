import subprocess, logging, shutil
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from tempfile import NamedTemporaryFile
from utils import *

api = FastAPI(
  title="ATRAC API"
)
logger = logging.getLogger("uvicorn.info")
@api.on_event("startup")
async def startup_event():
  api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )

@api.get("/")
async def root():
    return RedirectResponse("/docs")

@api.post('/encode')
def encode_atrac(type: atracTypes, background_tasks: BackgroundTasks, file: UploadFile = File()):
  global logger
  if type not in ['LP2', 'LP4']:
    raise HTTPException(status_code=400, detail="Invalid encoding type")
  filename = file.filename
  logger.info(f"Beginning encode for {filename}")
  with NamedTemporaryFile() as input, NamedTemporaryFile() as output:
    shutil.copyfileobj(file.file, input)
    encoder = subprocess.run(['/usr/bin/wine', 'psp_at3tool.exe', '-e', '-br', str(bitrates[type]), 
      Path(input.name), 
      Path(output.name)], capture_output=True)
    logger.info(encoder.stdout.decode())
    return FileResponse(path=output.name, filename=Path(filename).stem + '.at3')

@api.post('/decode')
def decode_atrac(background_tasks: BackgroundTasks, file: UploadFile = File()):
  global logger
  filename = file.filename
  logger.info(f"Beginning decode for {filename}")
  with NamedTemporaryFile() as input, NamedTemporaryFile as output:
    shutil.copyfileobj(file.file, input)
    encoder = subprocess.run(['/usr/bin/wine', 'psp_at3tool.exe', '-d', 
      Path(input.name), 
      Path(output.name)], capture_output=True)
    logger.info(encoder.stdout.decode())
    return FileResponse(path=output.name, filename=Path(filename).stem + '.wav')