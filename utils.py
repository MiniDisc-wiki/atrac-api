import os, shutil, subprocess
from enum import Enum
from tempfile import gettempdir, NamedTemporaryFile
from pathlib import Path
from uuid import uuid4


class atracTypes(str, Enum):
  LP2 = 'LP2'
  LP4 = 'LP4'

bitrates = {
  'LP2': 132,
  'LP4': 66
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['wav', 'at3']


def remove_file(filename, logger): 
  os.remove(filename)
  logger.info(f"Removed {filename}")


def do_encode(input, type, logger):
  output = Path(gettempdir(), str(uuid4())).absolute()
  encoder = subprocess.run(['/usr/bin/wine', 'psp_at3tool.exe', '-e', '-br', str(bitrates[type]), 
    input, 
    output], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  logger.info(encoder.stdout.decode('utf-8', errors='ignore'))
  return output
