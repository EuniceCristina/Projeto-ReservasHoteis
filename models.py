from flask_login import UserMixin
from database.db_config import obter_conexao


class User(UserMixin):
    def __init__(self, id, name, email, telephone, password):
        self.id = id
        self.name = name
        self.email = email
        self.telephone = telephone
        self.password = password

    @staticmethod
    def get(user_id):
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("SELECT nome,cpf,telefone,email,senha,tipo FROM hospedesWHERE hos_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conexao.close()
        if result:
            return User(*result) 
        return None