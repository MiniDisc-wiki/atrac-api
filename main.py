from flask import Flask, request, after_this_request, Response, send_from_directory
import os, subprocess, signal, sys
from werkzeug.utils import secure_filename
from pathlib import Path
from flask_cors import CORS

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/uploads/')

api = Flask(__name__)
CORS(api)
api.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['wav', 'at3']

bitrates = {
  'LP2': 132,
  'LP4': 66
}

@api.route('/encode', methods=['POST'])
def encode_atrac():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
          return 'No file', 400
        file = request.files['file']
        type = request.args.get('type')
        if type not in ['LP2', 'LP4']:
          return 'Invalid encoding type', 400
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return 'No file', 400
        if file and allowed_file(file.filename):
            @after_this_request 
            def remove_file(response): 
                api.logger.info(f"Successfully encoded {Path(filename).stem}.at3")
                os.remove(os.path.join(api.config['UPLOAD_FOLDER'], filename))
                os.remove(os.path.join(api.config['UPLOAD_FOLDER'], Path(filename).stem) + '.at3')
                return response 
            filename = secure_filename(file.filename)
            api.logger.info(f"Beginning encode for {filename}")
            file.save(os.path.join(api.config['UPLOAD_FOLDER'], filename))
            encoder = subprocess.run(['/usr/bin/wine', 'psp_at3tool.exe', '-e', '-br', str(bitrates[type]), 
              os.path.join(api.config['UPLOAD_FOLDER'], filename), 
              os.path.join(api.config['UPLOAD_FOLDER'], Path(filename).stem) + '.at3'], capture_output=True)
            return send_from_directory(directory=api.config['UPLOAD_FOLDER'], path=Path(filename).stem + '.at3')


@api.route('/decode', methods=['POST'])
def decode_atrac():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
          return 'No file', 400
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return 'No file', 400
        if file and allowed_file(file.filename):
            @after_this_request 
            def remove_file(response): 
                os.remove(os.path.join(api.config['UPLOAD_FOLDER'], filename)) 
                os.remove(os.path.join(api.config['UPLOAD_FOLDER'], filename) + '.wav')
                return response 
            filename = secure_filename(file.filename)
            file.save(os.path.join(api.config['UPLOAD_FOLDER'], filename))
            encoder = subprocess.run(['/usr/bin/wine', 'psp_at3tool.exe', '-d',
              os.path.join(api.config['UPLOAD_FOLDER'], filename), 
              os.path.join(api.config['UPLOAD_FOLDER'], filename) + '.wav'], capture_output=True)
            return send_from_directory(directory=api.config['UPLOAD_FOLDER'], path=filename + '.wav')

if __name__ == '__main__':
  def signal_handler(sig, frame):
      print('SIGINT received, shutting down')
      sys.exit(0)
  signal.signal(signal.SIGINT, signal_handler)
  api.run(host="0.0.0.0") 