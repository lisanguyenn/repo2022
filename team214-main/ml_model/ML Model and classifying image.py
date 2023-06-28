# Import more libraries to do ML 
import pathlib
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import PIL
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from glob import glob
from tensorflow.keras.layers.experimental.preprocessing import Rescaling
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, BatchNormalization, Conv2D, MaxPooling2D

# Defining the path for train and test images
train_path="db_path/Train/Pictures_and_tags"
test_path="db_path/Test/Pictures_and_tags"
data_dir_train = pathlib.Path(train_path)
data_dir_test = pathlib.Path(test_path)

image_count_train = len(list(data_dir_train.glob('*/*.jpg')))
print(image_count_train)
image_count_test = len(list(data_dir_test.glob('*/*.jpg')))
print(image_count_test)

# Use 80% of the images for training, and 20% for validation.
batch_size = 32
img_height = 180
img_width = 180

# Train Data Set Creation
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir_train, labels='inferred', label_mode='categorical',
    class_names=None, color_mode='rgb', batch_size=32, image_size=(180,
    180), shuffle=True, seed=123, validation_split=0.2, subset='training',
    interpolation='bilinear', follow_links=False, smart_resize=False
)

# 2.2 Validation Data Set Creation
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir_train, labels='inferred', label_mode='categorical',
    class_names=None, color_mode='rgb', batch_size=32, image_size=(180,
    180), shuffle=True, seed=123, validation_split=0.2, subset='validation',
    interpolation='bilinear', follow_links=False, smart_resize=False
)

#3.1 Creating the model
model=Sequential([
    tf.keras.layers.experimental.preprocessing.Rescaling(scale=1./255., offset=0.0,),         
    
    Conv2D(32,(3,3),input_shape=(img_height,img_width,3),activation='relu',padding='same'),
    MaxPooling2D(pool_size=(2,2)),
    Dropout(0.1),
    
    Conv2D(64,(3,3),activation='relu',padding='same'),
    MaxPooling2D(pool_size=(2,2)),
    Dropout(0.1),
    
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.25),   
    Dense(9, activation='softmax')
])

#3.2 Compiling the model
### Todo, choose an appropirate optimiser and loss function
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# 3.3 Training the model
epochs = 20
history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs
)
# View the summary of all layers
model.summary()

#Insert ML model to the database
model.insertToDB()

labels = ['Acne / Rosacea',
                  'Actinic Keratosis / Basal Cell Carcinoma', 
                  'Atopic Dermatitis', 'Bullous Disease', 
                  'Cellulitis Impetigo (Bacterial Infections)', 
                  'Eczema', 'Exanthems (Drug Eruptions)', 'Hair Loss (Alopecia)', 
                  'Herpes HPV', 'Disorders of Pigmentation', 
                  'Lupus ',
                  'Melanoma (Skin Cancer)', 'Nail Fungus', 
                  'Poison Ivy', 
                  'Psoriasis (Lichen Planus)', 'Scabies Lyme', 
                  'Seborrheic Keratoses', 'Systemic Disease', 
                  'Tinea Ringworm (Fungal Infections)', 
                  'Urticaria Hives', 'Vascular Tumors', 'Vasculitis', 'Warts Molluscum']

def classify_image(user_photo):
  user_photo = user_photo.reshape((-1, 224, 224, 3))
  prediction = model.predict(user_photo).flatten()
  confidences = {labels[i]: float(prediction[i]) for i in range(23)}
  return confidences

def result(model_confidences):
    return max(model_confidences)

result(classify_image(user_picture_taken_on_app))