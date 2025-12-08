#!/usr/bin/env python
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

import pdb

def load_data(results_file):
    """Load the evaluation results."""
    if not os.path.exists(results_file):
        raise FileNotFoundError(f"Results file not found: {results_file}")
    
    # Load the detailed results
    results_df = pd.read_csv(results_file)
    
    return results_df

def create_operand_categories(results_df):
    """Create categories based on the number of digits in operands."""
    # Create a category column for each unique combination of num_digits_a and num_digits_b
    results_df['operand_category'] = results_df.apply(
        lambda row: f"{row['num_digits_a']}×{row['num_digits_b']}", axis=1
    )
    
    return results_df

def bucketize_response_length(results_df, num_buckets=10):
    """Bucketize the response lengths (thinking_tokens) into equal-sized buckets."""
    # Calculate bucket edges based on the distribution of thinking_tokens
    # pdb.set_trace()
    min_tokens = results_df['thinking_tokens'].min()
    max_tokens = results_df['thinking_tokens'].max()
    
    # Create bucket edges
    bucket_edges = np.linspace(min_tokens, max_tokens, num_buckets + 1)
    
    # Create bucket labels using bucket centers
    bucket_labels = [f"{int((bucket_edges[i] + bucket_edges[i+1])/2/1000)}K" 
                    for i in range(num_buckets)]
    
    # Create buckets column
    results_df['token_bucket'] = pd.cut(
        results_df['thinking_tokens'], 
        bins=bucket_edges,
        labels=bucket_labels,
        include_lowest=True
    )
    
    # Also create a numeric midpoint value for each bucket for better plotting
    bucket_midpoints = [(bucket_edges[i] + bucket_edges[i+1])/2 for i in range(num_buckets)]
    bucket_dict = {label: midpoint for label, midpoint in zip(bucket_labels, bucket_midpoints)}
    results_df['token_bucket_midpoint'] = results_df['token_bucket'].map(bucket_dict)
    
    return results_df

