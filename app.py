from flask import Flask, render_template, redirect, request, url_for, flash
#from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models import obter_conexão
from flask_mysqldb import MySQL

#login_manager = LoginManager()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'senhadoprojeto'

#login_manager.init_app(app)
#@login_manager.user_loader
#def load_user(user_id):
  #  return User.get(user_id)

@app.route('/')
def index():
    return 'Bem vindo ao projeto de reservas de hoteís. '


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'senha'
app.config['MYSQL_DB'] = 'db_projetoHotel'

mysql = MySQL(app)

# Listar hóspedes
@app.route('/')
def listar_hospedes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM hospede")
    hospedes = cur.fetchall()
    cur.close()
    return render_template('hospedes.html', hospedes=hospedes)

# Adcionar hóspede
@app.route('/add_hospede', methods=['GET', 'POST'])
def add_hospede():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO hospede (nome, cpf, telefone, email) VALUES (%s, %s, %s, %s)",
                    (nome, cpf, telefone, email))
        mysql.connection.commit()
        cur.close()

        flash('Hóspede adicionado com sucesso!')
        return redirect(url_for('hospedes'))

    return render_template('add_hospede.html')

# Editar um hóspede
@app.route('/edit_hospede/<int:id>', methods=['GET', 'POST'])
def edit_hospede(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM hospede WHERE id = %s", (id,))
    hospede = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE hospede SET nome = %s, cpf = %s, telefone = %s, email = %s WHERE id = %s",
                    (nome, cpf, telefone, email, id))
        mysql.connection.commit()
        cur.close()

        flash('Dados do hóspede atualizados com sucesso!')
        return redirect(url_for('hospedes'))

    return render_template('hospedes.html', hospede=hospede)

# Excluir hóspede
@app.route('/excluir_hospede/<int:id>', methods=['GET', 'POST'])
def excluir_hospede(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM hospede WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Hóspede excluído com sucesso!')
    return redirect(url_for('hospedes'))

if __name__ == '__main__':
    app.run(debug=True)  