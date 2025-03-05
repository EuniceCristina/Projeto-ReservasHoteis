from flask import Flask, render_template, redirect, request, url_for, flash
from flask_mysqldb import MySQL
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'senhadoprojeto'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(usuario_id):
    return User.get(usuario_id)


#configiração página inicial
@app.route('/index')
def index():
    user = current_user
    if user.tipo == 'administrador':
        barra = True
        return render_template('index.html', barra=barra)
    else: 
        return render_template('index.html')

#configuração do banco
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_projetoHotel'

mysql = MySQL(app)

#página login
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['senha']
        
        user = User.get_by_email(email)

        if not user:
            
            flash("E-mail não cadastrado!", "error")
            return render_template('login.html')

        if not user.senha==senha:
            
            flash("Senha incorreta!", "error")
            return render_template('login.html')

        login_user(user, remember=True)

        flash("Login realizado com sucesso!", "success")
        if user.tipo == 'usuario':
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))

  
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form['email']
        telefone = request.form['telefone']
        nome = request.form['nome']
        senha = request.form['senha']
        tipo = request.form['usuario']
        cpf = request.form['cpf']
        

        existing_user_email = User.get_by_email(email)
        existing_user_cpf = User.get_by_cpf(cpf)
        if existing_user_email:
            flash("E-mail já está em uso!", "error")
            return render_template('registro.html')
        elif existing_user_cpf:
            flash("Cpf já está em uso!", "error")
            return render_template('registro.html')
        


        

        User.create(nome=nome, email=email, telefone=telefone, senha=senha,tipo=tipo,cpf=cpf)

        
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for('login'))
    return render_template('registro.html')

#página de hospedes
@app.route('/hospedes', methods=['GET'])
@login_required
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

    user = current_user


    if not user:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("login"))

    if user.tipo == 'usuario':
        flash('Você não permissão para entrar')
        return render_template('quartos.html')
    else:
        barra = True
        return render_template('hospedes.html', hospedes=hospedes, barra=barra)

#página para adicionar hóspedes
@app.route('/add_hospede', methods=['GET', 'POST'])
@login_required
def add_hospede():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        email = request.form['email']

       
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM hospede WHERE cpf = %s",(cpf,))
        existing_cpf = cur.fetchone()

        cur.execute("SELECT * FROM hospede WHERE email = %s", (email,))
        existing_email = cur.fetchone()
        
        if existing_cpf or existing_email:
            texto=('Já existe um hóspede com este CPF ou e-mail. Tente novamente com dados diferentes.')
            return render_template('add_hospedes.html', flash=texto)

        
        cur.execute("INSERT INTO hospede (nome, cpf, telefone, email) VALUES (%s, %s, %s, %s)",
                    (nome, cpf, telefone, email))
        mysql.connection.commit()
        cur.close()

        flash ('Hóspede adicionado com sucesso!', 'success')
        return redirect(url_for('hospedes'))  

    user = current_user


    if not user:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("login"))

    if user.tipo == 'usuario':
        flash('Você não permissão para adicionar', 'error')
        return render_template('quartos.html')
    else:
        return render_template('add_hospedes.html')   

#página para editar hóspedes
@app.route('/edit_hospede/<int:id>', methods=['GET', 'POST'])
@login_required
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
    user = current_user


    if not user:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("login"))

    if user.tipo == 'usuario':
        flash('Você não permissão para editar')
        return render_template('quartos.html')
    else:
        return render_template('edit_hospede.html', hospede=hospede)

#página para excluir hóspedes
@app.route('/excluir_hospede/<int:id>', methods=['GET', 'POST'])
@login_required
def excluir_hospede(id):
    user = current_user
    if user.tipo == 'usuario':
        flash('Você não permissão para excluir','error')
        return render_template('quartos.html')
    else:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM hospede WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()

        flash('Hóspede excluído com sucesso!')
        return redirect(url_for('hospedes'))


#página dos quartos
@app.route('/quartos', methods=['GET','POST'])
@login_required
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
    user = current_user
    if user.tipo == 'administrador':
        barra = True
        return render_template('quartos.html', quartos=quartos, barra=barra)
    else: 
        return render_template('quartos.html', quartos=quartos, id=current_user.id)

#página pada adicionar novos quartos
@app.route('/add_quartos', methods=['GET','POST'])
@login_required
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
    user = current_user


    if not user:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("login"))

    if user.tipo == 'usuario':
        return render_template('quartos.html')
    else:
        return render_template('add_quartos.html')

