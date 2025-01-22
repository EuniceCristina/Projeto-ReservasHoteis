import pymysql
#from flask_login import UserMixin

def obter_conexão():
    db_config = {
        'user' : 'root',
        'password' : '',
        'host' : 'localhost',
        'database' : 'db_projetoHotel'
    }
    return pymysql.connect(**db_config)

class Hospede():
    id : str 

    def __init__(self, nome, cpf, telefone, email):
        self.nome = nome 
        self.cpf = cpf
        self.telefone = telefone
        self.email = email

class Quarto():
    id : str 
    def __init__(self, numero, tipo, preco, capacidade, descricao):
        self.numero = numero
        self.tipo = tipo
        self.preco = preco
        self.capacidade = capacidade
        self.descricao = descricao

class Reserva():
    id : str 
    def __init__(self, hos_id, checkin, checkout, total):
        self.hos_id = hos_id
        self.checkin = checkin
        self.checkout = checkout
        self.total =total

    