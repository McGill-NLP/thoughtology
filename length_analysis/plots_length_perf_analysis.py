import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import math
import pdb

def analyze_predictions(file_path, num_bins=10):
    # Load TSV
    df = pd.read_csv(file_path, sep="\t")

    # Bin rows based on Tokens
    df["TokenBin"], bins = pd.qcut(df["Tokens"], q=num_bins, retbins=True, labels=False, duplicates="drop")
    bin_centers = [(bins[i] + bins[i+1]) / 2 for i in range(len(bins) - 1)]

    # Prepare containers for plotting
    avg_accuracy_per_bin = []
    ids_per_bin = []
    rows_per_bin = []

    for b in sorted(df["TokenBin"].dropna().unique()):
        bin_df = df[df["TokenBin"] == b]
        rows_per_bin.append(len(bin_df))

        # Compute per-ID accuracy *within the bin*
        per_id_accuracy = bin_df.groupby("ID")["Result"].mean()
        avg_accuracy = per_id_accuracy.mean()
        avg_accuracy_per_bin.append(avg_accuracy)

        ids_per_bin.append(per_id_accuracy.shape[0])

    # Plot 1: Average Accuracy vs Token Bin
    plt.figure(figsize=(8, 5))
    sns.lineplot(x=bin_centers, y=avg_accuracy_per_bin, marker="o")
    plt.xlabel("Token Bin (center)")
    plt.ylabel("Average Per-ID Accuracy")
    plt.title("Average Accuracy vs Token Count")
    plt.grid(True)
    plt.savefig("plots/accuracy_vs_tokens.png")
    plt.close()

    # Plot 2: Number of IDs and Total Rows per Bin
    plt.figure(figsize=(8, 5))
    sns.lineplot(x=bin_centers, y=ids_per_bin, marker="o", label="Unique IDs")
    sns.lineplot(x=bin_centers, y=rows_per_bin, marker="s", label="Total Rows")
    plt.xlabel("Token Bin (center)")
    plt.ylabel("Count")
    plt.title("Representation per Token Bin")
    plt.legend()
    plt.grid(True)
    plt.savefig("plots/counts_vs_tokens.png")
    plt.close()

    print("Saved plots:")
    print("accuracy_vs_tokens.png")
    print("counts_vs_tokens.png")


def format_xticks(x, _):
    return f"{int(x/1000)}k" if x >= 1000 else str(int(x))


def format_yticks(y, _):
    return f"{int(y * 100)}"