#página para excluir quartos
@app.route('/excluir_quarto/<int:id>', methods=['GET', 'POST'])
@login_required
def excluir_quarto(id):
    user = current_user
    if user.tipo == 'administrador':

        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM quarto WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Hóspede excluído com sucesso!')
        return redirect(url_for('quartos'))
    else:
        flash('Você não ter permissão para excluir esse quarto')
        return redirect(url_for('quartos'))

@app.route('/pedir_quarto/<int:id>', methods=['GET', 'POST'])
@login_required
def pedir_quarto(id):
    user = current_user
    if user.tipo == 'administrador':

        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM quarto WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        flash('Hóspede excluído com sucesso!')
        return redirect(url_for('quartos'))
    else:
        flash('Você não ter permissão para pedir esse quarto')
        return redirect(url_for('quartos'))
    

#página de reservas
@app.route('/reservas', methods=['GET', 'POST'])
@login_required  
def reservas():
    if current_user.tipo != 'administrador':
        flash('Acesso negado. Apenas administradores podem visualizar reservas.', 'error')
        return redirect(url_for('index')) 
     
    checkin_filter = request.form.get('checkin_filter')  
    ordem = request.form.get('ordem', 'asc')  

    cur = mysql.connection.cursor()
    
    query = """
        SELECT r.id, h.nome AS hospede, q.numero AS quarto, r.checkin, 
        r.checkout, r.total, IFNULL(r.situacao, 'Pendente') AS situacao
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
        situacao = reserva[6] if reserva[6] else 'Pendente'
        reservas_formatadas.append(reserva[:3] + (checkin, checkout, reserva[5], situacao))

    return render_template('reservas.html', reservas=reservas_formatadas, checkin_filter=checkin_filter, ordem=ordem, barra=True)


@app.route('/hos_reservas', methods=['GET', 'POST'])
@login_required  
def hos_reservas():
    usuario_id = current_user.id  

    cur = mysql.connection.cursor()
    
    query = """
        SELECT r.id, q.numero AS quarto, r.checkin, r.checkout, r.total, 
        IFNULL(r.situacao, 'Pendente') AS situacao
        FROM reserva r
        JOIN quarto q ON r.quarto_id = q.id
        WHERE r.hos_id = %s
        ORDER BY r.checkin DESC
    """

    cur.execute(query, (usuario_id,))
    reservas = cur.fetchall()
    cur.close()

    reservas_formatadas = []
    for reserva in reservas:
        checkin = reserva[2].strftime('%d/%m/%Y')  
        checkout = reserva[3].strftime('%d/%m/%Y')  
        situacao = reserva[5] if reserva[5] else 'Pendente'
        reservas_formatadas.append(reserva[:2] + (checkin, checkout, reserva[4], situacao))

    return render_template('hos_reserva.html', reservas=reservas_formatadas)


#página para adicionar reservas
@app.route('/add_reserva', methods=['GET', 'POST'])
def add_reserva():
    if request.method == 'POST':
        hos_id = request.form['hos_id']
        quarto_id = request.form['quarto_id']
        checkin = request.form['checkin']
        checkout = request.form['checkout']

        cur = mysql.connection.cursor()

        try:
            checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
            checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
            dias = (checkout_date - checkin_date).days

            if dias <= 0:
                flash('A data de check-out deve ser posterior à data de check-in.', 'error')
                return redirect(url_for('add_reserva'))

            cur.execute("SELECT preco FROM quarto WHERE id = %s", (quarto_id,))
            preco_quarto = cur.fetchone()

            if not preco_quarto:
                flash('Quarto inválido selecionado. Tente novamente.', 'error')
                return redirect(url_for('add_reserva'))

            total = preco_quarto[0] * dias

            cur.execute("""
                INSERT INTO reserva (hos_id, quarto_id, checkin, checkout, total) 
                VALUES (%s, %s, %s, %s, %s)
            """, (hos_id, quarto_id, checkin, checkout, total))

            mysql.connection.commit()
            flash('Reserva adicionada com sucesso!', 'success')

        except Exception as e:
            mysql.connection.rollback()  
            if 'Erro: O quarto já está reservado para este período.' in str(e):
                flash('O quarto já está reservado para este período. Escolha outra data ou outro quarto.', 'error')
            else:
                flash('Erro ao adicionar reserva. Tente novamente.', 'error')

        finally:
            cur.close()

        return redirect(url_for('reservas'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nome FROM hospede")
    hospedes = cur.fetchall()
    cur.execute("SELECT id, numero FROM quarto")
    quartos = cur.fetchall()
    cur.close()

    return render_template('add_reserva.html', hospedes=hospedes, quartos=quartos)



#página para excluir reservas
@app.route('/excluir_reserva/<int:id>', methods=['GET', 'POST'])
def excluir_reserva(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reserva WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash('Reserva excluída com sucesso!')
    user = current_user
    if user.tipo == 'usuario':
        return redirect(url_for('hos_reservas'))
    else: 
        return redirect(url_for('reservas'))
    

#página dos relátorios avançados
@app.route('/relatorios')
def relatorios():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id,nome FROM hospede')
    hospedes = cur.fetchall()
    cur.close()
    user = current_user
    if user.tipo == 'usuario':
            flash('Voce não permissão para acessar relatórios','error')
            return redirect(url_for('quartos'))
    else: 
        return render_template('relatorios.html', hospedes=hospedes)

#página para relátorio total de reservas
@app.route('/total_reservas', methods=['GET','POST'])
def total_reservas():
    if request.method=='POST':
        data1 = request.form['data1']
        data2 = request.form['data2']
        cur = mysql.connect.cursor()
        cur.execute('SELECT nome, SUM(total) FROM hospede as h JOIN reserva as r ON h.id=r.hos_id WHERE checkin BETWEEN %s and %s GROUP BY nome ',(data1,data2))
        totais = cur.fetchall()
        cur.close()
        
        return render_template('total_reservas.html',totais=totais) 
    user = current_user
    if user.tipo == 'usuario':
            flash('Voce não permissão para acessar relatórios','error')
            return redirect(url_for('quartos'))
    else: 
        return render_template('total_reservas.html')
    
@app.route('/confirmar_reserva/<int:id>',methods=['POST'])
def confirmar_reserva(id):
    cur = mysql.connection.cursor()

    cur.execute("UPDATE reserva SET situacao = 'Confirmada' WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('reservas'))

@app.route('/negar_reserva/<int:id>',methods=['POST'])
def negar_reserva(id):
    cur = mysql.connection.cursor()

    cur.execute("UPDATE reserva SET situacao = 'Negada' WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('reservas'))


#página para relátorio de reservas acima de 2000,00
@app.route('/reservas_acima', methods=['GET','POST'])
def reservas_acima():
    cur = mysql.connect.cursor()
    cur.execute("SELECT nome, total FROM hospede as h JOIN reserva as r ON h.id = r.hos_id WHERE total>='2000' ")
    totais = cur.fetchall()
    cur.close()
    user = current_user
    if user.tipo == 'usuario':
            flash('Voce não permissão para acessar relatórios','error')
            return redirect(url_for('quartos'))
    else: 
        return render_template('reservas_acima.html',totais=totais)

#página para relátorio de quartos mais reservados
@app.route('/quartos_reservados', methods=['GET','POST'])
def quartos_reservados():
     if request.method=='POST':
        dias = request.form['tempo']
        cur = mysql.connect.cursor()
        dias = int(dias)  
        query = '''
        SELECT numero, COUNT(r.quarto_id) AS quartos
        FROM quarto AS q
        JOIN reserva AS r ON q.id = r.quarto_id
        WHERE checkin BETWEEN NOW() - INTERVAL %s DAY AND NOW()
        GROUP BY numero
        ORDER BY quartos DESC LIMIT 10
        '''
        cur.execute(query, (dias,))
        totais = cur.fetchall()
        cur.close()
        user = current_user
        if user.tipo == 'usuario':
            flash('Voce não permissão para acessar relatórios','error')
            return redirect(url_for('quartos'))
        else: 
            return render_template('quartos_reservados.html',totais=totais, dias=dias)

#página para relátorio de quartos não reservados
@app.route('/nao_reservados', methods=['GET','POST'])
def nao_reservados():
    cur = mysql.connect.cursor()
    query = '''
        SELECT q.numero FROM quarto as q
        WHERE q.id NOT IN (SELECT r.quarto_id FROM reserva r)
        '''
    
    cur.execute(query)
    totais = cur.fetchall()
    cur.close()
    if request.method=='POST':
        return render_template('nao_reservados.html',totais=totais)
    user = current_user
    if user.tipo == 'usuario':
            flash('Voce não permissão para acessar relatórios','error')
            return redirect(url_for('quartos'))
    else: 
        return render_template('nao_reservados.html',totais=totais)


@app.route('/logout')
@login_required
def logout():
    
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)  