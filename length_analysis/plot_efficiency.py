import matplotlib.pyplot as plt

# Data points
tokens = [64, 256, 512, 768, 1024]
accuracy = [57.77, 69.75, 89.76, 93.5, 95]

# Unconstrained settings
avg_tokens_unconstrained = 1388.46
accuracy_unconstrained = 96.58

# Create plot
plt.figure(figsize=(9, 6))

# # Set the axes background to a slightly darker beige
# ax = plt.gca()  # Get current axes
# ax.set_facecolor('#f7ebd6')  # Light beige for contrast

plt.plot(tokens, accuracy, marker='o', linestyle='-', markersize=8, label='Test Time Scaling', color='tab:blue')

# Add dotted lines for unconstrained settings
plt.axvline(avg_tokens_unconstrained, linestyle='dotted', color='black', label='Avg Tokens (Unconstrained)')
plt.axhline(accuracy_unconstrained, linestyle='dotted', color='black', label='Accuracy (Unconstrained)')

# Add annotation for unconstrained setting
plt.text(avg_tokens_unconstrained-70, accuracy_unconstrained+0.5, 
         f"Unconstrained:\nAvg tokens: {int(avg_tokens_unconstrained)}\nAccuracy: {accuracy_unconstrained:.2f}%", 
         color='black', fontsize=10, ha='left', va='bottom', bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.3'))

# Add lines and annotations for % drops
for t, acc in zip(tokens, accuracy):
    # Compute percentage drops
    acc_drop = 100 * (accuracy_unconstrained - acc) / accuracy_unconstrained
    token_drop = 100 * (avg_tokens_unconstrained - t) / avg_tokens_unconstrained
    
    # Line to horizontal reference (accuracy drop)
    plt.plot([t, t], [acc, accuracy_unconstrained], linestyle='--', color='tab:red', alpha=0.8)
    plt.text(t, ((acc + accuracy_unconstrained) / 2)-0.5, f"-{acc_drop:.1f}%", 
             color='crimson', ha='right' if t > avg_tokens_unconstrained else 'left', fontsize=12, fontweight='bold')
    
    # Line to vertical reference (token drop)
    plt.plot([t, avg_tokens_unconstrained], [acc, acc], linestyle='--', color='teal', alpha=0.8)
    plt.text((t + avg_tokens_unconstrained) / 2, acc-0.15, f"-{token_drop:.1f}%", 
             color='teal', va='bottom', fontsize=12, fontweight='bold')

# Labels and title
plt.xlabel('Number of Tokens (Enforced Budget)', fontsize=16)
plt.ylabel('Accuracy (%)', fontsize=16)
plt.title('GSM8k Accuracy vs Enforced Token Budget', fontsize=18)
# plt.legend()
# plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(fontsize=11)
plt.yticks(fontsize=11)
plt.ylim(57,100)

# Show plot
plt.savefig("plots/gsm_efficiency.png", bbox_inches='tight')
plt.savefig("plots/gsm_efficiency.pdf", bbox_inches='tight')
