import argparse
import os
import joblib
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression


def model_fn(model_dir):
    return joblib.load(os.path.join(model_dir, "model.joblib"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", default=os.environ.get("SM_MODEL_DIR"))
    parser.add_argument("--train", default=os.environ.get("SM_CHANNEL_TRAIN"))
    args = parser.parse_args()

    df = pd.read_csv(os.path.join(args.train, "train.csv"))
    X = df.drop(columns="quality")
    y = df["quality"]

    model = make_pipeline(StandardScaler(), LinearRegression())
    model.fit(X, y)

    joblib.dump(model, os.path.join(args.model_dir, "model.joblib"))
    print("Training complete. Model saved.")
