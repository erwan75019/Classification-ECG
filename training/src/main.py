import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf
tf.get_logger().setLevel("ERROR")

from data import load_data, reshape_for_sequence_models
from evaluate import run_multiple_times, summarize_results
from plots import plot_summary_table

from mlp import build_mlp
from cnn import build_cnn
from lstm import build_lstm
from gru import build_gru


def save_global_comparison(mlp_summary, cnn_summary, lstm_summary):
    import os
    os.makedirs("../results/metrics", exist_ok=True)

    filepath = "../results/metrics/global_comparison.txt"

    with open(filepath, "w") as f:
        f.write("MODEL COMPARISON\n\n")

        models = {
            "MLP": mlp_summary,
            "CNN": cnn_summary,
            "LSTM": lstm_summary,
        }

        for model_name, summary in models.items():
            f.write(f"=== {model_name} ===\n")
            for key, value in summary.items():
                f.write(f"{key}: {value['mean']:.4f} ± {value['std']:.4f}\n")
            f.write("\n")


def main():
    X_train, X_test, y_train, y_test = load_data()

    
    
    # MLP
    print("\n===== MLP =====")

    model = build_mlp(X_train.shape[1:])
    model.summary()

    mlp_results = run_multiple_times(
        lambda: build_mlp(X_train.shape[1:]),
        X_train,
        y_train,
        X_test,
        y_test,
    )
    mlp_summary = summarize_results(mlp_results)
    plot_summary_table(mlp_summary, "mlp")

    
    
    # CNN
    print("\n===== CNN =====")
    X_train_seq = reshape_for_sequence_models(X_train)
    X_test_seq = reshape_for_sequence_models(X_test)

    model = build_cnn(X_train_seq.shape[1:])
    model.summary()

    cnn_results = run_multiple_times(
        lambda: build_cnn(X_train_seq.shape[1:]),
        X_train_seq,
        y_train,
        X_test_seq,
        y_test,
    )
    cnn_summary = summarize_results(cnn_results)
    plot_summary_table(cnn_summary, "cnn")

    
    
    # LSTM
    print("\n===== LSTM =====")

    model = build_lstm(X_train_seq.shape[1:])
    model.summary()

    lstm_results = run_multiple_times(
        lambda: build_lstm(X_train_seq.shape[1:]),
        X_train_seq,
        y_train,
        X_test_seq,
        y_test,
    )
    lstm_summary = summarize_results(lstm_results)
    plot_summary_table(lstm_summary, "lstm")

    
    
    # GRU
    print("\n===== GRU =====")

    model = build_gru(X_train_seq.shape[1:])
    model.summary()

    gru_results = run_multiple_times(
        lambda: build_gru(X_train_seq.shape[1:]),
        X_train_seq,
        y_train,
        X_test_seq,
        y_test,
    )
    gru_summary = summarize_results(gru_results)
    plot_summary_table(gru_summary, "gru")

    
    
    # Global comparison
    save_global_comparison(mlp_summary, cnn_summary, lstm_summary)

    print("\nTerminé. Les résultats ont été enregistrés dans training/results/metrics et training/graphs.")


if __name__ == "__main__":
    main()