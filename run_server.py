import pandas as pd
from PIL import Image
import numpy as np
import flask
import io
import os
from sklearn.externals import joblib

PUBLIC_IP = "52.117.158.147"
NODE_PORT = "31520"

app = flask.Flask(__name__)
credit_model = None
application_url = "http://{}:{}".format(PUBLIC_IP, NODE_PORT)

def load_credit_model():
    global credit_model

    credit_model_path = os.path.join(os.getcwd(), 'models', 'credit', 'german_credit_risk.joblib')
    credit_model = joblib.load(credit_model_path)

@app.route("/v1/deployments/credit/online", methods=["POST"])
def credit_online():
    response = {}
    labels = ['Risk', 'No Risk']

    if flask.request.method == "POST":
        payload = flask.request.get_json()

        if payload is not None:
            df = pd.DataFrame.from_records(payload['values'], columns=payload['fields'])
            scores = credit_model['model'].predict_proba(df).tolist()
            predictions = credit_model['postprocessing'](credit_model['model'].predict(df))
            response = {'fields': ['prediction', 'probability'], 'labels': labels,
                        'values': list(map(list, list(zip(predictions, scores))))}

    return flask.jsonify(response)

@app.route("/v1/deployments", methods=["GET"])
def get_deployments():
    response = {}

    if flask.request.method == "GET":
        response = {
            "count": 1,
            "resources": [
                {
                    "metadata": {
                        "guid": "credit",
                        "created_at": "2019-01-01T10:11:12Z",
                        "modified_at": "2019-01-02T12:00:22Z"
                    },
                    "entity": {
                        "name": "German credit risk compliant deployment",
                        "description": "Scikit-learn credit risk model deployment",
                        "scoring_url": "{}/v1/deployments/credit/online".format(application_url),
                        "asset": {
                              "name": "credit",
                              "guid": "credit"
                        },
                        "asset_properties": {
                               "problem_type": "binary",
                               "input_data_type": "structured",
                        }
                    }
                }
            ]
        }

    return flask.jsonify(response)

if __name__ == "__main__":
    load_credit_model()
    port = os.getenv('PORT', '5000')
    app.run(host='0.0.0.0', port=int(port))