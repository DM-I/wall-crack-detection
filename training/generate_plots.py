import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

csv_path = r'G:\bangong\qiangtijiance - CLAUDE\training\train_524dab54\weights\results.csv'
out_dir = r'G:\bangong\qiangtijiance - CLAUDE\training\train_524dab54\weights'

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip()

epochs = df['epoch'].values

fig, axes = plt.subplots(3, 2, figsize=(16, 14))

# 1. Loss curves
ax = axes[0, 0]
ax.plot(epochs, df['train/box_loss'], label='Train Box Loss', linewidth=1.5)
ax.plot(epochs, df['train/cls_loss'], label='Train Class Loss', linewidth=1.5)
ax.plot(epochs, df['train/dfl_loss'], label='Train DFL Loss', linewidth=1.5)
ax.plot(epochs, df['val/box_loss'], label='Val Box Loss', linewidth=1.5, linestyle='--')
ax.plot(epochs, df['val/cls_loss'], label='Val Class Loss', linewidth=1.5, linestyle='--')
ax.plot(epochs, df['val/dfl_loss'], label='Val DFL Loss', linewidth=1.5, linestyle='--')
ax.set_xlabel('Epoch')
ax.set_ylabel('Loss')
ax.set_title('Training & Validation Loss')
ax.legend(loc='upper right', fontsize=7, ncol=2)
ax.grid(True, alpha=0.3)

# 2. mAP curves
ax = axes[0, 1]
ax.plot(epochs, df['metrics/mAP50(B)'], label='mAP50', linewidth=2, color='#2196F3')
ax.plot(epochs, df['metrics/mAP50-95(B)'], label='mAP50-95', linewidth=2, color='#FF5722')
ax.set_xlabel('Epoch')
ax.set_ylabel('mAP')
ax.set_title('mAP50 & mAP50-95')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_ylim(bottom=0)

# 3. Precision & Recall
ax = axes[1, 0]
ax.plot(epochs, df['metrics/precision(B)'], label='Precision', linewidth=2, color='#4CAF50')
ax.plot(epochs, df['metrics/recall(B)'], label='Recall', linewidth=2, color='#FF9800')
ax.set_xlabel('Epoch')
ax.set_ylabel('Score')
ax.set_title('Precision & Recall')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1)

# 4. Combined Box + Class + DFL loss (train only)
ax = axes[1, 1]
ax.plot(epochs, df['train/box_loss'] + df['train/cls_loss'] + df['train/dfl_loss'],
        label='Total Train Loss', linewidth=2, color='#9C27B0')
ax.set_xlabel('Epoch')
ax.set_ylabel('Loss')
ax.set_title('Total Training Loss')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)

# 5. Learning rate
ax = axes[2, 0]
ax.plot(epochs, df['lr/pg0'], label='lr/pg0', linewidth=1.5, color='#E91E63')
ax.plot(epochs, df['lr/pg1'], label='lr/pg1', linewidth=1.5, color='#00BCD4')
ax.plot(epochs, df['lr/pg2'], label='lr/pg2', linewidth=1.5, color='#795548')
ax.set_xlabel('Epoch')
ax.set_ylabel('Learning Rate')
ax.set_title('Learning Rate Schedule')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)

# 6. Best epoch marker
ax = axes[2, 1]
ax.plot(epochs, df['metrics/mAP50-95(B)'], linewidth=2, color='#FF5722')
best_idx = df['metrics/mAP50-95(B)'].idxmax()
best_epoch = df.loc[best_idx, 'epoch']
best_map = df.loc[best_idx, 'metrics/mAP50-95(B)']
ax.annotate(f'Best: epoch {int(best_epoch)}\nmAP50-95={best_map:.4f}',
            xy=(best_epoch, best_map), xytext=(best_epoch + 8, best_map - 0.05),
            arrowprops=dict(arrowstyle='->', color='black'),
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
ax.plot(best_epoch, best_map, 'r*', markersize=15)
ax.set_xlabel('Epoch')
ax.set_ylabel('mAP50-95')
ax.set_title(f'Best Model: epoch {int(best_epoch)}  mAP50-95={best_map:.4f}')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{out_dir}/results.png', dpi=150, bbox_inches='tight')
print(f'results.png saved')

# Summary stats
print(f'\n=== Training Summary ===')
print(f'Total epochs: {len(df)}')
print(f'Best epoch: {int(best_epoch)}')
print(f'Best mAP50:    {df["metrics/mAP50(B)"].max():.4f}')
print(f'Best mAP50-95: {df["metrics/mAP50-95(B)"].max():.4f}')
print(f'Best Precision: {df["metrics/precision(B)"].max():.4f}')
print(f'Best Recall:    {df["metrics/recall(B)"].max():.4f}')
print(f'Final mAP50:    {df["metrics/mAP50(B)"].iloc[-1]:.4f}')
print(f'Final mAP50-95: {df["metrics/mAP50-95(B)"].iloc[-1]:.4f}')
