import socket
from bd import Banco


def processar_insercao(conexao, banco):

    try:
        # Recebe o tamanho do nome:
        tam_nome_byte = conexao.recv(1)
        if not tam_nome_byte:
            return False
        tam_nome = int.from_bytes(tam_nome_byte, "big")

        # Recebe o nome:
        nome_bytes = conexao.recv(tam_nome)
        nome = nome_bytes.decode()

        # Recebe o tamanho da classe:
        tam_classe_byte = conexao.recv(1)
        tam_classe = int.from_bytes(tam_classe_byte, "big")

        # Recebe a classe:
        classe_bytes = conexao.recv(tam_classe)
        classe = classe_bytes.decode()

        # Recebe o tamanho da especie:
        tam_especie_byte = conexao.recv(1)
        tam_especie = int.from_bytes(tam_especie_byte, "big")

        # Recebe a especie:
        especie_bytes = conexao.recv(tam_especie)
        especie = especie_bytes.decode()

        # Recebe o nível (1 byte):
        nivel_byte = conexao.recv(1)
        nivel = int.from_bytes(nivel_byte, "big")

        # Adiciona no banco usando o método adicionado em bd.py:
        id_inserido = banco.adicionar(nome, classe, especie, nivel)

        # Prepara a resposta:
        # Resposta de inserção: 1 byte opcode (valor 1) + 1 byte para o id inserido (sinalizado)
        resposta = (1).to_bytes(1, "big") + id_inserido.to_bytes(1, "big", signed=True)
        print("Resposta Inserção:", resposta, "\n")
        conexao.send(resposta)
    except Exception as e:
        print("Erro ao processar inserção:", e)
        # Em caso de erro, envie o opcode de erro (6)
        conexao.send((6).to_bytes(1, "big"))
    return True


def processar_busca(conexao, banco):

    try:
        # Recebe o id de busca:
        id_byte = conexao.recv(1)
        if not id_byte:
            return False
        id_busca = int.from_bytes(id_byte, "big")

        # Busca o registro no banco:
        registro = banco.buscar(id_busca)
        if registro is None:
            # Não encontrado – envia opcode de erro (6)
            conexao.send((6).to_bytes(1, "big"))
        else:
            # O registro retornado é uma tupla: (id, nome, classe, especie, nivel)
            id_reg, nome, classe, especie, nivel = registro

            # Codifica nome, classe, especie
            nome_enc = nome.encode()
            classe_enc = classe.encode()
            especie_enc = especie.encode()

            # Monta o pacote resposta:
            resposta = (1).to_bytes(1, "big")  # opcode 1 para resposta de sucesso
            resposta += id_reg.to_bytes(1, "big")  # id do registro
            resposta += len(nome_enc).to_bytes(1, "big") + nome_enc
            resposta += len(classe_enc).to_bytes(1, "big") + classe_enc
            resposta += len(especie_enc).to_bytes(1, "big") + especie_enc
            resposta += nivel.to_bytes(1, "big")
            print("Resposta Busca:", resposta, "\n")
            conexao.send(resposta)
    except Exception as e:
        print("Erro ao processar busca:", e)
        conexao.send((6).to_bytes(1, "big"))
    return True


