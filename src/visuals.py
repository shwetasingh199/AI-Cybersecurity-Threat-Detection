import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np

def confusion_matrix_figure(y_true, y_pred, labels):
    fig, ax = plt.subplots(figsize=(7, 5))
    cm = confusion_matrix(y_true, y_pred, labels=np.arange(len(labels)))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels, ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix")
    fig.tight_layout()
    return fig
