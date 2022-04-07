from sklearn import metrics
from tensorflow import keras
from sklearn.metrics import classification_report, confusion_matrix

import tensorflow as tf
import logging
import numpy as np
import utils


def evaluate_model(model, dataset):
  # X = np.concatenate([X for X, y in val_ds], axis=0)  
  # y_true = np.concatenate([y for x, y in val_ds], axis=0)
  # cannot use this approach as it loads all the samples into memory, which 
  # gets exhausted very fast.
  
  y_true = []
  y_pred_cat = []
  count = 0
  for x, y in dataset:
    # Note that here x and y do not come one after another--they come in batches
    # whose size is defined by the batch_size parameter passed to the prepare_dataset
    # method.
    count += 1
    logging.info(f'Predicting {count}-th sample')
    y_true.extend(y.numpy().tolist())
    y_pred = model.predict(x).ravel()
    y_pred_cat.extend(np.where(y_pred > 0.5, 1, 0).tolist())

  print(y_pred_cat)
  print(y_true)
  cm = metrics.confusion_matrix(y_true, y_pred_cat)
  print(cm)
  print(classification_report(y_true, y_pred_cat, target_names=['0','1']))

  print(model.evaluate(dataset, verbose=1))
  return


settings = utils.read_config_file()
image_size = (
  settings['dataset']['image']['height'], settings['dataset']['image']['width']
)
batch_size = settings['model']['batch_size']
  
utils.initialize_logger(settings['misc']['log_path'])
train_ds, val_ds = utils.prepare_dataset(image_size=image_size, batch_size=batch_size)
model = keras.models.load_model(settings['model']['save_to']['model'])

evaluate_model(model=model, dataset=val_ds)
evaluate_model(model=model, dataset=train_ds)
