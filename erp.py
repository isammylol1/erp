import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

def inicializar_banco():
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

def cadastrar_produto():
    print("\n--- CADASTRANDO NOVO PRODUTO ---")
    
    nome = input("Digite o nome do produto: ")
    categoria = input("Digite a categoria: ")
    
    try:
        preco = float(input("Digite o preço: R$ "))
        quantidade = int(input("Digite a quantidade: "))
    except:
        print("ERRO: Digite números válidos para preço e quantidade!")
        return
    
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO produtos (nome, categoria, preco, quantidade)
        VALUES (?, ?, ?, ?)
    ''', (nome, categoria, preco, quantidade))
    
    conn.commit()
    produto_id = cursor.lastrowid
    conn.close()
    print(f"Produto '{nome}' cadastrado com sucesso! ID: {produto_id}")

def excluir_produto():
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM produtos")
    total = cursor.fetchone()[0]
    
    if total == 0:
        print("Não há produtos cadastrados!")
        conn.close()
        return
    
    print("\n--- EXCLUINDO PRODUTO ---")
    ver_produtos()
    
    try:
        id_excluir = int(input("\nDigite o ID do produto que quer excluir: "))
    except:
        print("Digite um número válido!")
        conn.close()
        return
    
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_excluir,))
    produto = cursor.fetchone()
    
    if produto:
        confirmacao = input(f"Tem certeza que quer excluir '{produto[1]}'? (s/n): ")
        if confirmacao.lower() == 's':
            cursor.execute("DELETE FROM produtos WHERE id = ?", (id_excluir,))
            conn.commit()
            print("Produto excluído com sucesso!")
        else:
            print("Exclusão cancelada.")
    else:
        print("Produto não encontrado!")
    
    conn.close()

def ver_produtos():
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    
    if not produtos:
        print("Não há produtos cadastrados!")
        conn.close()
        return
    
    print("\n--- LISTA DE PRODUTOS ---")
    print("-" * 80)
    
    print(f"{'id':<4} {'nome':<20} {'categoria':<15} {'preco':<10} {'quantidade':<12} {'estoque_status'}")
    print("-" * 80)
    
    total_produtos = 0
    produtos_baixo_estoque = 0
    valor_total_estoque = 0.0
    
    for produto in produtos:
        id_prod, nome, categoria, preco, quantidade, data_cadastro = produto
        preco_formatado = f"R$ {preco:.2f}"
        estoque_status = 'BAIXO' if quantidade < 5 else '✓ OK'
        
        print(f"{id_prod:<4} {nome:<20} {categoria:<15} {preco_formatado:<10} {quantidade:<12} {estoque_status}")
        
        total_produtos += 1
        if quantidade < 5:
            produtos_baixo_estoque += 1
        valor_total_estoque += preco * quantidade
    
    print("-" * 80)
    
    print(f"\n RESUMO:")
    print(f"Total de produtos: {total_produtos}")
    print(f"Produtos com estoque baixo: {produtos_baixo_estoque}")
    print(f"Valor total em estoque: R$ {valor_total_estoque:.2f}")
    conn.close()
    
def mostrar_dashboard():
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('DASHBOARD DE ESTOQUE', fontsize=16, fontweight='bold')
   
    cursor.execute("SELECT categoria, COUNT(*) FROM produtos GROUP BY categoria")
    cats, qtds = zip(*cursor.fetchall())
    axes[0, 0].pie(qtds, labels=cats, autopct='%1.1f%%')
    axes[0, 0].set_title('Distribuição por Categoria')

    cursor.execute("SELECT nome, quantidade FROM produtos ORDER BY quantidade DESC LIMIT 10")
    nomes, qtds = zip(*cursor.fetchall())
    axes[0, 1].bar(nomes, qtds)
    axes[0, 1].set_title('Top 10 em Estoque')
    axes[0, 1].tick_params(axis='x', rotation=45)

    cursor.execute("SELECT categoria, SUM(preco * quantidade) FROM produtos GROUP BY categoria")
    cats, vals = zip(*cursor.fetchall())
    axes[1, 0].bar(cats, vals)
    axes[1, 0].set_title('Valor por Categoria (R$)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    cursor.execute("SELECT nome, quantidade FROM produtos WHERE quantidade < 5")
    estoque_baixo = cursor.fetchall()
    if estoque_baixo:
        nomes, qtds = zip(*estoque_baixo)
        axes[1, 1].bar(nomes, qtds, color='red')
        axes[1, 1].tick_params(axis='x', rotation=45)
    else:
        axes[1, 1].text(0.5, 0.5, 'Estoque OK', ha='center', va='center', fontsize=14)
    axes[1, 1].set_title('Estoque Baixo (<5)')
    
    plt.tight_layout()
    plt.show()

    cursor.execute("SELECT COUNT(*), COUNT(DISTINCT categoria), SUM(preco * quantidade) FROM produtos")
    total_prod, total_cat, valor_total = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade < 5")
    estoque_baixo_count = cursor.fetchone()[0]
    
    print(f"\nRESUMO:")
    print(f"Produtos: {total_prod} | Categorias: {total_cat}")
    print(f"Valor total: R$ {valor_total:.2f} | Estoque baixo: {estoque_baixo_count}")
    
    conn.close()
def mostrar_menu():
    print("\n" + "="*50)
    print("        SISTEMA DE ESTOQUE ERP")
    print("="*50)
    print("1. Cadastrar novo produto")
    print("2. Excluir produto") 
    print("3. Ver todos os produtos")
    print("4. Dashboard e Estatísticas")
    print("6. Sair do programa")
    print("="*50)

if __name__ == "__main__":
    print("Bem-vindo ao Sistema de Estoque ERP.")
    inicializar_banco()

    while True:
        mostrar_menu()
        
        opcao = input("\nEscolha uma opção (1-5): ")
        
        if opcao == "1":
            cadastrar_produto()
        elif opcao == "2":
            excluir_produto()
        elif opcao == "3":
            ver_produtos()
        elif opcao == "4":
            mostrar_dashboard()
        elif opcao == "5":
            print("Obrigado por usar o sistema.")
            break
        else:
            print("Opção inválida! Digite 1, 2, 3, 4 ou 5.")

