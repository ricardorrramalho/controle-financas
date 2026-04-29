# Gerenciador de Financas Pessoais

Projeto em Python para registrar receitas, despesas e acompanhar o saldo.

Ele roda pelo terminal e usa SQLite, entao nao precisa instalar banco de dados nem
nenhuma biblioteca externa.

## Funcionalidades

- Adicionar receitas e despesas
- Escolher categoria da transacao
- Listar todas as transacoes
- Remover uma transacao pelo ID
- Ver saldo total
- Gerar relatorio mensal com resumo por categoria

## Como rodar

No terminal, entre na pasta do projeto:

```bash
cd C:\Users\Usuário\Documents\pythonprojeto
```

Depois rode:

```bash
python app.py
```

Se o comando `python` nao funcionar no seu computador, tente:

```bash
py app.py
```

## Banco de dados

O arquivo `financas.db` e criado automaticamente na primeira vez que o app roda.
Ele fica na propria pasta do projeto.

## Estrutura

```text
pythonprojeto/
  app.py
  README.md
```
