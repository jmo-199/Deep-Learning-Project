# -*- coding: utf-8 -*-
"""Combined Image Model with confusion matrix.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1l1Q6Vh6ws_U8ne200wxqv7IN4q1jfJe-
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np
import os, librosa
import librosa.display
import numpy as np
from tqdm import tqdm
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.datasets import fetch_lfw_people
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
import tensorflow_hub as hub
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Activation, Conv2D, MaxPooling2D, AveragePooling2D, Flatten, Dropout, BatchNormalization, Concatenate
from tensorflow.keras.optimizers import SGD, RMSprop, Adam
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from skimage.transform import resize
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import GlobalAveragePooling2D
np.random.seed(42)
tf.random.set_seed(42)

df1 = pd.read_csv('/content/drive/MyDrive/features_3_sec.csv')

def audio_file_to_spectrogram(file_path, target_shape=(128, 128)):
    try:
        y, sr = librosa.load(file_path, sr=None)  # Load file with its original sample rate
        # Use keyword arguments for melspectrogram
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=512)
        S_dB = librosa.power_to_db(S, ref=np.max)
        # Resize spectrogram to target shape
        S_resized = resize(S_dB, target_shape, mode='constant', anti_aliasing=True)
        return S_resized[:, :, np.newaxis]  # Add channel dimension
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return None

import random
def load_data_sample(base_dir, sample_size=100, target_shape=(128, 128)):
    X, y = [], []
    genre_paths = [os.path.join(base_dir, genre) for genre in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, genre))]

    for genre_path in genre_paths:
        files = [f for f in os.listdir(genre_path) if f.endswith('.wav')]
        sampled_files = random.sample(files, min(len(files), sample_size))

        for file in sampled_files:
            file_path = os.path.join(genre_path, file)
            spectrogram = audio_file_to_spectrogram(file_path, target_shape)
            if spectrogram is not None:
                X.append(spectrogram)
                y.append(os.path.basename(genre_path))

    return np.array(X), np.array(y)

def prepare_labels(y):
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    return to_categorical(y_encoded)

def split_data(X, y, test_size=0.2):
    return train_test_split(X, y, test_size=test_size, random_state=42)

from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

# Encode genre labels
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(df1['label'])  # 'label' is the column with genre labels
y = to_categorical(encoded_labels)

def resnet(input):
    x11 = Conv2D(64, (1, 1), padding='same', strides=1)(input)
    x12 = Activation('relu')(x11)
    x13 = Concatenate()([x12, input])
    x14 = Conv2D(64, (3, 3), padding='same', strides=1)(x13)
    x15 = Activation('relu')(x14)
    x16 = Concatenate()([x15, input])
    x17 = Conv2D(64, (1, 1), padding='same', strides=1)(x16)
    x18 = Activation('relu')(x17)
    x19 = Concatenate()([x18, input])
    x20 = Conv2D(64, (3, 3), padding='same', strides=1)(x19)
    x21 = Activation('relu')(x20)
    x22 = Concatenate()([x21, input])
    x23 = Conv2D(64, (3, 3), padding='same', strides=1)(x22)
    x24 = Activation('relu')(x23)
    x25 = Conv2D(64, (3, 3), padding='same', strides=1)(input)
    x26 = Activation('relu')(x25)
    x27 = Concatenate()([x26, input])
    x28 = Conv2D(64, (1, 1), padding='same', strides=1)(x27)
    x29 = Activation('relu')(x28)
    x30 = Concatenate()([x29, input])
    x31 = Conv2D(64, (3, 3), padding='same', strides=1)(x30)
    x32 = Activation('relu')(x31)
    x33 = Concatenate()([x32, input])
    x34 = Conv2D(64, (1, 1), padding='same', strides=1)(x33)
    x35 = Activation('relu')(x34)
    x36 = Concatenate()([x35, input, x24])
    x37 = MaxPooling2D(pool_size=2)(x36)
    return x37

def create_cnn_model(input_shape, num_classes):
    inputs = Input(input_shape)
    x08 = Conv2D(64, (1, 1), padding='same', strides=1)(inputs)
    x09 = Activation('relu')(x08)
    x10 = resnet(inputs)
    x11 = resnet(x10)
    x12 = resnet(x11)
    x13 = resnet(x12)
    x14 = resnet(x13)
    x15 = resnet(x14)
    x16 = resnet(x15)
    x = Flatten(name='flatten')(x16)
    x = Dense(256, activation='relu', name='fc1')(x)
    x = Dense(256, activation='relu', name='fc2')(x)
    x = Dense(num_classes, activation='softmax', name='predictions')(x)
    model = Model(inputs, x)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def create_new_model(input_shape, num_classes):
    model = Sequential([
        Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=input_shape),
        MaxPooling2D(2, 2),

        Conv2D(64, (3, 3), padding='same', activation='relu'),
        MaxPooling2D(2, 2),

        Conv2D(128, (3, 3), padding='same', activation='relu'),
        MaxPooling2D(2, 2),

        Conv2D(256, (3, 3), padding='same', activation='relu'),
        MaxPooling2D(2, 2),

        Conv2D(512, (3, 3), padding='same', activation='relu'),
        MaxPooling2D(2, 2),

        Conv2D(1024, (3, 3), padding='same', activation='relu'),
        MaxPooling2D(2, 2),

        Conv2D(2048, (3, 3), padding='same', activation='relu'),
        MaxPooling2D(2, 2),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

base_dir = '/content/drive/MyDrive/genres_original'
X_image, y_image = load_data_sample(base_dir)
y_categorical = prepare_labels(y_image)
X_train_image, X_test_image, y_train_image, y_test_image = split_data(X_image, y_categorical)

print(X_train_image.shape)
print(X_test_image.shape)
print(y_train_image.shape)
print(y_test_image.shape)

def train_model(X_train, y_train):
    model = create_cnn_model((128, 128, 1), y_train.shape[1])
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)
    return model

def train_model_2(X_train, y_train):
    model = create_new_model((128, 128, 1), y_train.shape[1])
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)
    return model

history_1 = train_model(X_train_image, y_train_image)

history_2 = train_model_2(X_train_image, y_train_image)

meta_1 = history_1.predict(X_train_image)
meta_2 = history_2.predict(X_train_image)

# Slice meta_2 to match the shape of meta_1
meta_2 = meta_2[:meta_1.shape[0]]

csv_input = Input(shape=(meta_2.shape[1],))
image_input = Input(shape=meta_1.shape[1:])

# Concatenate the outputs of both models
combined_input = Concatenate()([csv_input, image_input])

combined_output = Dense(256, activation='relu')(combined_input)
combined_output = Dense(128, activation='relu')(combined_output)
combined_output = Dense(64, activation='relu')(combined_output)
combined_output = Dense(32, activation='relu')(combined_output)
combined_output = Dense(10, activation='relu')(combined_output)

# Create the combined model
combined_model = Model(inputs=[csv_input, image_input], outputs=combined_output)

# Compile the combined model
combined_model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])

y_train_image = y_train_image[:meta_1.shape[0]]

# Train the combined model using both sets of inputs
history_3 = combined_model.fit([meta_1, meta_2], y_train_image, epochs=50, batch_size=32, validation_split=0.2)

new_1 = history_1.predict(X_test_image)
new_2 = history_2.predict(X_test_image)
new_2 = new_2[:new_1.shape[0]]

test_loss, test_acc = combined_model.evaluate([new_1, new_2], y_test_image, verbose=2)
print(f'Test accuracy: {test_acc:.4f}, Test loss: {test_loss:.4f}')

# Visualization of training history
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history_3.history['accuracy'], label='Train Accuracy')
plt.plot(history_3.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='upper left')

plt.subplot(1, 2, 2)
plt.plot(history_3.history['loss'], label='Train Loss')
plt.plot(history_3.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper left')

plt.show()

y_pred = combined_model.predict([new_1, new_2])
y_pred = np.argmax(y_pred, axis=1)
#y_test_image = np.argmax(y_test_image, axis=1)
conf_mat_1 = confusion_matrix(y_test_image, y_pred)

plt.figure(figsize=(8, 6))
sns.set(font_scale=1.2)  # Adjust font size
sns.heatmap(conf_mat_1, annot=True, fmt='d', cmap='YlGnBu', cbar=False, square=True)

# Customize labels, title, and axis ticks
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.xticks(rotation=45)
plt.tight_layout()

# Show plot
plt.show()