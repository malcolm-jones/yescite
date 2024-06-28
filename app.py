from flask import Flask, request, render_template
from yescite import lines_bib_to_keep

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():

    input_bbl = ''
    input_bib = ''
    output_text = ''

    if request.method == 'POST':    
        input_bbl = request.form.get('input_bbl')
        input_bib = request.form.get('input_bib')
        lines_bbl = input_bbl.splitlines()
        lines_bib = input_bib.splitlines()
        new_bib = lines_bib_to_keep(lines_bbl, lines_bib)
        output_text = '\n'.join(new_bib)
    
    return render_template(
        'index.html', 
        input_bbl=input_bbl, 
        input_bib=input_bib, 
        output_text=output_text,
    )

if __name__ == '__main__':
    app.run(debug=True)
