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
    return render_template('index.html')


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_projetoHotel'

mysql = MySQL(app)

# Listar hóspedes
@app.route('/hospedes', methods=['GET'])
def hospedes():
    nome_filtro = request.args.get('nome', '')  
    ordem = request.args.get('ordenar', 'asc')  

    if ordem == 'asc':
        order_by = 'ASC'
    else:
        order_by = 'DESC'

    cur = mysql.connection.cursor()

    if nome_filtro:
        cur.execute("SELECT * FROM hospede WHERE nome LIKE %s ORDER BY nome " + order_by, (nome_filtro + '%',))
    else:
        cur.execute("SELECT * FROM hospede ORDER BY nome " + order_by)

    hospedes = cur.fetchall()  
    cur.close()

    return render_template('hospedes.html', hospedes=hospedes)


@app.route('/add_hospede', methods=['GET', 'POST'])
def add_hospede():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        email = request.form['email']

       
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM hospede WHERE cpf = %s OR email = %s", (cpf, email))
        existing_hospede = cur.fetchone()
        
        if existing_hospede:
            flash= ('Já existe um hóspede com este CPF ou e-mail. Tente novamente com dados diferentes.')
            return render_template('add_hospedes.html', flash=flash)

        
        cur.execute("INSERT INTO hospede (nome, cpf, telefone, email) VALUES (%s, %s, %s, %s)",
                    (nome, cpf, telefone, email))
        mysql.connection.commit()
        cur.close()

        flash('Hóspede adicionado com sucesso!', 'success')
        return redirect(url_for('hospedes'))  

    return render_template('add_hospedes.html')  


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

        flash('Dados do hóspede atualizados com sucesso!', 'success')
        return redirect(url_for('hospedes'))

    return render_template('edit_hospede.html', hospede=hospede)


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


@app.route('/quartos', methods=['GET','POST'])
def quartos():
    numero_filtro = request.args.get('numero', '')  
    ordem = request.args.get('ordenar', 'asc')  

    if ordem == 'asc':
        order_by = 'ASC'
    else:
        order_by = 'DESC'

    cursor = mysql.connection.cursor()

    if numero_filtro:
        cursor.execute("SELECT * FROM quarto WHERE numero LIKE %s ORDER BY numero " + order_by, (numero_filtro + '%',))
    else:
        cursor.execute("SELECT * FROM quarto ORDER BY numero " + order_by)

    quartos = cursor.fetchall()
    cursor.close()
    return render_template('quartos.html', quartos=quartos)

@app.route('/add_quartos', methods=['GET','POST'])
def add_quartos():
    if request.method == 'POST':
        numero = request.form['numero']
        tipo = request.form['tipo']
        preco = request.form['preco']
        capacidade = request.form['capacidade']
        descricao = request.form['descricao']

        cursor=mysql.connection.cursor()
        cursor.execute(f"SELECT * FROM quarto WHERE numero = {numero}")
        existing_quarto = cursor.fetchone()
        
        if existing_quarto:
            flash = ('Já existe um quarto com este número. Tente novamente com dados difierentes.')
            return render_template('add_quartos.html', flash=flash)
        
        cursor.execute("INSERT INTO quarto (numero, tipo, preco, capacidade, descricao) VALUES (%s, %s, %s, %s, %s)", (numero, tipo, preco, capacidade, descricao))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('quartos'))
    return render_template('add_quartos.html')

@app.route('/excluir_quarto/<int:id>', methods=['GET', 'POST'])
def excluir_quarto(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM quarto WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Hóspede excluído com sucesso!')
    return redirect(url_for('quartos'))

if __name__ == '__main__':
    app.run(debug=True)  
