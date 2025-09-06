import os
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask, request, render_template, Response
from yescite import YesCite, bib_to_df
import io

load_dotenv()

sentry_sdk.init(
    dsn=os.environ.get("GLITCHTIP_DSN"),
    integrations=[FlaskIntegration()]
)

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():

    input_bbl = ''
    input_bib = ''
    output_yescite = ''
    output_aliases_used = ''
    output_aliases_unused = ''

    if request.method == 'POST':    
        input_bbl = request.form.get('input_bbl')
        input_bib = request.form.get('input_bib')
        lines_bbl = input_bbl.splitlines()
        lines_bib = input_bib.splitlines()
        yc = YesCite(lines_bbl, lines_bib)
        output_yescite = '\n'.join(yc.yescite)
        output_aliases_used = yc.aliases_used
        output_aliases_unused = yc.aliases_unused
    
    return render_template(
        'index.html', 
        input_bbl=input_bbl, 
        input_bib=input_bib, 
        output_yescite=output_yescite,
        output_aliases_used=output_aliases_used,
        output_aliases_unused=output_aliases_unused,
    )

@app.route('/download_csv', methods=['POST'])
def download_csv():
    input_bib = request.form.get('input_bib', '')
    lines_bib = input_bib.splitlines()
    df = bib_to_df(lines_bib)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return Response(
        csv_buffer,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=bib.csv"}
    )

@app.route("/crash")
def crash():
    1 / 0

@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500

if __name__ == '__main__':
    app.run(debug=False)
