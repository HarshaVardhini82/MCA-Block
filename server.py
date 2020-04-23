import os
import urllib.request
import ipfshttpclient
from my_constants import app
from flask import Flask, flash, request, redirect, render_template, url_for, jsonify
from werkzeug.utils import secure_filename
from blockchain import Blockchain
import requests as request_file_hash

                # This package is used in the 'hashed' function while getting the hash of the file.
                # Notice that this package , 'requests' is different than the package 'request'.
                # 'request' package is used in the 'add_file' function for multiple actions.

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

blockchain = Blockchain()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hashed(filename):
    url = 'https://ipfs.infura.io:5001/api/v0/add'
    user_file = { 'file' : (filename), }
    response = request_file_hash.post(url, files = user_file)
    #print(p['Hash'])
    # client = ipfshttpclient.connect('/dns/ipfs.infura.io/tcp/5001/https')
    # result = client.add(filename)
    hashed_file = response.json()['Hash']
    return  hashed_file

def retrieve_from_hash(file_hash):
    url = 'https://ipfs.infura.io:5001/api/v0/block/get'
    response = request_file_hash.post(url, key = file_hash)
    print(response)
    user_file = response
    return user_file

@app.route('/')
def home():
    return render_template('first.html')

@app.route('/add_file', methods=['POST'])
def add_file():
    if request.method == 'POST':

        error_flag = True

        # check if the post request has the file part
        if 'file' not in request.files:
            message = 'No file part'
        else:
            file = request.files['file']
            if file.filename == '':
                message = 'No file selected for uploading'

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                message = 'File successfully uploaded'
                #file_hash = 'ABDEFgh'
                hashed_output1 = hashed(filename)
                sender = request.form['sender_name']
                receiver = request.form['receiver_name']
                index = blockchain.add_file(sender, receiver, hashed_output1)
                message = f'This file will be added to Block {index}'
                error_flag = False
            else:
                message = 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'

        chain = blockchain.chain
        response = {'message': message, 'blockchain': chain}

        if error_flag == True:
            return render_template('first.html', messages = response)
        else:
            return render_template('second.html',messages = response)

@app.route('/retrieve_file', methods=['POST'])
def retrieve_file():
    if request.method == 'POST':

        message = ''
        error_flag = True

        if request.form['file_hash'] == '':
            message = 'No hash entered'
        if len(request.form['file_hash']) != 64:
            message = 'Incorrect hash'
        else:
            error_flag = False
            file_hash = request.form['file_hash']
            user_file = retrieve_from_hash(file_hash)
            print(user_file)

        if error_flag == True:
            return render_template('first.html', messages = {'message' : message})
        else:
            return render_template('second.html',messages = {'message' : message})



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)