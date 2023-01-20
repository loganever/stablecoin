# -*- codeing = utf-8 -*-
import time
import flask
from flask import Flask, request, g, jsonify
from flask_cors import CORS
import stablecoin


app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.get("/get_stablecoin_ratio")
def stablecoin_ratio():
    return stable_coin_ratio.get_data()


@app.get("/get_swap_data")
def swap_data():
    result = {}
    for i in swap.data.keys():
        if len(swap.data[i])>0:
            result[i] = swap.data[i]
    return result


if __name__ == "__main__":
    print("init")
    stable_coin_ratio = stablecoin.StableCoinRatio()
    swap = stablecoin.Swap()
    print("ok")
    app.run(host='0.0.0.0', port=8899)
