import os
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    ConfusionMatrixDisplay,
)

from train import train_model
from plots import plot_learning_curves


def plot_roc_curve(y_test, y_proba, model_name):
    os.makedirs("../graphs", exist_ok=True)

    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc_score = roc_auc_score(y_test, y_proba)

    plt.figure(figsize=(6, 6))

    # Courbe ROC (bleu)
    plt.plot(fpr, tpr, "b", label=f"ROC (AUC = {auc_score:.2f})")

    # Diagonale (baseline)
    plt.plot([0, 1], [0, 1], "k--")

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC - {model_name}")
    plt.legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(f"../graphs/{model_name.lower()}_roc.png")
    plt.close()


def plot_confusion_matrix(y_test, y_pred, model_name):
    os.makedirs("../graphs", exist_ok=True)

    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Normal", "Infarctus"]
    )

    disp.plot(cmap="Blues", values_format="d")
    plt.title(f"Matrice de confusion - {model_name}")
    plt.tight_layout()
    plt.savefig(f"../graphs/{model_name.lower()}_confusion_matrix.png")
    plt.close()


def save_classification_report(y_test, y_pred, model_name):
    os.makedirs("../results/reports", exist_ok=True)

    report = classification_report(y_test, y_pred, zero_division=0)

    filepath = f"../results/reports/{model_name.lower()}_report.txt"

    with open(filepath, "w") as f:
        f.write(report)


def evaluate_model(model, X_test, y_test):
    start_time = time.perf_counter()
    y_proba = model.predict(X_test, verbose=0)
    inference_time = time.perf_counter() - start_time

    y_pred = (y_proba > 0.5).astype(int)

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    results = {
        "accuracy": report["accuracy"],
        "precision": report["1"]["precision"],
        "recall": report["1"]["recall"],
        "f1": report["1"]["f1-score"],
        "auc": roc_auc_score(y_test, y_proba),
        "inference_time": inference_time,
    }

    return results, y_proba, y_pred


def run_multiple_times(build_model_fn, X_train, y_train, X_test, y_test, n_runs=5):
    all_results = []
    best_f1 = -1.0
    best_model = None
    best_history = None
    best_y_proba = None
    best_y_pred = None

    for run in range(n_runs):
        print(f"Run {run+1}/{n_runs}")

        model = build_model_fn()
        history, train_time = train_model(model, X_train, y_train)

        results, y_proba, y_pred = evaluate_model(model, X_test, y_test)
        results["train_time"] = train_time

        all_results.append(results)

        if results["f1"] > best_f1:
            best_f1 = results["f1"]
            best_model = model
            best_history = history
            best_y_proba = y_proba
            best_y_pred = y_pred

    if best_model is not None:
        os.makedirs("../models", exist_ok=True)

        model_filename = f"{best_model.name.lower()}_ecg.keras"
        model_path = os.path.join("../models", model_filename)

        best_model.save(model_path)

        plot_learning_curves(best_history, best_model.name)
        plot_roc_curve(y_test, best_y_proba, best_model.name)
        plot_confusion_matrix(y_test, best_y_pred, best_model.name)
        save_classification_report(y_test, best_y_pred, best_model.name)

        print(f"Meilleur modèle sauvegardé : {model_path} avec F1 = {best_f1:.4f}")

    return all_results



def summarize_results(results_list):
    summary = {}

    for key in results_list[0].keys():
        values = [r[key] for r in results_list]

        summary[key] = {
            "mean": np.mean(values),
            "std": np.std(values),
        }

    return summary

