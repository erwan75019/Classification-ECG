import matplotlib.pyplot as plt
import os


def plot_learning_curves(history, model_name):
    os.makedirs("../graphs", exist_ok=True)

    plt.figure(figsize=(10, 4))

    # Loss
    plt.subplot(1, 2, 1)
    plt.plot(history.history["loss"], "b", label="train_loss")
    plt.plot(history.history["val_loss"], "r", label="val_loss")
    plt.title("Loss")
    plt.xlabel("epoch")
    plt.ylabel("loss")
    plt.legend()

    # Accuracy
    plt.subplot(1, 2, 2)
    plt.plot(history.history["accuracy"], "b", label="train_accuracy")
    plt.plot(history.history["val_accuracy"], "r", label="val_accuracy")
    plt.title("Accuracy")
    plt.xlabel("epoch")
    plt.ylabel("accuracy")
    plt.legend()

    plt.tight_layout()
    plt.savefig(f"../graphs/{model_name.lower()}_learning.png")
    plt.close()


def plot_summary_table(summary, model_name):
    os.makedirs("../results/metrics", exist_ok=True)

    filepath = f"../results/metrics/{model_name}_summary.txt"

    with open(filepath, "w") as f:
        for key, value in summary.items():
            mean = value["mean"]
            std = value["std"]

            f.write(f"{key}: {mean:.4f} ± {std:.4f}\n")

