from flask import Flask, render_template, request, redirect, Response
from werkzeug.utils import secure_filename
import os
import tensorflow as tf
from tensorflow import keras
import cv2
import numpy as np

app = Flask(__name__)
uploaded = False
pne = False
# load in tensorflow model
new_model = tf.keras.models.load_model('xray_model')

def process_data(img_path):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (196, 196))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img/255.0
    img = np.reshape(img, (196,196,1))
    return img

@app.route("/", methods=["POST", "GET"])
def index():
    # if it's a post request, we add the image to the folder
    if request.method == "POST":
        # We store the image from the html form in this pic variable
        pic = request.files['pic']
        if not pic:
            return 'No pic uploaded!', 400
        # get the name of the image which is uploaded
        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype
        if not filename or not mimetype:
            return 'Bad upload!', 400
        image_path = "./static/images/image.png"
        pic.save(image_path)
        global uploaded
        global pne
        # we change the uploaded boolean to true so the html page wont't show the upload button anymore
        uploaded = True
        # process image and convert it into the numpy array
        data = []
        data.append(process_data(image_path))
        img = np.array(data)
        # Make prediction
        y_val_hat = new_model.predict(img, batch_size=1)
        y_val_hat = np.argmax(y_val_hat, axis=1)
        # 1 means pneumonia, 0 means healthy
        if (y_val_hat == [0]):
            pne = False
        else:
            pne = True
        return render_template("index.html", uploaded=uploaded, pne=pne)
    else:
        return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)
