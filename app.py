import sqlite3
from datetime import datetime
from pathlib import Path


ARQUIVO_BANCO = Path(__file__).parent / "financas.db"

CATEGORIAS = [
    "alimentacao",
    "transporte",
    "moradia",
    "saude",
    "educacao",
    "lazer",
    "salario",
    "outros",
]


def conectar():
    return sqlite3.connect(ARQUIVO_BANCO)


def preparar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL
        )
        """
    )

    conexao.commit()
    conexao.close()


def moeda(valor):
    texto = f"R$ {valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def mostrar_titulo():
    print("\n" + "=" * 44)
    print("   GERENCIADOR DE FINANCAS PESSOAIS")
    print("=" * 44)


def mostrar_menu():
    print("\n1 - Adicionar transacao")
    print("2 - Listar transacoes")
    print("3 - Remover transacao")
    print("4 - Mostrar saldo total")
    print("5 - Relatorio mensal")
    print("0 - Sair")


def ler_opcao():
    return input("\nEscolha uma opcao: ").strip()


def escolher_tipo():
    while True:
        print("\nTipo da transacao:")
        print("1 - Receita")
        print("2 - Despesa")
        opcao = input("Digite 1 ou 2: ").strip()

        if opcao == "1":
            return "receita"
        if opcao == "2":
            return "despesa"

        print("Opcao invalida. Tenta de novo.")


def escolher_categoria():
    print("\nCategorias:")
    for posicao, categoria in enumerate(CATEGORIAS, start=1):
        print(f"{posicao} - {categoria}")

    while True:
        escolha = input("Escolha uma categoria: ").strip()

        if escolha.isdigit():
            indice = int(escolha) - 1
            if 0 <= indice < len(CATEGORIAS):
                return CATEGORIAS[indice]

        print("Categoria invalida. Digite o numero que aparece na lista.")


def ler_valor():
    while True:
        entrada = input("Valor: R$ ").strip().replace(",", ".")

        try:
            valor = float(entrada)
            if valor > 0:
                return valor
            print("O valor precisa ser maior que zero.")
        except ValueError:
            print("Valor invalido. Exemplo valido: 25,90")


def ler_data():
    hoje = datetime.now().strftime("%d/%m/%Y")
    texto = input(f"Data (dd/mm/aaaa) [hoje: {hoje}]: ").strip()

    if texto == "":
        return datetime.now().strftime("%Y-%m-%d")

    try:
        data = datetime.strptime(texto, "%d/%m/%Y")
        return data.strftime("%Y-%m-%d")
    except ValueError:
        print("Data invalida. Vou usar a data de hoje.")
        return datetime.now().strftime("%Y-%m-%d")


def adicionar_transacao():
    print("\n--- Nova transacao ---")
    tipo = escolher_tipo()
    descricao = input("Descricao: ").strip()

    if descricao == "":
        descricao = "Sem descricao"

    categoria = escolher_categoria()
    valor = ler_valor()
    data = ler_data()

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        """
        INSERT INTO transacoes (tipo, descricao, categoria, valor, data)
        VALUES (?, ?, ?, ?, ?)
        """,
        (tipo, descricao, categoria, valor, data),
    )
    conexao.commit()
    conexao.close()

    print("\nTransacao adicionada com sucesso.")


def buscar_transacoes(mes=None, ano=None):
    conexao = conectar()
    cursor = conexao.cursor()

    if mes and ano:
        inicio = f"{ano:04d}-{mes:02d}-01"
        if mes == 12:
            fim = f"{ano + 1:04d}-01-01"
        else:
            fim = f"{ano:04d}-{mes + 1:02d}-01"

        cursor.execute(
            """
            SELECT id, tipo, descricao, categoria, valor, data
            FROM transacoes
            WHERE data >= ? AND data < ?
            ORDER BY data DESC, id DESC
            """,
            (inicio, fim),
        )
    else:
        cursor.execute(
            """
            SELECT id, tipo, descricao, categoria, valor, data
            FROM transacoes
            ORDER BY data DESC, id DESC
            """
        )

    transacoes = cursor.fetchall()
    conexao.close()
    return transacoes


def mostrar_transacoes(transacoes):
    if not transacoes:
        print("\nNenhuma transacao encontrada.")
        return

    print("\nID   DATA         TIPO      CATEGORIA      VALOR        DESCRICAO")
    print("-" * 70)

    for item in transacoes:
        id_transacao, tipo, descricao, categoria, valor, data = item
        data_brasil = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
        print(
            f"{id_transacao:<4} {data_brasil:<10}  {tipo:<8}  "
            f"{categoria:<13} {moeda(valor):<12} {descricao}"
        )


def listar_transacoes():
    transacoes = buscar_transacoes()
    mostrar_transacoes(transacoes)


def remover_transacao():
    listar_transacoes()
    print("\n--- Remover transacao ---")

    try:
        id_transacao = int(input("Digite o ID que deseja remover: ").strip())
    except ValueError:
        print("ID invalido.")
        return

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT descricao, valor FROM transacoes WHERE id = ?", (id_transacao,))
    transacao = cursor.fetchone()

    if transacao is None:
        conexao.close()
        print("Nao encontrei nenhuma transacao com esse ID.")
        return

    descricao, valor = transacao
    confirma = input(
        f"Remover '{descricao}' no valor de {moeda(valor)}? (s/n): "
    ).strip().lower()

    if confirma == "s":
        cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
        conexao.commit()
        print("Transacao removida.")
    else:
        print("Remocao cancelada.")

    conexao.close()


def calcular_totais(transacoes):
    receitas = 0
    despesas = 0

    for transacao in transacoes:
        tipo = transacao[1]
        valor = transacao[4]

        if tipo == "receita":
            receitas += valor
        else:
            despesas += valor

    return receitas, despesas, receitas - despesas


def mostrar_saldo_total():
    transacoes = buscar_transacoes()
    receitas, despesas, saldo = calcular_totais(transacoes)

    print("\n--- Saldo total ---")
    print(f"Receitas: {moeda(receitas)}")
    print(f"Despesas: {moeda(despesas)}")
    print(f"Saldo:    {moeda(saldo)}")


def ler_mes_ano():
    agora = datetime.now()

    try:
        mes = input(f"Mes [atual: {agora.month:02d}]: ").strip()
        ano = input(f"Ano [atual: {agora.year}]: ").strip()

        mes = agora.month if mes == "" else int(mes)
        ano = agora.year if ano == "" else int(ano)

        if 1 <= mes <= 12:
            return mes, ano

        print("Mes invalido. Vou usar o mes atual.")
        return agora.month, agora.year
    except ValueError:
        print("Entrada invalida. Vou usar o mes atual.")
        return agora.month, agora.year


def gastos_por_categoria(transacoes):
    categorias = {}

    for transacao in transacoes:
        tipo = transacao[1]
        categoria = transacao[3]
        valor = transacao[4]

        if tipo == "despesa":
            categorias[categoria] = categorias.get(categoria, 0) + valor

    return categorias


def relatorio_mensal():
    print("\n--- Relatorio mensal ---")
    mes, ano = ler_mes_ano()
    transacoes = buscar_transacoes(mes, ano)
    receitas, despesas, saldo = calcular_totais(transacoes)

    print(f"\nResumo de {mes:02d}/{ano}")
    print("-" * 26)
    print(f"Receitas: {moeda(receitas)}")
    print(f"Despesas: {moeda(despesas)}")
    print(f"Saldo:    {moeda(saldo)}")

    categorias = gastos_por_categoria(transacoes)

    if categorias:
        print("\nDespesas por categoria:")
        for categoria, total in sorted(categorias.items()):
            print(f"- {categoria}: {moeda(total)}")

    mostrar_transacoes(transacoes)


def main():
    preparar_banco()

    while True:
        mostrar_titulo()
        mostrar_menu()
        opcao = ler_opcao()

        if opcao == "1":
            adicionar_transacao()
        elif opcao == "2":
            listar_transacoes()
        elif opcao == "3":
            remover_transacao()
        elif opcao == "4":
            mostrar_saldo_total()
        elif opcao == "5":
            relatorio_mensal()
        elif opcao == "0":
            print("\nAte mais. Cuida bem do seu dinheiro :)")
            break
        else:
            print("\nOpcao invalida.")

        input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()
