import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# A simplified dataset containing only the 4 features we are extracting in the frontend.
# The `Result` column is the label (-1 for phishing, 1 for legitimate).
# This dataset is generated for this specific project.
data = pd.DataFrame({
    'url_length': [50, 20, 80, 40, 65, 30, 25, 75, 55, 48],
    'has_https': [1, 1, -1, 1, -1, 1, 1, -1, 1, -1],
    'has_at_symbol': [-1, 1, -1, 1, -1, 1, 1, -1, 1, 1],
    'num_dots': [3, 2, 5, 3, 4, 3, 2, 6, 4, 3],
    'Result': [-1, 1, -1, 1, -1, 1, 1, -1, 1, -1]
})

X = data.drop("Result", axis=1)
y = data["Result"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
