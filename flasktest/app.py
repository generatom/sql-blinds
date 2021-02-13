from flask import Flask, render_template, render_template_string, request
from flask import redirect, url_for
import os
import lipsum
from db import get_db


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'test.sqlite'),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    import db
    db.init_app(app)

    @app.route('/', methods=['GET', 'POST'])
    def index(v=""):
        db = get_db()
        if request.method == 'POST':
            inject_string = request.form['inject']
            injection = render_template_string(inject_string)
            db.add_search(inject_string)
            return render_template('index.html', inject=injection,
                                   searches=db.get_searches())

        return render_template('index.html', searches=db.get_searches(),
                                value=v)

    @app.route('/reset')
    def reset():
        db = get_db()
        db.reset()

        return redirect(url_for('index'))

    return app
