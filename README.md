## Wine Quality Prediction - Flask App in a Docker Container

Predicts a wine's quality score (0-10) from 11 physicochemical measurements, using a
Gradient Boosting model. The app is containerized with Docker and deployed to Heroku
through a GitHub Actions CI/CD pipeline.

live app: https://wine-quality-hoyne-b95d2349a725.herokuapp.com/
##
### Data
- **Dataset:** [UCI Wine Quality](https://archive.ics.uci.edu/dataset/186/wine+quality), red and white Vinho Verde wines combined
- **Features (11):** fixed acidity, volatile acidity, citric acid, residual sugar, chlorides, free sulfur dioxide, total sulfur dioxide, density, pH, sulphates, alcohol
- **Target:** quality (tasters' score; only 3-9 appear in the data)
- **Cleaning:** no missing values; removed 1,179 duplicate rows (6,497 → 5,318) so identical wines couldn't appear in both the training and test sets
##
### Model
Compared 4 regression models against a baseline that always predicts the average quality
(75/25 stratified split, random_state=29):

| Model | MAE | RMSE | R² | Exact (rounded) | Within 1 point |
|---|---|---|---|---|---|
| Random Forest | 0.534 | 0.688 | 0.385 | 57.5% | 86.1% |
| **Gradient Boosting** | 0.540 | 0.691 | 0.380 | **58.1%** | **86.2%** |
| KNN | 0.555 | 0.710 | 0.345 | 55.1% | 85.9% |
| Linear Regression | 0.566 | 0.723 | 0.322 | 52.9% | 85.2% |
| Baseline (mean) | 0.694 | 0.878 | 0.000 | 43.7% | 76.6% |

**Why Gradient Boosting:** it performed almost the same as Random Forest but was slightly
better at predicting the exact rounded score, and it produces a much smaller model file,
which keeps the Docker image light.

**Most important features:** alcohol (0.46), volatile acidity (0.15), free sulfur dioxide (0.11).

**Limitation:** most wines score 5-6, so the model pulls predictions toward the middle.
Very good or very poor wines tend to be under- or over-rated.
##
### App
- Enter any of the 11 measurements; blank boxes use the dataset median (shown in gray)
- Each box shows the range seen in the training data
- Returns a rounded score, a label (below average / average / above average) and the exact model output

### Run with Docker
    docker build -t wine-quality .
    docker run --rm -p 5000:5000 wine-quality
Then open http://localhost:5000
##
### Issues resolved
- **Docker Desktop wouldn't install:** Windows' "Virtual Machine Platform" feature was off. Ran `wsl --install --no-distribution` in an admin PowerShell and restarted.
- **"Failed to connect to the docker API":** the Docker engine wasn't running. Opened Docker Desktop first.
- **JSONArgsRecommended warning:** switched the Dockerfile `CMD` to JSON form with `sh -c` so `$PORT` still works and gunicorn receives stop signals.
- **ValueError on blank inputs:** after making inputs optional, `app.py` now falls back to each feature's median.
- **"This command is for Docker apps only" on Heroku:** new Heroku apps use the heroku-24 stack. Added a workflow step to run `heroku stack:set container` before deploying.

### SageMaker training quota (ResourceLimitExceeded)
- **Error:** The first training job failed with `ResourceLimitExceeded`: "The account-level service limit
  'ml.m5.large for training job usage' is 0 Instances."
- **Troubleshooting:** In **Service Quotas → Amazon SageMaker** (region us-east-2), I found that all of my
  training job quotas were 0, while `ml.m5.xlarge for endpoint usage` was already 16. I submitted a quota
  increase request to 1 instance for training job usage.
- **Result:** The request was approved the next day. The training job then ran successfully
  (114 billable seconds), and the model was deployed to an `ml.m5.xlarge` endpoint, which already had quota.

J. Hoyne ANA680
