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

@app.route('/preferencias', methods=['POST', 'GET'])
def preferencias():
    if request.method == 'POST':
        # obter preferências selecionadas
        generos_selecionados = request.form.getlist('generos')
        print(f"Gêneros selecionados: {generos_selecionados}")  # Apenas para debug
        # pode salvar os dados no banco ou realizar outro processamento
        # redirecionar para o main após salvar
        return redirect(url_for('main'))
    return render_template('preferencias.html')

@app.route('/main')
def main():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)
