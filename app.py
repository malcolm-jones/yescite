import os
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask, request, render_template, Response, jsonify
import io

from yescite import YesCite, bib_to_df, extract_entries, add_arXiv_versions
from validation import valid_yescite, valid_bibtocsv, valid_bibformat, valid_arxivversions
import usage

load_dotenv()

sentry_sdk.init(
    dsn=os.getenv("GLITCHTIP_DSN"),
    integrations=[FlaskIntegration()],
    traces_sample_rate=float(os.getenv("TRACES_SAMPLE_RATE")),
)

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    usage.add_log("Index")
    return render_template('index.html')

@app.route('/yescite', methods=['POST'])
def yescite():
    endpoint_code = "yescite"
    usage.add_log(endpoint_code)
    if request.method == "POST":
        usage.add_log("POST")
        input_yescite_bbl = request.form['input_yescite_bbl']
        input_yescite_bib = request.form['input_yescite_bib']
        if (
            not valid_yescite(input_yescite_bbl, input_yescite_bib)
        ):
            usage.add_log("Failed validation.")
            return jsonify({"processed_text": os.getenv("VALIDATION_MESSAGE")})
        else:
            usage.add_log("Passed validation.")
            lines_bbl = input_yescite_bbl.splitlines()
            lines_bib = input_yescite_bib.splitlines()
            yc = YesCite(lines_bbl, lines_bib)
            output_yescite = '\n'.join(yc.yescite)
            return jsonify({"processed_text": f"{output_yescite}"})

@app.route('/bibtocsv', methods=['POST'])
def bibtocsv():
    endpoint_code = "bibtocsv"
    usage.add_log(endpoint_code)
    if request.method == "POST":
        usage.add_log("POST")
        input_bibtocsv = request.form['input_bibtocsv']
        if (
            not valid_bibtocsv(input_bibtocsv)
        ):
            usage.add_log("Failed validation.")
            return jsonify({"processed_text": os.getenv("VALIDATION_MESSAGE")})
        else:
            usage.add_log("Passed validation.")
            lines_bib = input_bibtocsv.splitlines()
            df = bib_to_df(lines_bib)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            return Response(
                csv_buffer,
                mimetype='text/csv',
                headers={"Content-Disposition": "attachment;filename=bib.csv"}
            )

@app.route('/bibformat', methods=['POST'])
def bibformat():
    endpoint_code = "bibformat"
    usage.add_log(endpoint_code)
    if request.method == "POST":
        usage.add_log("POST")
        input_bibformat = request.form["input_bibformat"]
        if (
            not valid_bibformat(input_bibformat)
        ):
            usage.add_log("Failed validation.")
            return jsonify({"processed_text": os.getenv("VALIDATION_MESSAGE")})
        else:
            usage.add_log("Passed validation.")
            lines_bib = input_bibformat.splitlines()
            df = bib_to_df(lines_bib)
            output_bibformat = extract_entries(df)
            return jsonify({"processed_text": f"{output_bibformat}"})

@app.route('/arxivversions', methods=['POST'])
def arxivversions():
    endpoint_code = "arxivversions"
    usage.add_log(endpoint_code)
    if request.method == "POST":
        usage.add_log("POST")
        input_arxivversions = request.form['input_arxivversions']
        if (
            not valid_arxivversions(input_arxivversions)
        ):
            usage.add_log("Failed validation.")
            return jsonify({"processed_text": os.getenv("VALIDATION_MESSAGE")})
        else:
            usage.add_log("Passed validation.")
            lines_bib = input_arxivversions.splitlines()
            df = bib_to_df(lines_bib)
            df, num_unique_matches = add_arXiv_versions(df)
            usage.add_log(f"{num_unique_matches} out of {len(df)} entries "
                "had unique matches on arXiv.")
            output = extract_entries(df)
            return jsonify({"processed_text": f"{output}"})
    
# @app.route('/exampleAJAX', methods=['GET', 'POST'])
# def exampleAJAX():
#     if request.method == 'POST':
#         input_1 = request.form['exampleAJAX_input_1']
#         input_2 = request.form['exampleAJAX_input_2']
#         return jsonify({
#             "processed_text": f"Received: {input_1} and {input_2}"
#         })

@app.route("/crash")
def crash():
    1 / 0

@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500

if __name__ == '__main__':
    app.run(debug=True)
