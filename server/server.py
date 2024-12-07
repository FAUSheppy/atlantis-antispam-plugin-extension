#!/usr/bin/python3

import argparse
import flask
import sys
import subprocess
import os
import datetime
import secrets
import json
from flask_cors import CORS, cross_origin

app = flask.Flask("")
CORS(app)

# Function to format headers
def format_headers(headers):
    formatted = []
    for key, values in headers.items():
        for value in values:
            formatted.append(f"{key}: {value}")
    return "\r\n".join(formatted)

# Function to rebuild the MIME parts
def rebuild_parts(parts, boundary=None):
    body = []
    for part in parts:
        if "parts" in part:
            # Multipart container
            sub_boundary = part["headers"]["content-type"][0].split("boundary=")[1].strip('"')
            body.append(f"--{sub_boundary}")
            body.append(rebuild_parts(part["parts"], boundary=sub_boundary))
            body.append(f"--{sub_boundary}--")
        else:
            # Leaf part
            headers = format_headers(part["headers"])
            body.append(headers)
            body.append("\r\n")
            body.append(part.get("body") or "")
    return "\r\n".join(body)

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
                            #print(k.title(), ": ", el.split("\t")[0], sep="")
                            f.write(k.title() + ": " + el.split("\t")[0] + "\n")
                        else:
                            #print(k.title(), ": ", el, sep="")
                            f.write(k.title() + ": " + el + "\n")
                        first_line = False
                    else:
                        for fixed in el.split("\t"):
                            f.write("\t" + fixed + "\n")

            # header ending line #
            f.write("\n")

        if "body" in part:
            #print(part["body"])
            f.write(part["body"])

        if "parts" in part:
            for subpart in part["parts"]:
                print_part(subpart)

    return return_string

def feed_spamd(string):

    print("test", file=sys.stderr)
    process = subprocess.run(
        ['spamassassin'],
        input=string,
        text=True,
        capture_output=True,
        universal_newlines=True
    )

    print(process.stderr, process.stdout, file=sys.stderr)

    return process.stdout

def analyse_spamd_reponse(string):

    if not "X-Spam-Status:" in string:
        return { "error" : "Missing X-Spam-Status in Reponse" }

    # should look like this X-Spam-Status: No, score=-4.3 required=3.1 tests= #
    try:

        status_line = string.split("X-Spam-Status")[1].split("\n")[0]
        is_spam = "X-Spam-Flag: YES" in string
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
    result = print_part(flask.request.json)

    # Rebuild the email
    email_data = flask.request.json
    email_headers = format_headers(email_data["headers"])
    email_body = rebuild_parts(email_data["parts"])
    email_text = f"{email_headers}\r\n\r\n{email_body}"

    # analyze with spamd #
    result_spamd = feed_spamd(email_text)
    response = analyse_spamd_reponse(result_spamd)

    print(json.dumps(response, indent=2), file=sys.stderr)
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
