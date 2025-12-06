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

    input_bbl = ''
    input_bib_YesCite = ''
    output_yescite = ''
    output_aliases_used = ''
    output_aliases_unused = ''

    if request.method == 'POST':    
        endpoint_code = "YesCite"
        usage.add_log(endpoint_code)
        input_bbl = request.form.get('input_bbl')
        input_bib_YesCite = request.form.get('input_bib_YesCite')
        if (
            not valid_yescite(input_bbl, input_bib_YesCite)
        ):
            usage.add_log(": ".join([
                endpoint_code, 
                "Input failed validation.",
            ]))
            return render_template(
                'index.html',  
                message_yescite=os.getenv("VALIDATION_MESSAGE"),
                scrollToAnchor='message-yescite',
            )
        lines_bbl = input_bbl.splitlines()
        lines_bib = input_bib_YesCite.splitlines()
        yc = YesCite(lines_bbl, lines_bib)
        output_yescite = '\n'.join(yc.yescite)
        output_aliases_used = yc.aliases_used
        output_aliases_unused = yc.aliases_unused
    
    return render_template(
        'index.html', 
        input_bbl=input_bbl, 
        input_bib_YesCite=input_bib_YesCite, 
        output_yescite=output_yescite,
        output_aliases_used=output_aliases_used,
        output_aliases_unused=output_aliases_unused,
    )

@app.route('/download_csv', methods=['POST'])
def download_csv():
    endpoint_code = "bib2csv"
    usage.add_log(endpoint_code)
    input_bib_to_csv = request.form.get('input_bib_to_csv', '')
    if (
        not valid_bibtocsv(input_bib_to_csv)
    ):
        usage.add_log(": ".join([
            endpoint_code,
            "Input failed validation.",
        ]))
        return render_template(
            'index.html', 
            input_bib_to_csv=input_bib_to_csv, 
            message_bibtocsv=os.getenv("VALIDATION_MESSAGE"),
            scrollToAnchor='message-bibtocsv',
        )
    else:
        lines_bib = input_bib_to_csv.splitlines()
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
    input_bibformat = request.form.get('input_bibformat', '')
    if (
        not valid_bibformat(input_bibformat)
    ):
        usage.add_log(": ".join([
            endpoint_code,
            "Input failed validation.",
        ]))
        return render_template(
            'index.html', 
            input_bibformat=input_bibformat, 
            message_bibformat=os.getenv("VALIDATION_MESSAGE"),
            scrollToAnchor='message-bibformat',
        )
    else:
        lines_bib = input_bibformat.splitlines()
        df = bib_to_df(lines_bib)
        output_bibformat = extract_entries(df)
        return render_template(
            'index.html', 
            input_bibformat=input_bibformat, 
            output_bibformat=output_bibformat,
            scrollToAnchor='output_bibformat',
        )

@app.route('/arxivversions', methods=['POST'])
def arxivversions():
    endpoint_code = "arxivversions"
    usage.add_log(endpoint_code)
    input_arxivversions = request.form.get('input_arxivversions', '')
    if (
        not valid_arxivversions(input_arxivversions)
    ):
        usage.add_log(": ".join([
            endpoint_code,
            "Input failed validation.",
        ]))
        return render_template(
            'index.html', 
            input_arxivversions=input_arxivversions, 
            message_arxivversions=os.getenv("VALIDATION_MESSAGE"),
            scrollToAnchor='message-arxivversions',
        )
    else:
        lines_bib = input_arxivversions.splitlines()
        df = bib_to_df(lines_bib)
        df, num_unique_matches = add_arXiv_versions(df)
        usage.add_log(": ".join([
            endpoint_code,
            f"{num_unique_matches} out of {len(df)} entries had unique " 
            "matches on arXiv.",
        ]))
        output_arxivversions = extract_entries(df)
        return render_template(
            'index.html', 
            input_arxivversions=input_arxivversions, 
            output_arxivversions=output_arxivversions,
            scrollToAnchor='output_arxivversions',
        )
    
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
    app.run(debug=False)
