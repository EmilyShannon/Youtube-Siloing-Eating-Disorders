import ast
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.model_selection import train_test_split
import tensorflow_hub as hub
import tensorflow_text as text
from keras import backend as K
from tensorflow import keras

#Load the CSV file with the reply text
dataset = pd.read_csv(f"{os.getcwd()}\\tumblrPostInfo\\thinspo-posts.csv")

#Three classes: pro-ed, pro-recovery, neutral
num_classes = 3

data = dataset.values
all_replies=[]
labels=[]
for post in data:

  #For unnecessary header lines
  if(post[0]=='tags'):
    continue
  else:
    #Should both come out as lists
    tags = ast.literal_eval(post[0])
    reply_texts = ast.literal_eval(post[1])
    
    #Skip posts with no reply text
    if(len(reply_texts)==0):
      continue
    
    else:

      #Neutral by default
      num = 2

      #These tags are just examples
      if('pro recovery' in tags):
        num=1
      elif ('ed' in tags):
        num=0
      else:
        num=2
      
      for reply in reply_texts:
        labels.append(num)
        all_replies.append(reply)

# print(labels)
# print(all_replies)


#This generates a matrix of 0's and 1's, where the 1's are in the index of the category that that reply is in
y = tf.keras.utils.to_categorical(labels, num_classes=num_classes)

#print(y)

#Make a set for training and another for testing 
x_train, x_test, y_train, y_test = train_test_split(all_replies, y, test_size=0.25)
# print(x_train)
# print(x_test)
# print(y_train)
# print(y_test)

#Try this to avoid value error
x_train = np.array(x_train)
x_test = np.array(x_test)


#Using a pretrained model to parse/encode the text
input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
preprocessor = hub.KerasLayer("https://tfhub.dev/google/universal-sentence-encoder-cmlm/multilingual-preprocess/2")
encoder = hub.KerasLayer("https://tfhub.dev/google/universal-sentence-encoder-cmlm/multilingual-base/1")


preprocessed_input = preprocessor(input)
endoded_input = encoder(preprocessed_input)

x = tf.keras.layers.Dropout(0.2, name="dropout")(encoded_input['pooled_output'])
x = tf.keras.layers.Dense(num_classes, activation='softmax', name="output")(x)

#The number of epochs determines the number of passes through the training set
n_epochs = 20
earlystop_callback = tf.keras.callbacks.EarlyStopping(monitor = "val_loss", 
                                                      patience = 3,
                                                      restore_best_weights = True)

#Create and compile the model
model = tf.keras.Model(input, x)
model.compile(optimizer = "adam", loss = "categorical_crossentropy")

#Train the model with our data
model_fit = model.fit(x_train, 
                      y_train, 
                      epochs = n_epochs,
                      validation_data = (x_test, y_test),
                      callbacks = [earlystop_callback])

#Samples to test the predictions the model makes
samples =  ['I wish I was skinny','I want to recover', 'I want you to recover. 🥺💛\nBut yeah, I can understand where you are coming from and it hurts.  \nJust please try to take care. 💛']


def predict_class(reviews):
  '''predict class of input text
  Args:
    - reviews (list of strings)
  Output:
    - class (list of int)
  '''
  return [np.argmax(pred) for pred in model.predict(reviews)]


print([x for x in predict_class(samples)])