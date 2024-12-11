from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # validar o login
        return redirect(url_for('main'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # registrar o usuário
        return redirect(url_for('preferencias'))
    return render_template('register.html')

@app.route('/preferencias')
def preferencias():
    return render_template('prefer.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/lista')
def lista():
    return render_template('lista.html')

@app.route('/perfil')
def perfil():
    user = {
        'name': 'Mubi Seridoense',
        'email': 'mubiseridoense@email.com'
    }
    return render_template('perfil.html', user=user)

@app.route('/comunidade')
def comunidade():
    return render_template('comunidade.html')

@app.route('/configuracoes')
def configuracoes():
    return render_template('configuracoes.html')

if __name__ == '__main__':
    app.run(debug=True)
