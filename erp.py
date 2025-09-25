lista_produtos = []

contador_id = 1

def mostrar_menu():
    """Função que mostra o menu principal"""
    print("\n" + "="*50)
    print("        SISTEMA DE ESTOQUE ERP")
    print("="*50)
    print("1. Cadastrar novo produto")
    print("2. Excluir produto")
    print("3. Ver todos os produtos")
    print("4. Sair do programa")
    print("="*50)

def cadastrar_produto():
    """Função para cadastrar um novo produto"""
    global contador_id  
    
    print("\n--- CADASTRANDO NOVO PRODUTO ---")
    
    nome = input("Digite o nome do produto: ")
    categoria = input("Digite a categoria: ")
    
    try:
        preco = float(input("Digite o preço: R$ "))
        quantidade = int(input("Digite a quantidade: "))
    except:
        print("ERRO: Digite números válidos para preço e quantidade!")
        return  
    
    novo_produto = {
        'id': contador_id,
        'nome': nome,
        'categoria': categoria, 
        'preco': preco,
        'quantidade': quantidade
    }
    
    lista_produtos.append(novo_produto)
    print(f"Produto '{nome}' cadastrado com sucesso! ID: {contador_id}")
    
    contador_id += 1

def excluir_produto():
    """Função para excluir um produto"""
    
    if len(lista_produtos) == 0:
        print("Não há produtos cadastrados!")
        return
    
    print("\n--- EXCLUINDO PRODUTO ---")
    
    # Mostro os produtos para o usuário ver
    ver_produtos()
    
    # Peço o ID do produto a ser excluído
    try:
        id_excluir = int(input("\nDigite o ID do produto que quer excluir: "))
    except:
        print("Digite um número válido!")
        return
    
    # Procuro o produto na lista
    produto_encontrado = None
    for produto in lista_produtos:
        if produto['id'] == id_excluir:
            produto_encontrado = produto
            break
    
    if produto_encontrado:
        confirmacao = input(f"Tem certeza que quer excluir '{produto_encontrado['nome']}'? (s/n): ")
        if confirmacao.lower() == 's':
            lista_produtos.remove(produto_encontrado)
            print("Produto excluído com sucesso!")
        else:
            print("Exclusão cancelada.")
    else:
        print("Produto não encontrado!")

def ver_produtos():
    """Função para mostrar todos os produtos"""
    
    if len(lista_produtos) == 0:
        print("Não há produtos cadastrados!")
        return
    
    print("\n--- LISTA DE PRODUTOS ---")
    print("-" * 60)
    
    # Cabeçalho da tabela
    print(f"{'ID':<4} {'NOME':<20} {'CATEGORIA':<15} {'PREÇO':<10} {'ESTOQUE':<8}")
    print("-" * 60)
    
    # Mostro cada produto da lista
    for produto in lista_produtos:
        # Verifico se o estoque está baixo
        estoque_status = ""
        if produto['quantidade'] < 5:
            estoque_status = "⭐ BAIXO"
        
        print(f"{produto['id']:<4} {produto['nome']:<20} {produto['categoria']:<15} "
              f"R$ {produto['preco']:<7.2f} {produto['quantidade']:<8} {estoque_status}")
    
    print("-" * 60)
    
    # Mostro algumas estatísticas simples
    total_produtos = len(lista_produtos)
    produtos_baixo_estoque = 0
    
    for produto in lista_produtos:
        if produto['quantidade'] < 5:
            produtos_baixo_estoque += 1
    
    print(f"\n📊 RESUMO:")
    print(f"Total de produtos: {total_produtos}")
    print(f"Produtos com estoque baixo: {produtos_baixo_estoque}")

# PROGRAMA PRINCIPAL
print("Bem-vindo ao Sistema de Estoque!")

# Loop principal do programa
while True:
    mostrar_menu()
    
    opcao = input("\nEscolha uma opção (1-4): ")
    
    if opcao == "1":
        cadastrar_produto()
    elif opcao == "2":
        excluir_produto() 
    elif opcao == "3":
        ver_produtos()
    elif opcao == "4":
        print("Obrigado por usar o sistema! Até mais!")
        break
    else:
        print("Opção inválida! Digite 1, 2, 3 ou 4.")




    