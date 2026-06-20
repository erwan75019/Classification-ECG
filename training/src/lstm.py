import tensorflow as tf


def build_lstm(input_shape, learning_rate=1e-4, dropout_rate=0.5):
    inputs = tf.keras.layers.Input(shape=input_shape)

    x = tf.keras.layers.LSTM(64, return_sequences=True)(inputs)
    x = tf.keras.layers.BatchNormalization()(x)

    x = tf.keras.layers.LSTM(32)(x)
    x = tf.keras.layers.Dense(32, activation="relu")(x)
    x = tf.keras.layers.Dropout(dropout_rate)(x)

    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="LSTM")

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )

    return model
