import os
from enum import Enum

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/uploads/')

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
