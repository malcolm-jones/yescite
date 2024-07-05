from flask import Flask, request, render_template
from yescite import YesCite

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():

    input_bbl = ''
    input_bib = ''
    output_yescite = ''

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

if __name__ == '__main__':
    app.run(debug=True)
