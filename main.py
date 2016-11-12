import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash
)


app = Flask(__name__)


class Produto:
    def __init__(self):
        self.id = None
        self.nome = None
        self.imagem = None
        self.valor = None
        self.quantidade = None


class Carrinho:
    def __init__(self):
        self.produtos = []

    def add_produto(self, produto):
        self.produtos.append(produto)

    def remove_produto(self, produto_id):
        for p in self.produtos:
            if p.id == produto_id:
                self.produtos.remove(p)
                return p


def conectar_db():
    return sqlite3.connect('banco.db')


def gerar_produto(linha):
    produto = Produto()
    produto.id = linha[0]
    produto.nome = linha[1]
    produto.imagem = linha[2]
    produto.valor = linha[3]
    produto.quantidade = linha[4]
    return produto


def todos_produtos():
    conexao = conectar_db()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM PRODUTO")
    resultado = cursor.fetchall()
    conexao.close()

    produtos = []
    for linha in resultado:
        produto = gerar_produto(linha)
        produtos.append(produto)
    return produtos


def buscar_produto(produto_id):
    conexao = conectar_db()
    cursor = conexao.cursor()
    sql = "SELECT * FROM PRODUTO WHERE ID = {}".format(produto_id)
    cursor.execute(sql)
    resultado = cursor.fetchone()
    conexao.close()

    return gerar_produto(resultado)


def salvar_produto(produto):
    conexao = conectar_db()
    cursor = conexao.cursor()
    sql = """
    INSERT INTO PRODUTO(NOME, IMAGEM, VALOR, QUANTIDADE)
    VALUES ('{}', '{}', {}, {})""".format(
        produto.nome,
        produto.imagem,
        produto.valor,
        produto.quantidade
    )
    cursor.execute(sql)
    cursor.commit()
    conexao.close()


def finalizar_carrinho(carrinho):
    conexao = conectar_db()
    cursor = conexao.cursor()
    for produto in carrinho.produtos:
        sql = """
        UPDATE PRODUTO
        SET QUANTIDADE = QUANTIDADE - 1
        WHERE ID = {}
        """.format(produto.id)
        cursor.execute(sql)
    cursor.commit()
    conexao.close()


@app.route("/")
def index():
    produtos = todos_produtos()
    return render_template('index.html', produtos=produtos)


@app.route("/carrinho/add/<int:produto_id>")
def adicionar_carrinho(produto_id):
    if not 'carrinho' in session:
        session['carrinho'] = Carrinho()

    carrinho = session['carrinho']
    produto = buscar_produto(produto_id)
    carrinho.add(produto)
    session['carrinho'] = carrinho
    flash(
        "Produto {} Adicionado ao Carrinho".format(produto.nome)
    )
    return redirect(url_for('index'))


@app.route("/carrinho")
def listar_carrinho():
    if 'carrinho' in session:
        produtos = session['carrinho'].produtos
    else:
        produtos = []
    return render_template('carrinho.html', produtos=produtos)


@app.route("/carrinho/delete/<int:produto_id>")
def deletar_carrinho(produto_id):
    carrinho = session['carrinho']
    produto = carrinho.remove_produto(produto_id)
    session['carrinho'] = carrinho
    flash("Produto {} Removido do Carrinho".format(produto.nome))
    return redirect(url_for('listar_carrinho'))


@app.route("/carrinho/finalizar")
def finalizar_compra():
    carrinho = session['carrinho']
    finalizar_carrinho(carrinho)
    flash("Compra Finalizada! Muito Obrigado e Volte Sempre :D")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
