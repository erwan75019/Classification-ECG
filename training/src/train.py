import time
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau


def train_model(model, X_train, y_train, epochs=200, batch_size=32):
    
    # Calcul des class weights
    weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(y_train),
        y=y_train
    )
    class_weight_dict = dict(zip(np.unique(y_train), weights))

    # Callbacks
    early_stop = EarlyStopping(
        monitor="val_loss",
        patience=30,
        restore_best_weights=True
    )

    reduce_lr = ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=10,
        min_lr=1e-6,
        verbose=1
    )

    # Temps d'entraînement 
    start_time = time.perf_counter()

    history = model.fit(
        X_train,
        y_train,
        validation_split=0.2,
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[early_stop, reduce_lr],
        class_weight=class_weight_dict,
        verbose=1
    )

    training_time = time.perf_counter() - start_time

    return history, training_time
