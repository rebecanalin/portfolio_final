from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy # Instalando a biblioteca para interagir com o DB SQLite.
import os

# Configuração do app Flask

# Define que a pasta de templates está um nível acima (..) do diretório atual do app.py
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

# Inicializa o Flask, indicando onde estão as pastas templates e static
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Configuração do Banco de Dados SQLite
# Cria um arquivo chamado 'votos.db' no mesmo diretório
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///votos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 1. Definição do Modelo do Banco de Dados (Tabela de Votos)
class Voto(db.Model):
    # ID primário autoincrementável do voto
    id = db.Column(db.Integer, primary_key=True) 
    # Campo para armazenar o ID do projeto que recebeu o voto
    projeto_id = db.Column(db.String(50), nullable=False) 
    # Campo para registrar o timestamp do voto
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self): # O repr imprime uma string clara que fornece informações essenciais sobre o objeto que está serndo impresso. 
        return f'<Voto {self.projeto_id}>'
    
class Contato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mensagem = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Contato {self.nome}>'
    

# Mapeamento para exibir nomes completos (IDs dos projetos!)
PROJECT_NAMES = {
    'ling01': 'Linguagens: Infográfico dos movimentos artísticos',
    'ling02': 'Linguagens: Protagonist - Eu',
    'nat01': 'Naturezas: Eletromagnetismo no dia-a-dia',
    'nat02': 'Naturezas: Reino das Plantas',
    'mat01': 'Matemática: Atividades Gerais',
    'tec01': 'Modelagem Conceitual de Banco de Dados',
    'tec02': 'Calculadora em Java',
    'hum01': 'Humanas: Integrada - Marcadores Sociais',
}

## ROTA PRINCIPAL: EXIBIR PÁGINA INICIAL E RANKING (Método GET)
@app.route('/')
def inicio():
    """Calcula o ranking atual e renderiza o template main.html."""
    
    # 1. Consulta ao Banco de Dados (Calcula os votos)
    ranking_data = db.session.query(
        Voto.projeto_id, 
        db.func.count(Voto.id).label('total_votos')
    ).group_by(Voto.projeto_id).order_by(db.desc('total_votos')).all()

    # 2. Processa os dados para exibição legível
    ranking_final = []
    for rank, (id_projeto, votos) in enumerate(ranking_data, 1):
        ranking_final.append({
            'rank': rank,
            'nome': PROJECT_NAMES.get(id_projeto, f'Projeto ID: {id_projeto}'), 
            'votos': votos
        })
        
    # 3. Renderiza o template, enviando a lista de ranking
    return render_template('main.html', ranking=ranking_final)

# 2. Endpoint para Receber os Votos (Rota POST)
@app.route('/votar', methods=['POST'])
def votar():
    # 1. Pega o valor enviado pelo formulário
    projeto_recebido = request.form.get('projeto_id')

    if projeto_recebido:
        # 2. Cria uma nova entrada (objeto) na tabela Voto
        novo_voto = Voto(projeto_id=projeto_recebido)
        
        # 3. Adiciona e salva no banco de dados
        db.session.add(novo_voto)
        db.session.commit()
        
        # 4. Redireciona o usuário de volta para a página principal ou de ranking
        # Redireciona para o topo da seção de votação na página principal 
        return redirect(url_for('inicio') + '#votacao')

    # Se a requisição não contiver 'projeto_id', apenas redireciona
    return redirect(url_for('inicio')) 

# 3. Rotas para cada disciplina
@app.route('/linguagens')
def linguagens_page():
    return render_template('linguagens.html') ## Renderiza o template (páginas)

@app.route('/matematica')
def matematica_page():
    return render_template('matematica.html')

@app.route('/naturezas')
def naturezas_page():
    return render_template('naturezas.html')

@app.route('/humanas')
def humanas_page():
    return render_template('humanas.html')

@app.route('/tecnico')
def tecnico_page():
    return render_template('tecnico.html')


# 4. Rota para receber as informações do formulário de contato.

@app.route('/contato', methods=['GET', 'POST'])
def enviar_contato():
    # Pega os dados recebidos do formulário
    nome_recebido = request.form.get('nome')
    email_recebido = request.form.get('email')
    mensagem_recebida = request.form.get('mensagem')

    # 2. Verifica se todos os campos foram preenchidos (opcional, mas recomendado)
    if nome_recebido and email_recebido and mensagem_recebida:
        # 3. Cria uma nova entrada (objeto) na tabela Contato
        nova_mensagem = Contato(
            nome=nome_recebido, 
            email=email_recebido, 
            mensagem=mensagem_recebida
        )

        # 4. Adiciona e salva a nova mensagem no banco de dados
        db.session.add(nova_mensagem)
        db.session.commit()
    
    # 5. Redireciona o usuário de volta para a seção de contato na página principal
    return redirect(url_for('inicio') + '#contato')

# 5. Execução do Aplicativo
if __name__ == '__main__':
    # Cria o arquivo de banco de dados e as tabelas (Execute isso uma vez!)
    with app.app_context():
        db.create_all()
    # Inicia o servidor Flask
    app.run(debug=True)

