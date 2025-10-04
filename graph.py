import matplotlib.pyplot as plt

# Data
models = ['Chen et al.', 'Al-Dhaheri et al.', 'Zhen et al.', 'Zhu et al.', 'CargoOpt (Proposed)']
accuracy = [89.02, 86.50, 82.30, 85.00, 96.00]

# Plot
plt.figure(figsize=(10, 6))
bars = plt.bar(models, accuracy, color=['blue', 'orange', 'green', 'red', 'purple'])
plt.ylabel('Accuracy (%)')
plt.title('Accuracy Comparison of Stowage Optimization Models')
plt.ylim(0, 100)

# Add value labels on bars
for bar, acc in zip(bars, accuracy):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{acc}%', 
             ha='center', va='bottom', fontsize=10)

plt.xticks(rotation=15)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('accuracy_comparison.png')  # Save the chart as an image
plt.show()