from flask import Flask, render_template, redirect, request, url_for, flash
#from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models import obter_conexão
from flask_mysqldb import MySQL
from datetime import datetime

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
            flash('Já existe um hóspede com este CPF ou e-mail. Tente novamente com dados diferentes.')
            return render_template('add_hospedes.html')

        
        cur.execute("INSERT INTO hospede (nome, cpf, telefone, email) VALUES (%s, %s, %s, %s)",
                    (nome, cpf, telefone, email))
        mysql.connection.commit()
        cur.close()

        flash('Hóspede adicionado com sucesso!', 'success')
        return redirect(url_for('hospedes'))  

    return render_template('add_hospedes.html')  


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


@app.route('/excluir_hospede/<int:id>', methods=['GET', 'POST'])
def excluir_hospede(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM hospede WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Hóspede excluído com sucesso!')
    return redirect(url_for('hospedes'))



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


@app.route('/reservas', methods=['GET', 'POST'])
def reservas():
    checkin_filter = request.form.get('checkin_filter')  
    ordem = request.form.get('ordem', 'asc')  

    cur = mysql.connection.cursor()
    
    query = """
        SELECT r.id, h.nome AS hospede, q.numero AS quarto, r.checkin, r.checkout, r.total 
        FROM reserva r
        JOIN hospede h ON r.hos_id = h.id
        JOIN quarto q ON r.quarto_id = q.id
    """

    conditions = []
    params = []

    if checkin_filter:
        conditions.append("r.checkin = %s")
        params.append(checkin_filter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += f" ORDER BY r.checkin {ordem}"

    cur.execute(query, tuple(params))
    reservas = cur.fetchall()
    cur.close()

    reservas_formatadas = []
    for reserva in reservas:
        checkin = reserva[3].strftime('%d/%m/%Y')  
        checkout = reserva[4].strftime('%d/%m/%Y')  
        reservas_formatadas.append(reserva[:3] + (checkin, checkout, reserva[5]))

    return render_template('reservas.html', reservas=reservas_formatadas, checkin_filter=checkin_filter, ordem=ordem)




@app.route('/add_reserva', methods=['GET', 'POST'])
def add_reserva():
    if request.method == 'POST':
        hos_id = request.form['hos_id']
        quarto_id = request.form['quarto_id']
        checkin = request.form['checkin']
        checkout = request.form['checkout']

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT * FROM reserva 
            WHERE quarto_id = %s AND 
            (
                (checkin BETWEEN %s AND %s) OR 
                (checkout BETWEEN %s AND %s) OR 
                (checkin <= %s AND checkout >= %s)
            )
        """, (quarto_id, checkin, checkout, checkin, checkout, checkin, checkout))
        conflito = cur.fetchone()

        if conflito:
            flash('O quarto já está reservado para o período selecionado. Escolha outras datas ou outro quarto.', 'error')
            cur.close()
            return redirect(url_for('add_reserva'))

        checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
        dias = (checkout_date - checkin_date).days

        if dias <= 0:
            flash('A data de check-out deve ser posterior à data de check-in.', 'error')
            cur.close()
            return redirect(url_for('add_reserva'))


        cur.execute("SELECT preco FROM quarto WHERE id = %s", (quarto_id,))
        preco_quarto = cur.fetchone()

        if not preco_quarto:
            flash('Quarto inválido selecionado. Tente novamente.', 'error')
            cur.close()
            return redirect(url_for('add_reserva'))

        total = preco_quarto[0] * dias

        cur.execute("""
            INSERT INTO reserva (hos_id, quarto_id, checkin, checkout, total) 
            VALUES (%s, %s, %s, %s, %s)
        """, (hos_id, quarto_id, checkin, checkout, total))
        mysql.connection.commit()
        cur.close()

        flash('Reserva adicionada com sucesso!', 'success')
        return redirect(url_for('reservas'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nome FROM hospede")
    hospedes = cur.fetchall()
    cur.execute("SELECT id, numero FROM quarto")
    quartos = cur.fetchall()
    cur.close()

    return render_template('add_reserva.html', hospedes=hospedes, quartos=quartos)



@app.route('/excluir_reserva/<int:id>', methods=['GET', 'POST'])
def excluir_reserva(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reserva WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Reserva excluída com sucesso!')
    return redirect(url_for('reservas'))

if __name__ == '__main__':
    app.run(debug=True)  
