#!/usr/bin/python3

import argparse
import flask
import sys
import subprocess
import os
import datetime
import secrets
import yaml
import json

app = flask.Flask("")

@app.route('/test', methods=["POST"])
def test():

    print(json.dumps(flask.request.json, indent=2))
    return flask.jsonify({ "test" : "spamspam"})

def create_app():
    pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='',
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--interface', default="localhost", help='Interface on which to listen')
    parser.add_argument('--port', default="5000", help='Port on which to listen')

    args = parser.parse_args()

    with app.app_context():
        create_app()

    app.run(host=args.interface, port=args.port, debug=True)
