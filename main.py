# -*- codeing = utf-8 -*-
import time
import flask
from flask import Flask, request, g, jsonify
import stablecoin


app = Flask(__name__)


@app.get("/get_stablecoin_ratio")
def stablecoin_ratio():
    return stable_coin_ratio.get_data()


@app.get("/get_swap_data")
def swap_data():
    return swap.data


if __name__ == "__main__":
    print("init")
    stable_coin_ratio = stablecoin.StableCoinRatio()
    swap = stablecoin.Swap()
    print("ok")
    app.run(host='0.0.0.0', port=5001)
