from keras.models import Sequential
from keras.layers import Dense

# Créez un modèle Keras équivalent à votre modèle MLP
model_keras = Sequential()
model_keras.add(Dense(100, activation='relu', input_shape=(X_train.shape[1],)))
model_keras.add(Dense(100, activation='relu'))
model_keras.add(Dense(1))

# Compilez le modèle Keras
model_keras.compile(optimizer='adam', loss='mean_squared_error')

# Copiez les poids du modèle MLP dans le modèle Keras
model_keras.set_weights(model.coefs_)