def plot_per_id_accuracy_by_token_bin_all(file_path, num_bins=10):
    # Load data
    df = pd.read_csv(file_path, sep="\t")

    manual_keep = [19, 27, 16]
    name_maps = {
        19: "II-10",
        27: "II-8",
        16: "I-13"
    }
    
    final_ids_to_keep = manual_keep

    final_ids_to_keep = df["ID"].unique()

    # Plotting setup
    num_ids = len(final_ids_to_keep)
    cols = 5
    rows = math.ceil(num_ids / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
    plt.subplots_adjust(
        wspace=0.03     # spacing between subplots
    )
    axes = axes.flatten()

    for i, uid in enumerate(final_ids_to_keep):
        sub_df = df[df["ID"] == uid]

        sub_df["TokenBin"], bins = pd.qcut(sub_df["Tokens"], q=num_bins, retbins=True, labels=False, duplicates="drop")
        bin_centers = [(bins[i] + bins[i+1]) / 2 for i in range(len(bins) - 1)]

        # Define a base color and create a gradient for shading
        base_color = "lightpink"
        alphas = np.linspace(0.1, 0.5, len(bins) - 1)  # Gradually increasing alpha

        grouped = sub_df.groupby(["TokenBin"]).agg(
            Accuracy=("Result", "mean"),
            RowCount=("Result", "count")
        ).reset_index()
        
        ax = axes[i]
        bin_x = [bin_centers[int(b)] for b in grouped["TokenBin"]]
        
        # Add vertical dashed lines for bin separators
        for b in bins:
            ax.axvline(b, color="gray", linestyle="dashed", linewidth=1, alpha=0.6)

        # Shade each bin with increasing transparency
        for j in range(len(bins) - 1):
            ax.axvspan(bins[j], bins[j+1], color=base_color, alpha=alphas[j])

        ax.plot(bin_x, grouped["Accuracy"], marker="o", markersize=8, linewidth=3, label=f"ID {uid}")

        ax.set_title(f"Problem: {uid}", fontsize=20, pad=10)
        ax.set_xlabel("Number of Tokens", fontsize=16)
        ax.xaxis.set_major_formatter(FuncFormatter(format_xticks))
        ax.yaxis.set_major_formatter(FuncFormatter(format_yticks))
        ax.grid(True, axis='y', linestyle='--', alpha=0.2)
        ax.set_ylim(-0.05, 1.05)
        if i % cols != 0:
            ax.set_yticklabels([])
            ax.yaxis.set_ticks_position('none')
        else:
            ax.set_ylabel("Accuracy (%)", fontsize=16)

    # Hide any unused subplots
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle("AIME-24 Accuracy vs (binned) Length of Thoughts", fontsize=20, y=0.95)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig("plots/per_id_accuracy_all.png")
    plt.savefig("plots/per_id_accuracy_all.pdf")
    plt.close()

    print(f"Saved plot: per_id_accuracy.png")


def plot_per_id_accuracy_by_token_bin(file_path, num_bins=10):
    # Load data
    df = pd.read_csv(file_path, sep="\t")

    manual_keep = [19, 27, 16]
    name_maps = {
        19: "II-10",
        27: "II-8",
        16: "I-13"
    }

    final_ids_to_keep = manual_keep

    # Plotting setup
    num_ids = len(final_ids_to_keep)
    cols = 3
    rows = math.ceil(num_ids / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4), sharex=True)
    plt.subplots_adjust(
        wspace=0.03     # spacing between subplots
    )
    axes = axes.flatten()

    for i, uid in enumerate(final_ids_to_keep):
        sub_df = df[df["ID"] == uid]

        sub_df["TokenBin"], bins = pd.qcut(sub_df["Tokens"], q=num_bins, retbins=True, labels=False, duplicates="drop")
        bin_centers = [(bins[i] + bins[i+1]) / 2 for i in range(len(bins) - 1)]

        # Define a base color and create a gradient for shading
        base_color = "lightpink"
        alphas = np.linspace(0.1, 0.5, len(bins) - 1)  # Gradually increasing alpha

        grouped = sub_df.groupby(["TokenBin"]).agg(
            Accuracy=("Result", "mean"),
            RowCount=("Result", "count")
        ).reset_index()
        
        ax = axes[i]
        bin_x = [bin_centers[int(b)] for b in grouped["TokenBin"]]
        
        # Add vertical dashed lines for bin separators
        for b in bins:
            ax.axvline(b, color="gray", linestyle="dashed", linewidth=1, alpha=0.6)

        # Shade each bin with increasing transparency
        for j in range(len(bins) - 1):
            ax.axvspan(bins[j], bins[j+1], color=base_color, alpha=alphas[j])

        ax.plot(bin_x, grouped["Accuracy"], marker="o", markersize=8, linewidth=3, label=f"ID {uid}")

        ax.set_title(f"Problem ID: {name_maps[uid]}", fontsize=16, pad=10)
        ax.set_xlabel("Number of Tokens", fontsize=16)
        ax.xaxis.set_major_formatter(FuncFormatter(format_xticks))
        ax.yaxis.set_major_formatter(FuncFormatter(format_yticks))
        ax.grid(True, axis='y', linestyle='--', alpha=0.2)
        ax.set_ylim(-0.05, 1.05)
        if i % cols != 0:
            ax.set_yticklabels([])
            ax.yaxis.set_ticks_position('none')
        else:
            ax.set_ylabel("Accuracy (%)", fontsize=16)

    # Hide any unused subplots
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle("AIME-24 Accuracy vs (binned) Length of Thoughts", fontsize=18, y=0.9)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig("plots/per_id_accuracy.png")
    plt.savefig("plots/per_id_accuracy.pdf")
    plt.close()

    print(f"Saved plot: per_id_accuracy.png")


