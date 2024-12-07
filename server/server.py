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
from flask_cors import CORS, cross_origin

app = flask.Flask("")
CORS(app)

def print_part(part):

    return_string = ""
    with open("test-out-mail.txt", "w") as f:

        if "headers" in part:
            headers = part["headers"]
            for k, v in headers.items():

                first_line = True
                for el in v:
                    if first_line:
                        if "\t" in el:
                            print(k.title(), ": ", el.split("\t")[0], sep="")
                            f.write(k.title() + ": " + el.split("\t")[0] + "\n")
                        else:
                            print(k.title(), ": ", el, sep="")
                            f.write(k.title() + ": " + el + "\n")
                        first_line = False
                    else:
                        for fixed in el.split("\t"):
                            f.write("\t" + fixed + "\n")

            # header ending line #
            f.write("\n")

        if "body" in part:
            print(part["body"])
            f.write(part["body"])

        if "parts" in part:
            for subpart in part["parts"]:
                print_part(subpart)

def feed_spamd(string):

    process = subprocess.run(
        ['spamd', 'spamassassin', '-D'],
        input=string,
        text=True,
        capture_output=True,
        universal_newlines=True
    )

    return process.stdout

def analyse_spamd_reponse(string):

    if not "X-Spam-Status:" in string:
        return { "error" : "Missing X-Spam-Status in Reponse" }

    # should look like this X-Spam-Status: No, score=-4.3 required=3.1 tests= #
    try:

        status_line = string.split("X-Spam-Status")[1].split("\n")[0]
        is_spam = "No, " in status_line
        score = float(status_line.split("score=")[1].split(" ")[0])
        return { "is_spam" : is_spam, "score" : score }

    except (ValueError, IndexError):
        return { "error" : "Failed to parse spam status" }



@cross_origin(origins=["*"])
@app.route('/test', methods=["POST"])
def test():

    # write a debug file #
    with open("test.json", "w") as f:
        f.write(json.dumps(flask.request.json, indent=2))

    # get the full email as a string #
    result = ""
    for part in flask.request.json:
        result += print_part(part)

    # analyze with spamd #
    result_spamd = feed_spamd(result)
    response = analyse_spamd_reponse(result_spamd)

    return flask.jsonify(response)

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
