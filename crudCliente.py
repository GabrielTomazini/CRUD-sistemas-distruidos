import socket

# opcodes definidos:
# 1 - Inserir
# 2 - Buscar
# 3 - Atualizar
# 4 - Remover
# 5 - Sair
# 6 - Erro

# Se forem utilizar atualização parcial, lembrem que devem adaptar o pacote, pois há campos que podem não existir
# Sugetão nesse caso: indiquem quantos campos serão atualizados, qual dado está sendo enviado, o tamanho (se necessário)
# e o campo.
# Por exemplo, suponha que nome será identificado com 1, idade com 2, endereço com 3 e CEP com 4. Se quiserem atualizar só o
# nome, montem uma estrutura que mande 3 15 1 1 5 teste, onde 3 é o opcode de atualizar, 15 é o id de quem será atualizado,
# 1 é a quantidade de campos modificados, 1 é o campo enviado (nome), 5 é a quantidade de caracteres e 'teste' é o novo nome.
# Caso não queiram lidar com isso, forcem o envio de todos os campos

# Pacotes definidos até aqui
# Inserção (requisição):
# 1 byte opcode (valor 1)
# 1 byte para o tamanho do nome (nNome, sem sinal, formato big), nNome bytes para o nome
# 1 byte para idade, sem sinal, formato big
# 1 byte para o tamanho do endereco (nEnd, sem sinal, formato big), nEnd bytes para o endereço
# 8 bytes para o CEP
# Inserção (resposta):
# 1 byte opcode (valor 1)
# 1 byte para o id inserido, sinalizado, formato big
#
# Busca (requisição):
# 1 byte para opcode (valor 2)
# 1 byte para id, sem sinal, formato big
# Busca (resposta, sucesso)
# 1 byte opcode (valor 1)
# 1 byte para id, sem sinal, formato big
# 1 byte para o tamanho do nome (nNome, sem sinal, formato big), nNome bytes para o nome
# 1 byte para idade, sem sinal, formato big
# 1 byte para o tamanho do endereco (nEnd, sem sinal, formato big), nEnd bytes para o endereço
# 8 bytes para o CEP
# Inserção (resposta):
# 1 byte opcode (valor 1)
# 1 byte para o id inserido, sinalizado, formato big
# Busca (resposta, erro)
# 1 byte para opcode (valor 6)

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(("127.0.0.1", 50000))

opcao = None
while opcao != 5:

    opcao = int(
        input(
            "Digite 1 para inserir, 2 para buscar, 3 para atualizar, 4 para remover, 5 pra sair: "
        )
    )
    match opcao:
        case 1:
            nome = input("Digite nome: ")
            classe = input("Digite classe: ")
            especie = input("Digite especie: ")
            nivel = int(input("Digite nível: "))
            msg = opcao.to_bytes(1, "big")
            msg = msg + len(nome.encode()).to_bytes(1, "big") + nome.encode()
            msg = msg + len(classe.encode()).to_bytes(1, "big") + classe.encode()
            msg = msg + len(especie.encode()).to_bytes(1, "big") + especie.encode()
            msg = msg + nivel.to_bytes(1, "big")
            print("Mensagem Inserção: ", msg, "\n")
            cliente.send(msg)
            opcode = cliente.recv(1)
            id = cliente.recv(1)
            id = int.from_bytes(id, "big", signed=True)
            print(id)
        case 2:
            id = int(input("Digite id de busca: "))
            msg = opcao.to_bytes(1, "big") + id.to_bytes(1, "big")
            print("Mensagem Busca: ", msg, "\n")
            cliente.send(msg)
            opcode = cliente.recv(1)
            opcode = int.from_bytes(opcode, "big")
            if opcode == 6:
                print("Não encontrado")
            else:
                id = cliente.recv(1)
                id = int.from_bytes(id, "big")

                tam_nome = cliente.recv(1)
                tam_nome = int.from_bytes(tam_nome, "big")
                nome = cliente.recv(tam_nome).decode()

                tam_classe = cliente.recv(1)
                tam_classe = int.from_bytes(tam_classe, "big")
                classe = cliente.recv(tam_classe).decode()

                tam_especie = cliente.recv(1)
                tam_especie = int.from_bytes(tam_especie, "big")
                especie = cliente.recv(tam_especie).decode()

                nivel = cliente.recv(1)
                nivel = int.from_bytes(nivel, "big")

                print(
                    "Dados encontrados: ID: ",
                    id,
                    " Nome: ",
                    nome,
                    " Classe: ",
                    classe,
                    " Raça: ",
                    especie,
                    " nível: ",
                    nivel,
                )
        case 3:
            # Atualizar
            id = int(input("Digite o id para atualizar: "))
            nome = input("Digite novo nome: ")
            classe = input("Digite nova classe: ")
            especie = input("Digite nova espécie: ")
            nivel = int(input("Digite novo nível: "))
            msg = opcao.to_bytes(1, "big") + id.to_bytes(1, "big")
            msg += len(nome.encode()).to_bytes(1, "big") + nome.encode()
            msg += len(classe.encode()).to_bytes(1, "big") + classe.encode()
            msg += len(especie.encode()).to_bytes(1, "big") + especie.encode()
            msg += nivel.to_bytes(1, "big")
            print("Mensagem Atualização: ", msg, "\n")
            cliente.send(msg)
            opcode_resp = int.from_bytes(cliente.recv(1), "big")
            if opcode_resp == 6:
                print("Atualização falhou")
            else:
                id_resp = int.from_bytes(cliente.recv(1), "big")
                tam_nome = int.from_bytes(cliente.recv(1), "big")
                nome_resp = cliente.recv(tam_nome).decode()
                tam_classe = int.from_bytes(cliente.recv(1), "big")
                classe_resp = cliente.recv(tam_classe).decode()
                tam_especie = int.from_bytes(cliente.recv(1), "big")
                especie_resp = cliente.recv(tam_especie).decode()
                nivel_resp = int.from_bytes(cliente.recv(1), "big")
                print(
                    f"Atualização realizada: ID: {id_resp}, Nome: {nome_resp}, Classe: {classe_resp}, Espécie: {especie_resp}, Nível: {nivel_resp}"
                )
        case 4:
            # Remover
            id = int(input("Digite o id para remover: "))
            msg = opcao.to_bytes(1, "big") + id.to_bytes(1, "big")
            print("Mensagem Remoção: ", msg, "\n")
            cliente.send(msg)
            opcode_resp = int.from_bytes(cliente.recv(1), "big")
            if opcode_resp == 6:
                print("Remoção falhou")
            else:
                id_removido = int.from_bytes(cliente.recv(1), "big")
                print(f"Remoção realizada para o ID: {id_removido}")
        case 5:
            break

cliente.close()