def plot_normalized_token_accuracy(file_path, num_bins=10):
    # Load data
    df = pd.read_csv(file_path, sep="\t")

    # Normalize Tokens per ID
    def normalize_tokens(group):
        min_tok = group["Tokens"].min()
        max_tok = group["Tokens"].max()
        group["NormalizedToken"] = (group["Tokens"] - min_tok) / (max_tok - min_tok) if max_tok > min_tok else 0.0
        return group

    df = df.groupby("ID").apply(normalize_tokens).reset_index(drop=True)

    df["NormBin"], bins = pd.qcut(df["NormalizedToken"], q=num_bins, retbins=True, labels=False, duplicates="drop")
    bin_centers = [(bins[i] + bins[i+1]) / 2 for i in range(len(bins) - 1)]

    # Prepare containers for plotting
    avg_accuracy_per_bin = []
    ids_per_bin = []
    rows_per_bin = []

    for b in sorted(df["NormBin"].dropna().unique()):
        bin_df = df[df["NormBin"] == b]
        rows_per_bin.append(len(bin_df))

        # Compute per-ID accuracy *within the bin*
        per_id_accuracy = bin_df.groupby("ID")["Result"].mean()
        avg_accuracy = per_id_accuracy.mean()
        avg_accuracy_per_bin.append(avg_accuracy)

        ids_per_bin.append(per_id_accuracy.shape[0])
    
    # Define a base color and gradient transparency for shading
    base_color = "lightblue"
    alphas = np.linspace(0.1, 0.7, len(bins) - 1)  # Increasing transparency

    # Plot 1: Average Accuracy vs Token Bin
    plt.figure(figsize=(8, 5))

    # Shade bins
    for j in range(len(bins) - 1):
        plt.axvspan(bins[j], bins[j+1], color=base_color, alpha=alphas[j])

    # Add vertical bin separators
    for b in bins:
        plt.axvline(b, color="gray", linestyle="dashed", linewidth=1, alpha=0.6)

    sns.lineplot(x=bin_centers, y=avg_accuracy_per_bin, marker="D", markersize=10, linewidth=2.5, color="teal")
    plt.xlabel("Normalized (0-1) Number of Tokens", fontsize=14)
    plt.ylabel("Accuracy (%)", fontsize=14)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_yticks))
    plt.title("AIME-24 Accuracy vs Normalized (binned) Length of Thoughts", fontsize=14, pad=10)
    plt.grid(True, axis='y', linestyle='--', alpha=0.2)
    plt.savefig("plots/normalized_accuracy_vs_tokens.png")
    plt.savefig("plots/normalized_accuracy_vs_tokens.pdf", bbox_inches='tight')
    plt.close()

    # Plot 2: Number of IDs and Total Rows per Bin
    plt.figure(figsize=(8, 5))

    # Shade bins
    for j in range(len(bins) - 1):
        plt.axvspan(bins[j], bins[j+1], color=base_color, alpha=alphas[j])

    # Add vertical bin separators
    for b in bins:
        plt.axvline(b, color="gray", linestyle="dashed", linewidth=2, alpha=0.7)

    sns.lineplot(x=bin_centers, y=ids_per_bin, marker="o", label="Unique IDs", color="red")
    sns.lineplot(x=bin_centers, y=rows_per_bin, marker="s", label="Total Rows", color="green")
    plt.xlabel("Token Bin (center)")
    plt.ylabel("Count")
    plt.title("Representation per Token Bin")
    plt.legend()
    plt.grid(True)
    plt.savefig("plots/counts_vs_tokens.png")
    plt.close()

    print("Saved plots:")
    print("Normalized accuracy_vs_tokens.png")
    print("counts_vs_tokens.png")


# analyze_predictions("data/aime_50_samples.tsv", num_bins=5)
plot_per_id_accuracy_by_token_bin("data/aime_50_samples.tsv", num_bins=5)
plot_per_id_accuracy_by_token_bin_all("data/aime_50_samples.tsv", num_bins=5)
plot_normalized_token_accuracy("data/aime_50_samples.tsv", num_bins=5)