def plot_accuracy_by_response_length(results_df, output_dir, model_name, min_problems_per_category=5):
    """
    Plot accuracy per bucketized response length for each operand category.
    
    Args:
        results_df: DataFrame with the results
        output_dir: Directory to save the plot
        model_name: Name of the model for the plot title
        min_problems_per_category: Minimum number of problems required in a category to include it
    """
    # Start with a larger figure size and add more right margin for labels
    plt.figure(figsize=(14, 10))  # Made wider to accommodate labels
    
    # Create subplot with custom margins
    plt.subplots_adjust(right=0.85)  # Add more space on the right
    
    # Get all unique operand categories
    categories = results_df['operand_category'].unique()
    
    # Filter categories with too few problems
    valid_categories = []
    for category in categories:
        category_df = results_df[results_df['operand_category'] == category]
        num_problems = category_df['problem_id'].nunique()
        if num_problems >= min_problems_per_category:
            valid_categories.append(category)
    
    # Create a custom colormap from blue to red with aesthetically pleasing colors
    # Using a mix of royal blue to crimson red
    colors_list = [
        '#1E4B8F',  # Dark royal blue
        '#2E6BC4',  # Royal blue
        '#4682B4',  # Steel blue
        '#6F98C7',  # Light steel blue
        '#9BB2D3',  # Very light blue
        '#C8A8A8',  # Light rosy brown
        '#B87E7E',  # Rosy brown
        '#A85757',  # Dark rosy brown
        '#963232',  # Dark red
        '#8B0000'   # Dark crimson
    ]
    
    # Create a custom colormap
    from matplotlib.colors import LinearSegmentedColormap
    n_bins = len(valid_categories)
    if n_bins > len(colors_list):
        # If we have more categories than colors, interpolate
        custom_cmap = LinearSegmentedColormap.from_list("custom", colors_list)
        colors = custom_cmap(np.linspace(0, 1, n_bins))
    else:
        # If we have fewer categories than colors, use subset
        colors = colors_list[:n_bins]
    
    # Create a legend mapping
    legend_mapping = {}
    
    # For each operand category, calculate accuracy per token bucket
    for i, category in enumerate(valid_categories):
        category_df = results_df[results_df['operand_category'] == category]
        
        # Group by token bucket and calculate accuracy
        accuracy_by_bucket = category_df.groupby('token_bucket', observed=True).agg(
            num_examples=('is_correct', 'count'),
            correct=('is_correct', 'sum'),
            accuracy=('is_correct', lambda x: x.mean() * 100)
        ).reset_index()
        
        # Filter out buckets with fewer than 3 examples
        accuracy_by_bucket = accuracy_by_bucket[accuracy_by_bucket['num_examples'] >= 3]
        
        # Plot line with thicker lines and larger markers
        if not accuracy_by_bucket.empty:
            plt.plot(
                accuracy_by_bucket.index, 
                accuracy_by_bucket['accuracy'],
                marker='o',
                markersize=10,
                linewidth=2.5,
                color=colors[i],
                label=category,
                alpha=0.9  # Increased alpha for better visibility
            )
            
            # Add category label at the end of the line with larger font
            last_point = accuracy_by_bucket.iloc[-1]
            plt.annotate(
                category,
                (accuracy_by_bucket.index[-1], last_point['accuracy']),
                textcoords="offset points",
                xytext=(10, 0),
                ha='left',
                va='center',
                fontsize=12,
                bbox=dict(
                    facecolor='white',
                    edgecolor=colors[i],
                    alpha=0.9,
                    pad=2,
                    boxstyle='round,pad=0.3'
                )
            )
            
            # Save category info for legend
            legend_mapping[category] = (
                colors[i],
                category
            )
    
    # Set plot details with improved styling and larger fonts
    plt.title(f'{model_name}\nAccuracy by Response Length for Different Operand Categories', 
              fontsize=18, pad=20)
    plt.xlabel('Response Length (Thinking Tokens)', fontsize=16)
    plt.ylabel('Accuracy (%)', fontsize=16)
    
    # Set x-tick labels to the bucket names with better formatting
    if not results_df.empty:
        plt.xticks(range(len(results_df['token_bucket'].cat.categories)), 
                  results_df['token_bucket'].cat.categories, 
                  rotation=0,
                  fontsize=12)
    
    # Improve grid appearance
    plt.grid(True, linestyle='--', alpha=0.2)
    plt.ylim(0, 105)  # Set y-axis limit to allow space for annotations
    
    # Add horizontal reference lines at 25%, 50%, and 75%
    for y in [25, 50, 75]:
        plt.axhline(y=y, color='gray', linestyle=':', alpha=0.2)
    
    # Create a custom legend with better spacing and formatting
    if legend_mapping:
        from matplotlib.lines import Line2D
        
        # Sort categories for better organization in legend
        sorted_categories = sorted(legend_mapping.keys(), 
                                 key=lambda x: [int(n) for n in x.split('×')])
        
        # Create legend elements
        legend_elements = [
            Line2D([0], [0], color=legend_mapping[cat][0], linestyle='-', 
                  marker='o', markersize=6, linewidth=2, label=cat)
            for cat in sorted_categories
        ]
        
        # Calculate optimal number of columns for bottom legend
        ncol = min(8, max(3, len(legend_elements) // 2))
        
        # Add legend at the bottom
        legend = plt.legend(
            handles=legend_elements,
            loc='upper center',
            bbox_to_anchor=(0.5, -0.15),
            fontsize=12,
            ncol=ncol,
            columnspacing=1.0,
            handletextpad=0.5,
            handlelength=1.5,
            borderaxespad=0,
            frameon=True,
            fancybox=False,  # Removed fancy box
            shadow=False,    # Removed shadow
            framealpha=1.0,  # Solid background
            edgecolor='black'
        )
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save figure with high resolution and proper margins
    output_file = os.path.join(output_dir, f"{model_name}_accuracy_by_response_length.pdf")
    plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0.2)  # Added padding
    print(f"Saved accuracy by response length plot to {output_file}")
    plt.close()
    
    # Create a plot focusing only on the categories with higher number of problems
    if len(valid_categories) > 5:
        plot_top_categories(results_df, output_dir, model_name, 5)

def plot_top_categories(results_df, output_dir, model_name, num_top_categories=5):
    """Plot only the top categories with the most problems."""
    # Count problems per category
    category_counts = results_df.groupby('operand_category')['problem_id'].nunique().reset_index()
    category_counts.columns = ['operand_category', 'num_problems']
    
    # Get top categories
    top_categories = category_counts.nlargest(num_top_categories, 'num_problems')['operand_category'].tolist()
    
    # Filter data for top categories
    top_df = results_df[results_df['operand_category'].isin(top_categories)]
    
    # Create the plot
    plt.figure(figsize=(14, 10))
    
    # Create color palette
    colors = sns.color_palette("husl", len(top_categories))
    
    # For each operand category, calculate accuracy per token bucket
    for i, category in enumerate(top_categories):
        category_df = top_df[top_df['operand_category'] == category]
        
        # Group by token bucket and calculate accuracy
        accuracy_by_bucket = category_df.groupby('token_bucket', observed=True).agg(
            num_examples=('is_correct', 'count'),
            correct=('is_correct', 'sum'),
            accuracy=('is_correct', lambda x: x.mean() * 100)
        ).reset_index()
        
        # Plot line
        if not accuracy_by_bucket.empty:
            plt.plot(
                accuracy_by_bucket.index, 
                accuracy_by_bucket['accuracy'],
                marker='o',
                color=colors[i],
                label=category
            )
            
            # For each data point, annotate with number of examples
            for j, row in accuracy_by_bucket.iterrows():
                plt.annotate(
                    f"{int(row['num_examples'])}",
                    (j, row['accuracy']),
                    textcoords="offset points",
                    xytext=(0, 5),
                    ha='center',
                    fontsize=8
                )
    
    # Set plot details
    plt.title(f'{model_name} - Accuracy by Response Length (Top {num_top_categories} Categories)', fontsize=14)
    plt.xlabel('Response Length (Thinking Tokens)', fontsize=12)
    plt.ylabel('Accuracy (%)', fontsize=12)
    
    # Set x-tick labels to the bucket names
    if not top_df.empty:
        plt.xticks(range(len(top_df['token_bucket'].cat.categories)), 
                  top_df['token_bucket'].cat.categories, 
                  rotation=0)
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.ylim(0, 105)  # Set y-axis limit to allow space for annotations
    plt.legend(loc='best', fontsize=9)
    
    # Add explanatory text
    plt.figtext(0.5, 0.01, 
                "Numbers above each point indicate the count of examples in that bin", 
                ha='center', fontsize=10)
    
    # Tighten the layout
    plt.tight_layout()
    
    # Save figure
    output_file = os.path.join(output_dir, f"{model_name}_accuracy_by_response_length_top{num_top_categories}.pdf")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved top categories plot to {output_file}")
    plt.close()

def analyze_response_length_impact(results_df, output_dir, model_name):
    """Analyze the impact of response length on accuracy and create a summary report."""
    # Calculate accuracy by token bucket for each operand category
    category_stats = []
    for category in results_df['operand_category'].unique():
        category_df = results_df[results_df['operand_category'] == category]
        
        # Skip categories with too few examples
        if len(category_df) < 10:
            continue
        
        bucket_stats = category_df.groupby('token_bucket', observed=True).agg(
            count=('is_correct', 'count'),
            correct=('is_correct', 'sum'),
            accuracy=('is_correct', lambda x: x.mean() * 100)
        ).reset_index()

        # Filter out buckets with fewer than 3 examples
        bucket_stats = bucket_stats[bucket_stats['count'] >= 3]
        
        # Skip categories where all buckets have 100% accuracy
        if not bucket_stats.empty and (bucket_stats['accuracy'] == 100).all():
            continue
        
        print(f"Category: {category}")
        print(bucket_stats)
        print("--------------------------------")
        
        # Calculate the accuracy difference between highest and lowest bucket
        if len(bucket_stats) > 1:
            first_bucket_acc = bucket_stats.iloc[0]['accuracy']
            last_bucket_acc = bucket_stats.iloc[-1]['accuracy']
            acc_diff = last_bucket_acc - first_bucket_acc
            
            category_stats.append({
                'category': category,
                'num_problems': category_df['problem_id'].nunique(),
                'first_bucket_acc': first_bucket_acc,
                'last_bucket_acc': last_bucket_acc,
                'acc_difference': acc_diff,
                'first_bucket': bucket_stats.iloc[0]['token_bucket'],
                'last_bucket': bucket_stats.iloc[-1]['token_bucket']
            })
    
    # Create a DataFrame from the category stats
    if category_stats:
        stats_df = pd.DataFrame(category_stats)
        
        # Sort by accuracy difference to see which categories benefit most from longer responses
        stats_df = stats_df.sort_values('acc_difference', ascending=False)
        
        # Save the report
        output_file = os.path.join(output_dir, f"{model_name}_response_length_impact.csv")
        stats_df.to_csv(output_file, index=False)
        print(f"Saved response length impact analysis to {output_file}")
        
        # Create a bar plot of accuracy difference by category
        plt.figure(figsize=(12, 8))
        bars = plt.bar(stats_df['category'], stats_df['acc_difference'])
        
        # Add labels on each bar
        for i, bar in enumerate(bars):
            plt.text(
                bar.get_x() + bar.get_width()/2, 
                bar.get_height() + 0.5 if bar.get_height() >= 0 else bar.get_height() - 3,
                f"{stats_df.iloc[i]['acc_difference']:.1f}%",
                ha='center', 
                fontsize=9
            )
        
        plt.title(f"{model_name} - Impact of Response Length on Accuracy by Category\n" +
                 "(excluding categories with 100% accuracy in all buckets)", fontsize=14)
        plt.xlabel("Operand Category (digits)", fontsize=12)
        plt.ylabel("Accuracy Difference (Last Bucket - First Bucket) in %", fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save the plot
        plot_file = os.path.join(output_dir, f"{model_name}_response_length_impact.pdf")
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"Saved response length impact plot to {plot_file}")
        plt.close()

def plot_accuracy_by_response_length_grouped(
    results_df, output_dir, model_name, min_problems_per_category=5
):
    """
    Create three side-by-side plots for different groups of operand categories.
    Group 1: 1×1 to 6×6
    Group 2: 7×7 to 11×11
    Group 3: 12×12 to 20×20
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns
    from matplotlib.colors import LinearSegmentedColormap
    import os
    
    # Create the figure and subplots with more width and bottom space
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 7))
    plt.subplots_adjust(
        wspace=0.03,     # spacing between subplots
        top=0.8,       # top margin
        bottom=0.3,    # more bottom margin to give room for the legend
        left=0.05,
        right=0.98
    )
    
    # Define the category groups
    group1 = [f"{i}×{i}" for i in range(1, 7)]   # 1×1 to 6×6
    group2 = [f"{i}×{i}" for i in range(7, 12)]  # 7×7 to 11×11
    group3 = [f"{i}×{i}" for i in range(12, 21)] # 12×12 to 20×20
    
    # Create a custom colormap from a list of colors
    # colors_list = [
    #     '#1E4B8F', '#2E6BC4', '#4682B4', '#6F98C7', '#9BB2D3',
    #     '#C8A8A8', '#B87E7E', '#A85757', '#963232', '#8B0000'
    # ]
    colors_list = [
        '#0D2A5B',  # Very dark blue
        '#15447A',  # Dark navy blue
        '#1E5C99',  # Deep steel blue
        '#2D6DA7',  # Darker blue
        '#375E77',  # Dark muted teal
        '#704545',  # Dark desaturated red
        '#872D2D',  # Deep red
        '#6E1919',  # Darker red
        '#560F0F',  # Very dark red
        '#3D0000'   # Almost black red
    ]
    custom_cmap = LinearSegmentedColormap.from_list("custom", colors_list)
    
    # Define marker styles for different categories
    markers = ['o', 's', '^', 'D', 'v', '>', '<', 'p', '*', 'h', 
               'H', '8', 'd', 'P', 'X', 'o', 's', '^', 'D', 'v']
    
    # Build color arrays for all categories
    all_categories = group1 + group2 + group3
    all_colors = custom_cmap(np.linspace(0, 1, len(all_categories)))
    
    # Split out colors and markers for each group
    colors1 = {
        cat: color for cat, color in zip(group1, all_colors[:len(group1)])
    }
    colors2 = {
        cat: color for cat, color in zip(
            group2, all_colors[len(group1):len(group1) + len(group2)]
        )
    }
    colors3 = {
        cat: color for cat, color in zip(
            group3, all_colors[len(group1) + len(group2):]
        )
    }
    
    markers1 = {cat: marker for cat, marker in zip(group1, markers[:len(group1)])}
    markers2 = {cat: marker for cat, marker in zip(group2, markers[len(group1):len(group1) + len(group2)])}
    markers3 = {cat: marker for cat, marker in zip(group3, markers[len(group1) + len(group2):])}
    
    # List of lines for the legend
    legend_elements = []
    
    def plot_group(ax, categories, colors_dict, markers_dict, group_name):
        # Get the base color for the category
        base_color = "#F4A89A"

        # pdb.set_trace()
        
        # Normalize shading intensity based on number of bins
        num_bins = 5
        alpha_values = np.linspace(0.1, 0.4, num_bins)  # Increasing intensity

        ax.axvline(0, color='gray', linestyle='dashed', alpha=0.6, linewidth=1)
        
        for i in range(num_bins):
            bin_start = i
            bin_end = i + 1
            # if bin_end < num_bins:
            ax.fill_between(
                [bin_start, bin_end], -5, 105, 
                color=base_color, 
                alpha=alpha_values[i]
            )
            
            # Add vertical dashed line at bin edge
            ax.axvline(bin_end, color='gray', linestyle='dashed', alpha=0.6, linewidth=1)

        for cat in categories:
            cat_df = results_df[results_df['operand_category'] == cat]
            
            # Filter out categories with insufficient data
            if len(cat_df) >= min_problems_per_category:
                # Compute accuracy by response-length bucket
                accuracy_by_bucket = (
                    cat_df
                    .groupby('token_bucket', observed=True)
                    .agg(
                        num_examples=('is_correct', 'count'),
                        accuracy=('is_correct', lambda x: x.mean() * 100)
                    )
                    .reset_index()
                )
                # Only keep buckets with at least a few examples
                accuracy_by_bucket = accuracy_by_bucket[
                    accuracy_by_bucket['num_examples'] >= 3
                ]
                
                if not accuracy_by_bucket.empty:
                    # Plot line with specific marker
                    line = ax.plot(
                        accuracy_by_bucket.index+0.5,
                        accuracy_by_bucket['accuracy'],
                        marker=markers_dict[cat],
                        markersize=15,
                        linewidth=2.5,
                        color=colors_dict[cat],
                        label=cat,
                        alpha=0.9
                    )[0]
                    legend_elements.append(line)
        
        ax.set_title(group_name, fontsize=15, pad=10)
        ax.set_xlabel('Number of Tokens', fontsize=16)
        
        # Only the leftmost plot has a y-label
        if ax == ax1:
            ax.set_ylabel('Accuracy (%)', fontsize=16)
        else:
            ax.set_yticklabels([])
            ax.yaxis.set_ticks_position('none')

        ax.grid(True, axis='y', linestyle='--', alpha=0.2)
    
        ax.set_ylim(-5, 105)

        # pdb.set_trace()
        
        # Set x-tick labels
        if not results_df.empty:
            ax.set_xticks([xz + 0.5 for xz in range(len(results_df['token_bucket'].cat.categories))])
            ax.set_xticklabels(
                results_df['token_bucket'].cat.categories,
                rotation=0,
                fontsize=16
            )
        ax.tick_params(axis='both', which='major', labelsize=10)
    
    # Plot each group
    plot_group(ax1, group1, colors1, markers1, "Small Numbers\n(1×1 to 6×6)")
    plot_group(ax2, group2, colors2, markers2, "Medium Numbers\n(7×7 to 11×11)")
    plot_group(ax3, group3, colors3, markers3, "Large Numbers\n(12×12 to 20×20)")
    
    # Overall figure title
    fig.suptitle(
        f"Multiplication Accuracy vs (binned) Length of Thoughts",
        fontsize=18,
        y=0.95
    )
    
    # Sort the legend elements by the numeric size of the category
    legend_elements = sorted(
        list({line.get_label(): line for line in legend_elements}.values()),
        key=lambda x: [int(n) for n in x.get_label().split('×')]
    )
    
    # The legend goes at the bottom, below the figure
    ncol = min(10, max(3, len(legend_elements) // 2))
    fig.legend(
        handles=legend_elements,
        loc='lower center',
        bbox_to_anchor=(0.5, 0.08),  # push the legend further down
        fontsize=14,
        ncol=ncol,
        columnspacing=1.0,
        handletextpad=0.5,
        handlelength=1.5,
        borderaxespad=0,
        frameon=True,
        fancybox=False,
        shadow=False,
        framealpha=1.0,
        edgecolor='black'
    )
    
    # Save figure
    output_file = os.path.join(output_dir, f"{model_name}_accuracy_by_response_length_grouped.pdf")
    plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0.3)
    plt.savefig(output_file.replace("pdf", "png"), dpi=300, bbox_inches='tight', pad_inches=0.3)
    plt.close()
    print(f"Saved grouped accuracy plot to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Visualize accuracy by response length for different operand categories")
    parser.add_argument("results_file", help="Path to the results CSV file")
    parser.add_argument("--model", type=str, default=None, 
                       help="Model name for plot titles (default: extracted from filename)")
    parser.add_argument("--output-dir", type=str, default="plots/",
                       help="Directory to save visualizations (default: ./visualizations)")
    parser.add_argument("--num-buckets", type=int, default=5,
                       help="Number of buckets to divide response lengths into (default: 10)")
    parser.add_argument("--min-problems", type=int, default=3,
                       help="Minimum number of problems required in a category to include it (default: 3)")
    
    args = parser.parse_args()
    
    # Extract model name from filename if not provided
    if args.model is None:
        filename = os.path.basename(args.results_file)
        if filename.startswith("results_"):
            model_parts = filename.split("_")[1:-2]  # Remove "results_" and timestamp
            args.model = "_".join(model_parts)
        else:
            args.model = "model"
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load data
    results_df = load_data(args.results_file)
    
    # Create operand categories
    results_df = create_operand_categories(results_df)
    
    # Bucketize response lengths
    results_df = bucketize_response_length(results_df, args.num_buckets)
    
    # Generate visualizations
    plot_accuracy_by_response_length(results_df, args.output_dir, args.model, args.min_problems)
    plot_accuracy_by_response_length_grouped(results_df, args.output_dir, args.model, args.min_problems)
    
    # Analyze impact of response length on accuracy
    analyze_response_length_impact(results_df, args.output_dir, args.model)
    
    print(f"All visualizations have been saved to {args.output_dir}")

if __name__ == "__main__":
    main() 