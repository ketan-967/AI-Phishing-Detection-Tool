import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1. Load the dataset
df = pd.read_csv('dataset.csv')

# 2. Preprocessing
# Drop 'index' and 'Result'. Ensure your CSV column is named 'Result'
X = df.drop(['index', 'Result'], axis=1) 
y = df['Result']

# 3. Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Train the Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. Evaluate
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")

# 6. Save the model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved successfully as model.pkl")