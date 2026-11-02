from flask import Flask, render_template, request
import numpy as np
import pickle

app = Flask(__name__)

model = pickle.load(open('model.pkl', 'rb'))

# The 11 features, in the same order the model was trained on
FEATURES = [
    'fixed_acidity', 'volatile_acidity', 'citric_acid', 'residual_sugar',
    'chlorides', 'free_sulfur_dioxide', 'total_sulfur_dioxide', 'density',
    'pH', 'sulphates', 'alcohol'
]

DEFAULTS = {
    'fixed_acidity': 7.0, 'volatile_acidity': 0.29, 'citric_acid': 0.31,
    'residual_sugar': 3.0, 'chlorides': 0.047, 'free_sulfur_dioxide': 29,
    'total_sulfur_dioxide': 118, 'density': 0.9949, 'pH': 3.21,
    'sulphates': 0.51, 'alcohol': 10.3
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    values = [float(request.form.get(name) or DEFAULTS[name]) for name in FEATURES]
    features = np.array([values])

    raw = float(model.predict(features)[0])
    score = round(min(max(raw, 0), 10))

    if score >= 7:
        label = 'Above average'
    elif score >= 5:
        label = 'Average'
    else:
        label = 'Below average'

    return render_template('index.html', predict=score, raw=round(raw, 2), label=label)


if __name__ == '__main__':
    app.run(debug=True)