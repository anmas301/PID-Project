# Example Jupyter Notebook untuk Exploratory Data Analysis

## 📊 ISPA Risk Monitoring - Exploratory Data Analysis

### Import Libraries

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path.cwd().parent))
from config.config import CSV_FILES, DATA_PATHS

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
```

### Load Data

```python
# Load CSV datasets
df_kualitas_udara = pd.read_csv(CSV_FILES['kualitas_udara'])
df_suhu_kelembaban = pd.read_csv(CSV_FILES['suhu_kelembaban'])
df_tekanan_angin = pd.read_csv(CSV_FILES['tekanan_angin'])
df_kasus_ispa = pd.read_csv(CSV_FILES['kasus_ispa'])

print("Data loaded successfully!")
print(f"Kualitas Udara: {df_kualitas_udara.shape}")
print(f"Suhu Kelembaban: {df_suhu_kelembaban.shape}")
print(f"Tekanan Angin: {df_tekanan_angin.shape}")
print(f"Kasus ISPA: {df_kasus_ispa.shape}")
```

### Data Exploration

```python
# Display first few rows
df_kualitas_udara.head()
```

```python
# Check data info
df_kualitas_udara.info()
```

```python
# Statistical summary
df_kualitas_udara.describe()
```

### Visualizations

```python
# Plot 1: Distribution of air quality
plt.figure(figsize=(12, 6))
# Add your visualization code here
plt.title('Distribution of Air Quality Index')
plt.show()
```

```python
# Plot 2: Time series of ISPA cases
plt.figure(figsize=(14, 6))
# Add your visualization code here
plt.title('Trend of ISPA Cases Over Time')
plt.show()
```

### Correlation Analysis

```python
# Calculate correlations
# Add your analysis code here
```

### Insights & Findings

Write your observations and insights here.

---

**Note**: Jalankan notebook ini dengan `jupyter notebook` atau `jupyter lab`
