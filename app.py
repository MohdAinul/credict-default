
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from flask import Flask, request, jsonify

print("loading data...")

# dataset load
url = "https://github.com/ybifoundation/Dataset/raw/main/Credit%20Default.csv"
df = pd.read_csv(url)

# basic check
print("data shape:", df.shape)

# features & target
X = df.drop("Default", axis=1)
y = df["Default"]

# split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# scaling (important to avoid warnings)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# model
model = LogisticRegression(max_iter=1000, solver="liblinear")

print("training model...")
model.fit(X_train, y_train)

# accuracy
acc = model.score(X_test, y_test)
print("model accuracy:", round(acc, 3))


# ------------------ FLASK APP ------------------ #

app = Flask(__name__)

@app.route("/")
def home():
    return "API is running 🚀"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # extracting values
        income = data.get("Income")
        age = data.get("Age")
        loan = data.get("Loan")
        lti = data.get("Loan_to_Income")

        # basic validation
        if None in [income, age, loan, lti]:
            return jsonify({"error": "invalid input"}), 400

        # convert to array
        arr = np.array([[income, age, loan, lti]])

        # scale input
        arr = scaler.transform(arr)

        # prediction
        pred = model.predict(arr)[0]
        prob = model.predict_proba(arr)[0][1]

        return jsonify({
            "prediction": int(pred),
            "probability": round(float(prob), 3)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("starting server...")
    app.run(debug=False)