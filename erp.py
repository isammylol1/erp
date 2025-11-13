import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Inicialização do banco de dados
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
    
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    
    if df.empty:
        print("Não há produtos cadastrados!")
        return
    
    print("\n--- LISTA DE PRODUTOS ---")
    print("-" * 80)
    
    
    df_display = df.copy()
    df_display['preco'] = df_display['preco'].apply(lambda x: f"R$ {x:.2f}")
    df_display['estoque_status'] = df_display['quantidade'].apply(
        lambda x: '⭐ BAIXO' if x < 5 else '✓ OK'
    )
    
    print(df_display[['id', 'nome', 'categoria', 'preco', 'quantidade', 'estoque_status']].to_string(index=False))
    print("-" * 80)
    
    total_produtos = len(df)
    produtos_baixo_estoque = len(df[df['quantidade'] < 5])
    valor_total_estoque = (df['preco'] * df['quantidade']).sum()
    
    print(f"\n RESUMO:")
    print(f"Total de produtos: {total_produtos}")
    print(f"Produtos com estoque baixo: {produtos_baixo_estoque}")
    print(f"Valor total em estoque: R$ {valor_total_estoque:.2f}")

def carregar_dados_pandas():
    conn = sqlite3.connect('estoque.db')
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

def mostrar_dashboard():
    df = carregar_dados_pandas()
    
    if df.empty:
        print("Não há dados para mostrar no dashboard!")
        return
    
    plt.style.use('default')
    sns.set_palette("husl")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('DASHBOARD DE ESTOQUE - ANÁLISE COMPLETA', fontsize=16, fontweight='bold')
    
    if not df.empty:
        categorias_count = df['categoria'].value_counts()
        axes[0, 0].pie(categorias_count.values, labels=categorias_count.index, autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('Distribuição por Categoria')
        
    if not df.empty:
        produtos_estoque = df.nlargest(10, 'quantidade')[['nome', 'quantidade']]
        axes[0, 1].bar(produtos_estoque['nome'], produtos_estoque['quantidade'])
        axes[0, 1].set_title('Top 10 Produtos em Estoque')
        axes[0, 1].tick_params(axis='x', rotation=45)

    if not df.empty:
        df['valor_total'] = df['preco'] * df['quantidade']
        valor_por_categoria = df.groupby('categoria')['valor_total'].sum()
        axes[1, 0].bar(valor_por_categoria.index, valor_por_categoria.values)
        axes[1, 0].set_title('Valor Total por Categoria (R$)')
        axes[1, 0].tick_params(axis='x', rotation=45)

    if not df.empty:
        estoque_baixo = df[df['quantidade'] < 5][['nome', 'quantidade']]
        if not estoque_baixo.empty:
            axes[1, 1].bar(estoque_baixo['nome'], estoque_baixo['quantidade'], color='red')
            axes[1, 1].set_title('Produtos com Estoque Baixo (< 5 unidades)')
            axes[1, 1].tick_params(axis='x', rotation=45)
        else:
            axes[1, 1].text(0.5, 0.5, 'Todos os produtos\ncom estoque adequado', 
                           ha='center', va='center', fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Alertas de Estoque')
    
    plt.tight_layout()
    plt.show()

    print("\n" + "="*60)
    print("           ESTATÍSTICAS DETALHADAS DO ESTOQUE")
    print("="*60)
    
    print(f"\nRESUMO GERAL:")
    print(f"Total de produtos: {len(df)}")
    print(f"Total de categorias: {df['categoria'].nunique()}")
    print(f"Valor total em estoque: R$ {(df['preco'] * df['quantidade']).sum():.2f}")
    print(f"Produtos com estoque baixo: {len(df[df['quantidade'] < 5])}")
    
    print(f"\nESTATÍSTICAS POR CATEGORIA:")
    stats_categoria = df.groupby('categoria').agg({
        'id': 'count',
        'quantidade': 'sum',
        'preco': ['mean', 'sum']
    }).round(2)
    
    print(stats_categoria)

def exportar_para_excel():
    df = carregar_dados_pandas()
    
    if df.empty:
        print("Não há dados para exportar!")
        return
    
    filename = f"estoque_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Produtos', index=False)
        
        resumo = pd.DataFrame({
            'Metrica': ['Total Produtos', 'Total Categorias', 'Valor Total Estoque', 'Produtos Estoque Baixo'],
            'Valor': [
                len(df),
                df['categoria'].nunique(),
                (df['preco'] * df['quantidade']).sum(),
                len(df[df['quantidade'] < 5])
            ]
        })
        resumo.to_excel(writer, sheet_name='Resumo', index=False)
    
    print(f"Dados exportados para {filename}")

def mostrar_menu():
    """Função que mostra o menu principal atualizado"""
    print("\n" + "="*50)
    print("        SISTEMA DE ESTOQUE ERP")
    print("="*50)
    print("1. Cadastrar novo produto")
    print("2. Excluir produto") 
    print("3. Ver todos os produtos")
    print("4. Dashboard e Estatísticas")
    print("5. Exportar para Excel")
    print("6. Sair do programa")
    print("="*50)

if __name__ == "__main__":
    print("Bem-vindo ao Sistema de Estoque Avançado!")
    inicializar_banco()

    while True:
        mostrar_menu()
        
        opcao = input("\nEscolha uma opção (1-6): ")
        
        if opcao == "1":
            cadastrar_produto()
        elif opcao == "2":
            excluir_produto()
        elif opcao == "3":
            ver_produtos()
        elif opcao == "4":
            mostrar_dashboard()
        elif opcao == "5":
            exportar_para_excel()
        elif opcao == "6":
            print("Obrigado por usar o sistema.")
            break
        else:
            print("Opção inválida! Digite 1, 2, 3, 4, 5 ou 6.")
