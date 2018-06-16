import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'gaime-competition/Players'
ALLOWED_EXTENSIONS = set(['py', 'txt'])

def allowed_file(filename):
     return '.' in filename and \
            filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(app):
     if request.method == 'POST':
          if 'file' not in request.files:
               flash('No file part')
               return redirect(url_for('upload_page'))
          file = request.files['file']
          if file.filename == '':
               flash('No selected file')
               return redirect(url_for('index'))
          if file and not allowed_file(file.filename):
               flash('Please upload an approved file type!')
               return redirect(url_for('upload_page'))
          if file and allowed_file(file.filename):
               filename = secure_filename(file.filename)
               file.save(os.path.join(UPLOAD_FOLDER, filename))
               file.save(filename)
               flash('File successfully uploaded!')
               return redirect(url_for('index'))

     return render_template('upload.html')
