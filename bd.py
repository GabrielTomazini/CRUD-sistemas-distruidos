import sqlite3


class Banco:

    def __init__(self):
        self.conexao = sqlite3.connect("personagem.db")
        cursor = self.conexao.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS personagem(id INTEGER PRIMARY KEY, nome, classe, especie, nivel INTEGER)"
        )
        self.conexao.commit()
        cursor.close()

    def adicionar(self, nome, classe, especie, nivel):
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO personagem(nome, classe, especie, nivel) VALUES(?,?,?,?)",
            (nome, classe, especie, nivel),
        )
        if cursor.rowcount > 0:
            id = cursor.lastrowid
        else:
            id = None
        self.conexao.commit()
        cursor.close()
        return id

    # retorna uma tupla contendo todos os campos, na mesma ordem de criação do banco
    def buscar(self, id):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM personagem WHERE id = ?", (id,))
        retorno = cursor.fetchone()
        cursor.close()
        return retorno

    def atualizar(self, id, nome=None, classe=None, especie=None, nivel=None):
        dados = self.buscar(id)
        if dados is not None:
            nome = nome if nome else dados[1]
            classe = classe if classe else dados[2]
            especie = especie if especie else dados[3]
            nivel = nivel if nivel else dados[5]
            cursor = self.conexao.cursor()
            cursor.execute(
                "UPDATE personagem SET nome = ?, classe = ?, especie = ?, nivel = ? WHERE id = ?",
                (nome, classe, especie, nivel, id),
            )
            self.conexao.commit()
            # um registro foi alterado
            if cursor.rowcount > 0:
                dados = self.buscar(id)
            # nenhum registro foi alterado, atualização falhou
            else:
                dados = None
            cursor.close()
            return dados
        else:
            return None

    def remover(self, id):
        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM personagem WHERE id = ?", (id,))
        self.conexao.commit()
        sucesso = cursor.rowcount > 0
        cursor.close()
        return sucesso
