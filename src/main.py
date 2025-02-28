from flask import Flask, send_from_directory, render_template

app = Flask(__name__, template_folder='../src/templates', static_folder='../src/static')

#! serve our important routes
@app.route('/')
def index():
    return render_template('index.html')

#! serve our static files
#! routes go /content/static/<path>
@app.route('/content/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 