def processar_atualizacao(conexao, banco):
    """
    Formato do pacote de atualização (requisição):
      - 1 byte: opcode (valor 3)
      - 1 byte: id do registro a atualizar
      - 1 byte: tamanho do nome (nNome)
      - nNome bytes: novo nome
      - 1 byte: tamanho da classe (nClasse)
      - nClasse bytes: nova classe
      - 1 byte: tamanho da espécie (nEspecie)
      - nEspecie bytes: nova espécie
      - 1 byte: novo nível
    """
    try:
        id_byte = conexao.recv(1)
        if not id_byte:
            return False
        id_atualizar = int.from_bytes(id_byte, "big")
        tam_nome_byte = conexao.recv(1)
        tam_nome = int.from_bytes(tam_nome_byte, "big")
        nome = conexao.recv(tam_nome).decode()
        tam_classe_byte = conexao.recv(1)
        tam_classe = int.from_bytes(tam_classe_byte, "big")
        classe = conexao.recv(tam_classe).decode()
        tam_especie_byte = conexao.recv(1)
        tam_especie = int.from_bytes(tam_especie_byte, "big")
        especie = conexao.recv(tam_especie).decode()
        nivel_byte = conexao.recv(1)
        nivel = int.from_bytes(nivel_byte, "big")
        registro_atualizado = banco.atualizar(
            id_atualizar, nome, classe, especie, nivel
        )
        if registro_atualizado is None:
            conexao.send((6).to_bytes(1, "big"))
        else:
            id_reg, nome_reg, classe_reg, especie_reg, nivel_reg = registro_atualizado
            nome_enc = nome_reg.encode()
            classe_enc = classe_reg.encode()
            especie_enc = especie_reg.encode()
            resposta = (1).to_bytes(1, "big")
            resposta += id_reg.to_bytes(1, "big")
            resposta += len(nome_enc).to_bytes(1, "big") + nome_enc
            resposta += len(classe_enc).to_bytes(1, "big") + classe_enc
            resposta += len(especie_enc).to_bytes(1, "big") + especie_enc
            resposta += nivel_reg.to_bytes(1, "big")
            print("Resposta Atualização:", resposta, "\n")
            conexao.send(resposta)
    except Exception as e:
        print("Erro ao processar atualização:", e)
        conexao.send((6).to_bytes(1, "big"))
    return True


def processar_remocao(conexao, banco):
    """
    Formato do pacote de remoção (requisição):
      - 1 byte: opcode (valor 4)
      - 1 byte: id do registro a remover
    Resposta (sucesso):
      - 1 byte: opcode (valor 4) + 1 byte: id removido
    Em caso de erro, envia 1 byte com opcode 6.
    """
    try:
        id_byte = conexao.recv(1)
        if not id_byte:
            return False
        id_remover = int.from_bytes(id_byte, "big")
        sucesso = banco.remover(id_remover)
        if sucesso:
            resposta = (4).to_bytes(1, "big") + id_remover.to_bytes(1, "big")
            print("Resposta Remoção:", resposta, "\n")
            conexao.send(resposta)
        else:
            conexao.send((6).to_bytes(1, "big"))
    except Exception as e:
        print("Erro ao processar remoção:", e)
        conexao.send((6).to_bytes(1, "big"))
    return True


def main():
    HOST = "127.0.0.1"
    PORT = 50000

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen(5)
    print("Servidor rodando em {}:{}".format(HOST, PORT))

    while True:
        try:
            conexao, endereco = servidor.accept()
            print("Conexão estabelecida com:", endereco)
            banco = Banco()
            while True:
                # Recebe o opcode (1 byte) que indica a operação desejada:
                opcode_byte = conexao.recv(1)
                if not opcode_byte:
                    break  # Conexão encerrada pelo cliente
                opcode = int.from_bytes(opcode_byte, "big")

                if opcode == 1:
                    # Inserção
                    if not processar_insercao(conexao, banco):
                        break
                elif opcode == 2:
                    # Busca
                    if not processar_busca(conexao, banco):
                        break
                elif opcode == 3:
                    if not processar_atualizacao(conexao, banco):
                        break
                elif opcode == 4:
                    if not processar_remocao(conexao, banco):
                        break
                elif opcode == 5:
                    # Saída: encerra a conexão sem fechar o socket do servidor
                    print("Cliente solicitou desconexão.")
                    break
                else:
                    # Para opcodes não reconhecidos, envia erro (6)
                    conexao.send((6).to_bytes(1, "big"))
            conexao.close()
            print("Conexão encerrada com:", endereco)
        except Exception as e:
            print("Erro na conexão:", e)
            break

    servidor.close()


if __name__ == "__main__":
    main()
