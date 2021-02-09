from flask import Flask, render_template, render_template_string, request
import os
import lipsum


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'test.sqlite'),
    )

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            injection = render_template_string(request.form['inject'])
            return render_template('index.html', inject=injection)

        return render_template('index.html')

    return app
