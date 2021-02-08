from flask import Flask, render_template


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'test.sqlite'),
    )

    @app.route('/')
    def index():
        return render_template('index')

    @app.route('/check', methods=['GET', 'POST'])
    def check():
        if request.method == 'POST':
