# -*- coding: utf-8 -*-

import ssl
import json
import re
from datetime import datetime
import sys
import warnings
import os
import time

# Compatibilidade de rede; requer Python moderno para o cliente OpenAI
try:
    import urllib.request
    import urllib.error
    from urllib.parse import quote
except ImportError:
    pass

# Desabilitar verificação SSL para compatibilidade
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURACOES - API LLM7 (compativel com OpenAI)
# Nao use uma chave embutida no codigo. Defina LLM7_API_KEY no ambiente.
# ============================================================
LLM7_BASE_URL = os.environ.get("LLM7_BASE_URL", "https://api.llm7.io/v1")
LLM7_MODEL = os.environ.get("LLM7_MODEL", "fast")
LLM7_TIMEOUT = int(os.environ.get("LLM7_TIMEOUT", "90"))

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else "."
QUOTES_FILE = os.path.join(BASE_DIR, "quotes_cache.json")
GLOBAL_OUTPUT_FILE = os.path.join(BASE_DIR, "global.txt")
NATIONAL_OUTPUT_FILE = os.path.join(BASE_DIR, "nacional.txt")

# User-Agent para evitar bloqueios
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:52.0) Gecko/20100101 Firefox/52.0'
}

# TOPICOS MONITORADOS - foco ampliado em sobrevivencia e continuidade de servicos
# Cada consulta procura noticias; os resultados nao confirmam, por si so, uma ameaca.
TOPICS = {
    "crise_alimentar": "escassez alimentos OR falta alimentos OR inseguranca alimentar OR preco alimentos",
    "agricultura_colheitas": "quebra safra OR seca agricultura OR pragas lavouras OR fertilizantes escassez",
    "cadeia_abastecimento": "cadeia abastecimento OR desabastecimento OR falta produtos OR logistica cargas",
    "crise_energia": "apagao OR falta energia OR racionamento energia OR rede eletrica falha",
    "petroleo": "preco petroleo OR oferta petroleo OR crise combustiveis OR falta gasolina diesel",
    "gas_combustivel": "falta gas de cozinha OR abastecimento gas OR escassez combustivel",
    "crise_agua": "racionamento agua OR falta agua OR crise hidrica OR reservatorios seca",
    "qualidade_agua": "agua contaminada OR alerta qualidade agua OR contaminacao abastecimento",
    "guerras": "guerra OR conflito armado OR escalada militar OR ataques infraestrutura",
    "terrorismo": "atentado OR ameaca terrorista OR alerta seguranca publica",
    "conflitos_civis": "disturbios civis OR estado emergencia OR confrontos protestos",
    "colapso_economico": "crise bancaria OR inflacao OR desemprego OR recessao economia",
    "mercados_financas": "falha pagamentos bancarios OR bolsa queda OR controle capital OR crise credito",
    "greve": "greve OR paralisacao OR manifestacao OR servicos publicos interrompidos",
    "greve_caminhoneiros": "greve caminhoneiros OR bloqueio rodovias OR paralizacao cargas",
    "transporte_publico": "interrupcao transporte publico OR aeroportos cancelamentos OR ferrovias greve",
    "portos_comercio": "porto congestionado OR fechamento porto OR rota maritima interrompida OR frete",
    "ciberataque": "ciberataque OR ransomware OR ataque sistemas publicos OR falha digital",
    "telecomunicacoes": "falha telecomunicacoes OR interrupcao internet OR queda rede celular",
    "infraestrutura": "falha infraestrutura critica OR interrupcao servicos essenciais OR pane sistemas",
    "desastre_natural": "terremoto OR furacao OR inundacao OR deslizamento OR tsunami",
    "climatico": "onda de calor OR frio extremo OR tempestade severa OR evento climatico extremo",
    "incendios_florestais": "incendio florestal OR evacuacao incendio OR fumaca qualidade do ar",
    "vulcoes": "erupcao vulcanica OR alerta vulcanico OR cinzas vulcanicas",
    "pandemia": "surto doenca OR epidemia OR pandemia OR emergencia sanitaria OR transmissao comunitaria",
    "virus": "virus emergente OR surto viral OR variante viral OR transmissao humano humano",
    "nipah": "Nipah virus OR virus Nipah OR surto Nipah",
    "hantavirus": "hantavirus OR hantavirose OR sindrome pulmonar por hantavirus",
    "ebola_marburg": "Ebola virus OR surto Ebola OR virus Marburg OR febre hemorragica Marburg",
    "gripe_aviaria_h5n1": "H5N1 OR gripe aviaria H5N1 OR influenza aviaria humana",
    "influenza_h1n1": "H1N1 OR influenza A H1N1 OR gripe suina",
    "covid_sars": "COVID-19 OR SARS-CoV-2 OR nova variante coronavirus OR SARS OR MERS-CoV",
    "mpox_lassa_zika": "mpox OR variola dos macacos OR virus Lassa OR Zika virus",
    "outros_virus_emergentes": "chikungunya OR febre amarela OR virus Oropouche OR encefalite viral OR novo virus emergente",
    "doencas_animais": "doenca gado OR gripe aviaria animais OR peste suina OR mortalidade animais",
    "saude_publica": "falta medicamentos OR falta insumos hospitalares OR hospitais lotados",
    "nuclear": "acidente nuclear OR incidente radiologico OR alerta radiacao",
    "quimico_industrial": "vazamento quimico OR acidente industrial OR contaminacao toxica",
    "poluicao_ar": "poluicao do ar alerta OR fumaca toxica OR qualidade do ar perigosa",
    "refugiados": "refugiados OR deslocamento populacional OR crise humanitaria OR campos abrigo",
    "crime_seguranca": "saques OR aumento violencia crise OR alerta seguranca local",
    "moradia_abrigo": "desalojados OR abrigos emergencia OR desabrigados desastre",
    "residuos_saneamento": "falha saneamento OR esgoto contaminacao OR coleta lixo interrompida",
    "fertilizantes_insumos": "escassez fertilizantes OR preco fertilizantes OR falta sementes agricultura",
    "minerais_materiais": "escassez minerais criticos OR falta semicondutores OR escassez materiais",
    "fronteiras_sancoes": "fechamento fronteiras OR sancoes comerciais OR restricoes exportacao",
    "cortes_internet": "bloqueio internet OR apagao internet OR restricao comunicacao",
    "meteorologia": "alerta meteorologico OR alerta enchente OR alerta furacao OR alerta calor",
    "resgate_emergencia": "servicos emergencia sobrecarregados OR atraso resgate OR defesa civil alerta"
}
# TEORIAS E RELATORIOS GLOBAIS PARA CONTEXTO
GLOBAL_REPORTS = """
TEORIAS E RELATORIOS GLOBAIS PARA CONTEXTO:

AGENDA 2030:
- Objetivos de Desenvolvimento Sustentavel da ONU
- Transformacao dos sistemas alimentares globais
- Metas de energia limpa e acao climatica
- Mudancas na governanca global ate 2030

RESET GLOBAL:
- Grande Reinicio proposto pelo Forum Economico Mundial
- Transicao para economias verdes e digitais
- Reforma dos sistemas de saude e educacao
- Nova arquitetura financeira global

GLOBAL TRENDS 2040:
- Envelhecimento populacional e migracoes
- Escassez de recursos naturais
- Avancos tecnologicos disruptivos
- Fragmentacao geopolítica
- Mudancas climaticas severas

WORLD ECONOMIC FORUM PREVISOES:
- Ciberataques como ameaca top 5
- Crise de custo de vida
- Desastres naturais extremos
- Erosao da coesao social
- Poluicao e doencas ambientais
"""

def get_news(topic_query, limit=5):
    """Busca noticias com urllib (compatível Python 3.4)"""
    try:
        url = "https://news.google.com/rss/search?q={}&hl=pt-BR&gl=BR&ceid=BR:pt-419".format(quote(topic_query))
        req = urllib.request.Request(url, headers=HEADERS)
        response = urllib.request.urlopen(req, timeout=15)
        content = response.read().decode('utf-8', errors='ignore')
        response.close()

        items = []
        title_pattern = re.compile(r'<title>(.*?)</title>', re.IGNORECASE | re.DOTALL)
        titles = title_pattern.findall(content)

        for title in titles[1:limit+1]:
            clean_title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title)
            clean_title = re.sub(r'&lt;', '<', clean_title)
            clean_title = re.sub(r'&gt;', '>', clean_title)
            clean_title = re.sub(r'&amp;', '&', clean_title)
            clean_title = re.sub(r'&quot;', '"', clean_title)
            clean_title = clean_title.strip()
            if clean_title and len(clean_title) > 5:
                items.append(clean_title[:200])

        return items[:limit]
    except Exception as e:
        print("  Erro ao buscar {}: {}".format(topic_query[:20], str(e)[:50]))
        return []

def get_world_news(limit=5):
    """Busca noticias mundiais"""
    try:
        url = "https://news.google.com/rss/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JYQjBMVUpTR2dKQ1VpZ0FQAQ?hl=pt-BR&gl=BR&ceid=BR%3Apt-419"
        req = urllib.request.Request(url, headers=HEADERS)
        response = urllib.request.urlopen(req, timeout=15)
        content = response.read().decode('utf-8', errors='ignore')
        response.close()

        items = []
        title_pattern = re.compile(r'<title>(.*?)</title>', re.IGNORECASE | re.DOTALL)
        titles = title_pattern.findall(content)

        for title in titles[1:limit+1]:
            clean_title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title)
            clean_title = re.sub(r'&lt;', '<', clean_title)
            clean_title = re.sub(r'&gt;', '>', clean_title)
            clean_title = re.sub(r'&amp;', '&', clean_title)
            clean_title = re.sub(r'&quot;', '"', clean_title)
            clean_title = clean_title.strip()
            if clean_title and len(clean_title) > 5:
                items.append(clean_title[:200])

        return items[:limit]
    except Exception as e:
        print("  Erro ao buscar noticias mundiais: {}".format(str(e)[:50]))
        return []

def get_all_news():
    """Coleta noticias de todas as categorias"""
    news = {}
    print("Coletando noticias por categoria...")
    total = len(TOPICS)
    for i, (theme, query) in enumerate(TOPICS.items(), 1):
        print("  [{}/{}] Buscando: {}".format(i, total, theme.replace('_', ' ')))
        news[theme] = get_news(query, limit=5)
        time.sleep(0.5)
    print("Coletando noticias mundiais...")
    news["noticias_mundiais"] = get_world_news(5)
    return news

def get_quotes():
    """Le as cotações do arquivo cache"""
    try:
        if os.path.exists(QUOTES_FILE):
            with open(QUOTES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'dolar': data.get('dolar', 'N/A'),
                    'petroleo': data.get('petroleo', 'N/A'),
                    'bitcoin': data.get('bitcoin', 'N/A'),
                    'gasolina': data.get('gasolina', 'N/A'),
                    'ouro': data.get('ouro', 'N/A'),
                    'prata': data.get('prata', 'N/A')
                }
        return {}
    except Exception as e:
        print("Erro ao ler quotes: {}".format(str(e)))
        return {}

def extract_json_from_text(text):
    """Extrai JSON do texto da resposta"""
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def analyze_with_llm7(news, quotes):
    """Analisa noticias com a API LLM7 usando o cliente compativel com OpenAI."""
    api_key = os.environ.get("LLM7_API_KEY", "").strip()
    if OpenAI is None:
        print("Biblioteca openai ausente. Instale com: pip install openai")
        return None
    if not api_key:
        print("LLM7_API_KEY nao configurada; sera usada a analise manual.")
        return None

    news_summary = []
    for theme, items in news.items():
        if items:
            news_summary.append("{}:".format(theme.replace("_", " ").upper()))
            for item in items[:5]:
                clean_item = str(item).replace('"', "'").replace("\n", " ")
                if len(clean_item) > 180:
                    clean_item = clean_item[:177] + "..."
                news_summary.append("  - {}".format(clean_item))

    news_text = "\n".join(news_summary) if news_summary else "Nenhuma noticia relevante"
    quotes_text = """
COTACOES:
Dolar: {dolar}
Petroleo: {petroleo}
Bitcoin: {bitcoin}
Gasolina: {gasolina}
Ouro: {ouro}
Prata: {prata}
""".format(
        dolar=quotes.get("dolar", "N/A"),
        petroleo=quotes.get("petroleo", "N/A"),
        bitcoin=quotes.get("bitcoin", "N/A"),
        gasolina=quotes.get("gasolina", "N/A"),
        ouro=quotes.get("ouro", "N/A"),
        prata=quotes.get("prata", "N/A"),
    )

    prompt = """Voce e um analista de inteligencia focado em sobrevivencia, preparacao e antecipacao de crises.

CONTEXTO GLOBAL:
{global_reports}
{quotes}
NOTICIAS COLETADAS:
{news}

Analise as noticias como sinais a verificar, nao como confirmacao automatica de crise. Diferencie fatos noticiados, riscos plausiveis e incertezas. Nao invente eventos, numeros, datas ou fontes. Se as noticias nao trouxerem evidencia suficiente, diga isso explicitamente.

Responda somente com um objeto JSON valido, sem cercas de codigo ou texto adicional, usando exatamente esta estrutura:
{{"nivel_alerta":"CRITICO|ALTO|MEDIO|BAIXO","principais_ameacas":["evento observado ou risco concreto"],"previsoes_futuras":["possivel desenvolvimento identificado como possibilidade"],"preparacoes_necessarias":["acao pratica curta"],"recursos_essenciais":["recurso"],"impacto_social":["impacto possivel"],"sinais_alerta_precoce":["indicador para verificar"],"acoes_24h":["acao imediata"],"fontes_alternativas":["fonte oficial para confirmar"],"correlacoes":["relacao entre eventos, se houver"]}}

Limites: ate 5 ameacas, 3 previsoes, 5 preparacoes, 5 recursos, 5 impactos, 4 sinais, 5 acoes imediatas, 4 fontes e 4 correlacoes. Niveis: CRITICO, ALTO, MEDIO, BAIXO. Use linguagem objetiva e checklist.

Priorize: alimentos, agua, energia, combustiveis, guerras, desastres, clima, economia, greves, saude publica e pandemias, ciberataques, infraestrutura, deslocamento populacional e crises humanitarias. Considere Nipah, hantavirus, Ebola/Marburg, H5N1, H1N1, COVID-19, mpox, Lassa, Zika, Oropouche, SARS e MERS quando aparecerem nas noticias. Nao classifique um patogeno como ameaca pandemica atual sem evidencias atuais nas noticias fornecidas.
""".format(global_reports=GLOBAL_REPORTS, quotes=quotes_text, news=news_text)

    try:
        print("Enviando dados para LLM7 (modelo {})...".format(LLM7_MODEL))
        client = OpenAI(
            base_url=LLM7_BASE_URL,
            api_key=api_key,
            timeout=LLM7_TIMEOUT,
        )
        response = client.chat.completions.create(
            model=LLM7_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Voce e um analista de riscos. Retorne apenas JSON valido. "
                        "Nao invente fatos e sinalize incertezas."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1200,
        )
        content_text = (response.choices[0].message.content or "").strip()
        if not content_text:
            raise ValueError("A API retornou uma resposta vazia.")

        json_str = extract_json_from_text(content_text)
        analysis = json.loads(json_str)

        required_fields = [
            "nivel_alerta", "principais_ameacas", "previsoes_futuras",
            "preparacoes_necessarias", "recursos_essenciais", "impacto_social",
            "sinais_alerta_precoce", "acoes_24h", "fontes_alternativas", "correlacoes"
        ]
        for field in required_fields:
            if field not in analysis:
                analysis[field] = "BAIXO" if field == "nivel_alerta" else []
            if field != "nivel_alerta" and not isinstance(analysis[field], list):
                analysis[field] = [str(analysis[field])]
        level = str(analysis.get("nivel_alerta", "BAIXO")).upper()
        analysis["nivel_alerta"] = level if level in ("CRITICO", "ALTO", "MEDIO", "BAIXO") else "BAIXO"
        return analysis

    except Exception as e:
        print("Falha na analise LLM7: {}".format(str(e)[:240]))
        print("Continuando com a analise manual baseada nas noticias coletadas.")
        return None

def analyze_manual(news, quotes):
    """Fallback manual expandido: varios itens por categoria, sem depender da API."""
    alert_level = "BAIXO"
    threats, predictions, preparations = [], [], []
    resources, social_impacts, economic_impacts = [], [], []
    early_signals, actions_24h, actions_7d, actions_30d = [], [], [], []
    correlations, alternative_sources, vulnerable_groups = [], [], []

    def add(lst, value):
        if value not in lst:
            lst.append(value)

    def has(*names):
        return any(news.get(name) for name in names)

    def elevate(level):
        nonlocal_placeholder = None
        # Prioridade: BAIXO < MEDIO < ALTO < CRITICO
        rank = {"BAIXO": 0, "MEDIO": 1, "ALTO": 2, "CRITICO": 3}
        return level if rank[level] > rank[alert_level] else alert_level

    rules = [
        (("crise_alimentar",), "ALTO",
         ["Pressao sobre disponibilidade e preco de alimentos basicos.",
          "Risco de interrupcoes regionais na cadeia de abastecimento.",
          "Dependencia de importacoes ou de poucas rotas pode ampliar impactos."],
         ["Acompanhar precos, estoques e comunicados oficiais de abastecimento.",
          "Possivel aumento de precos se a oferta ou o transporte forem afetados.",
          "Produtos especificos podem faltar localmente sem configurar escassez nacional."],
         ["Manter despensa rotativa de alimentos nao pereciveis para necessidades da casa.",
          "Planejar refeicoes economicas e substituir ingredientes equivalentes.",
          "Evitar compras por panico; repor gradualmente o que for consumido."]),
        (("crise_energia",), "ALTO",
         ["Risco de interrupcao eletrica ou pressao sobre a oferta de energia.",
          "Falhas prolongadas podem afetar comunicacao, refrigeracao e pagamentos.",
          "Dependencia de energia pode interromper servicos locais essenciais."],
         ["Observar avisos da concessionaria e alertas de clima severo.",
          "Apagoes locais podem ocorrer por manutencao, demanda ou eventos climaticos.",
          "A duracao e a abrangencia dependem da causa e da infraestrutura afetada."],
         ["Carregar celulares e baterias externas quando houver aviso confiavel.",
          "Ter lanternas e pilhas funcionais e saber como desligar equipamentos com seguranca.",
          "Proteger alimentos refrigerados e seguir orientacoes locais durante apagao."]),
        (("crise_agua",), "ALTO",
         ["Possivel estresse hidrico, racionamento ou interrupcao localizada do abastecimento.",
          "Falta de agua afeta higiene, preparo de alimentos e servicos de saude.",
          "Secas e falhas de infraestrutura podem agravar a disponibilidade local."],
         ["Acompanhar nivel de reservatorios e avisos da companhia de agua.",
          "Restricoes podem ser localizadas e variar conforme clima e consumo.",
          "A qualidade da agua pode mudar apos inundacoes ou falhas na rede."],
         ["Armazenar agua potavel de forma limpa e em recipientes apropriados.",
          "Identificar pontos oficiais de distribuicao e orientacoes de fervura.",
          "Usar filtros ou desinfeccao adequados ao contaminante indicado pelas autoridades."]),
        (("guerras",), "CRITICO",
         ["Conflitos armados podem causar deslocamentos, danos a infraestrutura e perdas humanas.",
          "Escalada regional pode afetar rotas comerciais, energia e mercados.",
          "Desinformacao durante conflitos pode distorcer a percepcao do risco."],
         ["Acompanhar comunicados oficiais e fontes jornalisticas independentes.",
          "Sancoes, bloqueios e danos logisticos podem alterar precos e prazos de entrega.",
          "Riscos diretos dependem da localizacao; nao inferir ameaca local apenas por manchetes globais."],
         ["Manter documentos, contatos e medicamentos essenciais acessiveis.",
          "Definir contato familiar e ponto de encontro em emergencias.",
          "Se estiver em area afetada, seguir instrucoes das autoridades e orientacoes consulares."]),
        (("terrorismo",), "ALTO",
         ["Noticia de atentado ou ameaca pode elevar a seguranca em locais especificos.",
          "Transportes e eventos podem sofrer interrupcoes preventivas.",
          "Informacoes nao confirmadas podem provocar alarmes falsos."],
         ["Verificar comunicados da policia e dos organizadores do local.",
          "Restricoes de acesso podem mudar conforme a avaliacao das autoridades."],
         ["Evitar a area diretamente afetada e seguir instrucoes de emergencia.",
          "Combinar ponto de encontro e contato alternativo com familiares."]),
        (("colapso_economico",), "ALTO",
         ["Instabilidade financeira pode afetar credito, emprego e custo de vida.",
          "Inflacao persistente reduz o poder de compra das familias.",
          "Problemas em instituicoes especificas nao significam necessariamente colapso sistemico."],
         ["Acompanhar comunicados do banco central e dos reguladores financeiros.",
          "Variacoes de cambio e juros podem elevar custos de importados e dividas.",
          "Rumores sobre bancos devem ser verificados em fontes oficiais."],
         ["Manter orcamento, reserva de emergencia compativel com a realidade e contas essenciais em dia.",
          "Guardar copias seguras de documentos financeiros e contatos do banco.",
          "Evitar concentrar decisoes financeiras em rumores ou promessas de retorno garantido."]),
        (("greve", "greve_caminhoneiros"), "ALTO",
         ["Greves podem interromper transporte, servicos publicos ou cadeias de entrega.",
          "Bloqueios rodoviarios podem atrasar combustiveis, alimentos e medicamentos.",
          "Impactos dependem da adesao, duracao e abrangencia geografica."],
         ["Acompanhar comunicados de transporte e autoridades locais.",
          "Filas e faltas pontuais nao confirmam desabastecimento prolongado."],
         ["Planejar deslocamentos alternativos e evitar areas de bloqueio.",
          "Manter em casa os itens de uso regular sem compras excessivas.",
          "Consultar horarios e funcionamento de servicos antes de sair."]),
        (("ciberataque",), "ALTO",
         ["Ataques digitais podem interromper servicos, pagamentos ou sistemas publicos.",
          "Vazamentos de dados podem facilitar fraudes e roubo de identidade.",
          "Sistemas essenciais podem ter indisponibilidade temporaria durante resposta a incidentes."],
         ["Verificar avisos oficiais da instituicao afetada.",
          "Mensagens urgentes com links e pedidos de senha podem ser tentativas de phishing."],
         ["Manter backups offline de arquivos importantes.",
          "Ativar autenticacao multifator e atualizar sistemas suportados.",
          "Guardar contatos de emergencia e meios de pagamento alternativos seguros."]),
        (("nuclear",), "CRITICO",
         ["Acidente radiologico ou nuclear exige informacao precisa sobre local e contaminacao.",
          "A direcao do vento e as instrucoes oficiais importam mais que especulacoes online.",
          "Exposicao e medidas necessarias dependem do evento e da avaliacao tecnica."],
         ["Monitorar alertas da defesa civil e das autoridades de protecao radiologica.",
          "Nao tomar iodeto de potassio sem orientacao oficial; ele nao protege contra toda radiacao."],
         ["Se houver alerta local, entrar em edificio, permanecer abrigado e acompanhar instrucoes oficiais.",
          "Preparar medicamentos, documentos, agua e carregadores para uma eventual orientacao de abrigo ou evacuacao."]),
        (("climatico", "desastre_natural"), "ALTO",
         ["Eventos extremos podem causar inundacoes, deslizamentos, calor intenso ou interrupcoes de servicos.",
          "Danos a estradas e redes eletricas podem atrasar o socorro.",
          "O risco varia muito conforme local, previsao e condicoes da infraestrutura."],
         ["Acompanhar previsoes meteorologicas e alertas da defesa civil.",
          "Observar ordens de evacuacao, alertas de enchente e avisos de calor."],
         ["Preparar kit basico, documentos protegidos e contatos de emergencia.",
          "Conhecer rotas de evacuacao e locais seguros fora de areas inundaveis.",
          "Nunca atravessar agua de inundacao a pe ou de veiculo."]),
        (("pandemia", "virus"), "ALTO",
         ["Noticias de surtos podem indicar risco sanitario localizado ou em investigacao.",
          "A transmissao e a gravidade dependem do agente, da regiao e das evidencias disponiveis.",
          "Desinformacao pode levar a medidas inadequadas ou atrasar atendimento."],
         ["Acompanhar orientacoes das autoridades de saude.",
          "Verificar se os casos sao confirmados e qual area foi afetada.",
          "Mudancas de recomendacao devem ser baseadas em dados atualizados."],
         ["Manter vacinacao e medicamentos de uso regular em dia conforme orientacao profissional.",
          "Higienizar as maos e melhorar ventilacao em ambientes fechados quando indicado.",
          "Procurar atendimento se houver sinais de gravidade e seguir orientacao medica."]),
        (("refugiados",), "MEDIO",
         ["Deslocamentos populacionais podem aumentar a demanda por abrigo e servicos humanitarios.",
          "Comunidades acolhedoras podem precisar de apoio adicional em saude, moradia e educacao."],
         ["Acompanhar dados de agencias humanitarias e autoridades locais.",
          "Evitar associar migracao automaticamente a aumento de criminalidade."],
         ["Consultar canais oficiais para formas seguras de apoiar iniciativas humanitarias.",
          "Compartilhar apenas informacoes verificadas sobre servicos e acolhimento."]),
        (("petroleo",), "MEDIO",
         ["Variacoes no preco do petroleo podem repercutir em transporte e custos de producao.",
          "Choques de oferta podem pressionar combustiveis e fretes."],
         ["Acompanhar cotacoes com data, unidade e fonte identificadas.",
          "O efeito no preco local depende de impostos, cambio e politicas de precos."],
         ["Planejar deslocamentos e reduzir desperdicio de energia quando viavel."])
    ]

    for categories, level, threat_items, prediction_items, prep_items in rules:
        if has(*categories):
            alert_level = elevate(level)
            for item in threat_items:
                add(threats, item)
            for item in prediction_items:
                add(predictions, item)
            for item in prep_items:
                add(preparations, item)

    # Indicadores de alerta e correlacoes sao condicionais as categorias coletadas.
    if has("guerras") and has("petroleo"):
        add(correlations, "Conflito + petroleo: possivel pressao sobre energia, frete e alimentos; verificar escala e duracao.")
    if has("climatico", "desastre_natural") and has("crise_agua"):
        add(correlations, "Evento climatico + agua: possivel impacto em reservatorios, agricultura e abastecimento.")
    if has("ciberataque") and has("colapso_economico"):
        add(correlations, "Ciberataque + instabilidade financeira: avaliar comunicados de bancos e reguladores.")
    if has("greve", "greve_caminhoneiros") and has("crise_alimentar", "petroleo"):
        add(correlations, "Greve + alimentos/combustiveis: atrasos logisticos podem pressionar a oferta local.")
    if has("pandemia", "virus") and has("refugiados"):
        add(correlations, "Surto sanitario + deslocamento populacional: verificar capacidade de atendimento e comunicacao publica.")

    for item in [
        "Alertas oficiais locais, ordens de evacuacao ou abrigo.",
        "Interrupcoes confirmadas de agua, energia, transporte ou comunicacao.",
        "Variacoes persistentes de preco e disponibilidade em fontes distintas.",
        "Dados confirmados por mais de uma fonte confiavel, em vez de postagens virais."
    ]:
        add(early_signals, item)

    for item in [
        "Conferir alertas oficiais locais e a previsao do tempo.",
        "Verificar agua, alimentos, medicamentos e contatos essenciais.",
        "Carregar telefone e bateria externa se houver risco de interrupcao eletrica.",
        "Separar documentos e contatos de emergencia.",
        "Confirmar informacoes antes de repassar alertas."
    ]:
        add(actions_24h, item)

    for item in [
        "Repor gradualmente itens essenciais que realmente sao usados em casa.",
        "Testar lanternas, pilhas, carregadores e radio, se disponivel.",
        "Revisar contatos, ponto de encontro e necessidades de familiares.",
        "Identificar fontes oficiais de agua, saude, transporte e emergencia."
    ]:
        add(actions_7d, item)

    for item in [
        "Montar um plano familiar de comunicacao e contingencia.",
        "Revisar o orcamento e identificar despesas essenciais.",
        "Fazer backup de documentos digitais e proteger contas importantes.",
        "Atualizar o kit de emergencia conforme riscos reais da regiao."
    ]:
        add(actions_30d, item)

    for item in [
        "Defesa civil e servicos de emergencia locais.",
        "Agencias meteorologicas e hidrologicas oficiais.",
        "Autoridades de saude e organizacoes humanitarias reconhecidas.",
        "Reguladores financeiros, concessionarias e comunicados dos servicos afetados."
    ]:
        add(alternative_sources, item)

    for item in [
        "Criancas, idosos e pessoas com mobilidade reduzida.",
        "Pessoas que dependem de medicamentos ou equipamentos eletricos.",
        "Familias com inseguranca alimentar ou habitacional.",
        "Moradores de areas sujeitas a inundacao, calor extremo ou deslizamento."
    ]:
        add(vulnerable_groups, item)

    if not threats:
        threats = ["Nenhuma ameaca especifica pode ser inferida das noticias fornecidas."]
        predictions = ["Dados insuficientes para prever uma crise; ausencia de noticias coletadas nao prova ausencia de risco."]
        preparations = ["Manter preparacao basica proporcional aos riscos locais e acompanhar fontes oficiais."]
        resources = ["Agua potavel, alimentos habituais, medicamentos prescritos, lanterna e contatos de emergencia."]
        social_impacts = ["Nao ha base suficiente para estimar impacto social especifico."]
        alert_level = "BAIXO"
    else:
        # Recursos gerais e praticos; nao sao recomendacao de compra por panico.
        for item in [
            "Agua potavel e recipientes limpos.",
            "Alimentos habituais nao pereciveis e abridor manual, se necessario.",
            "Medicamentos prescritos e contatos de atendimento.",
            "Lanterna, pilhas ou bateria externa.",
            "Documentos importantes e contatos de emergencia."
        ]:
            add(resources, item)
        for item in [
            "Possivel aumento de preocupacao publica e procura por informacoes.",
            "Interrupcoes de servicos podem afetar mais pessoas com menos recursos.",
            "Impactos reais dependem da localizacao, duracao e resposta das autoridades."
        ]:
            add(social_impacts, item)

    economic_impacts = [
        "Precos, emprego e abastecimento podem ser afetados conforme a natureza e duracao do evento.",
        "Impactos locais devem ser confirmados por dados e comunicados especificos.",
        "Evitar decisoes financeiras precipitadas baseadas apenas em manchetes."
    ]

    # Nao truncar listas: o fallback expandido preserva todos os itens unicos.
    return {
        "nivel_alerta": alert_level,
        "resumo_executivo": (
            "Analise manual expandida: regras heuristicas aplicadas as categorias com noticias. "
            "Os itens descrevem riscos possiveis, nao confirmam que uma crise ocorrera. "
            "Verifique local, data e fontes oficiais antes de tomar decisoes."
        ),
        "principais_ameacas": threats,
        "previsoes_futuras": predictions,
        "sinais_alerta_precoce": early_signals,
        "preparacoes_necessarias": preparations,
        "recursos_essenciais": resources,
        "impacto_social": social_impacts,
        "impacto_economico": economic_impacts,
        "grupos_vulneraveis": vulnerable_groups,
        "acoes_24h": actions_24h,
        "acoes_7d": actions_7d,
        "acoes_30d": actions_30d,
        "fontes_alternativas": alternative_sources,
        "correlacoes": correlations,
        "citacoes_fontes": []
    }

def generate_report(analysis, quotes, scope="both"):
    """Gera checklist global, nacional ou combinado."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if scope == "global":
        report_title = "CHECKLIST DE AMEACAS GLOBAIS"
    elif scope == "national":
        report_title = "CHECKLIST DE AMEACAS NACIONAIS - BRASIL"
    else:
        report_title = "CHECKLIST DE AMEACAS PARA SOBREVIVENCIA"
    lines = [report_title, "Atualizado: {}".format(timestamp), ""]

    # Os topicos globais referem-se a riscos transfronteiricos ou sistemicos.
    global_categories = [
        ("CONFLITOS E GEOPOLITICA", ("guerras", "terrorismo", "conflitos_civis"), [
            "Escalada de conflitos armados entre paises",
            "Ataques a infraestrutura estrategica ou rotas internacionais",
            "Tensoes geopoliticas, sancoes e restricoes comerciais"
        ]),
        ("ENERGIA E COMBUSTIVEIS", ("petroleo", "gas_combustivel", "crise_energia"), [
            "Choques globais na oferta ou no preco de petroleo, gas e combustiveis",
            "Interrupcao de rotas internacionais de energia",
            "Crise energetica com impacto em producao e transporte"
        ]),
        ("ALIMENTOS E AGRICULTURA", ("crise_alimentar", "agricultura_colheitas", "fertilizantes_insumos"), [
            "Quebras de safra simultaneas em regioes produtoras",
            "Restricoes a exportacao de alimentos, graos ou fertilizantes",
            "Interrupcao internacional de cadeias alimentares",
            "Escassez global de insumos agricolas"
        ]),
        ("AGUA E CLIMA", ("crise_agua", "qualidade_agua", "climatico", "meteorologia"), [
            "Secas prolongadas afetando varias regioes produtoras",
            "Eventos climaticos extremos com impacto transfronteirico",
            "Pressao sobre recursos hidricos em bacias compartilhadas"
        ]),
        ("COMERCIO E LOGISTICA INTERNACIONAL", ("cadeia_abastecimento", "portos_comercio", "fronteiras_sancoes", "minerais_materiais"), [
            "Interrupcao de rotas maritimas, portos ou corredores comerciais",
            "Restricoes de exportacao e escassez de materiais estrategicos",
            "Ruptura de cadeias internacionais de componentes e medicamentos"
        ]),
        ("ECONOMIA E FINANCAS GLOBAIS", ("colapso_economico", "mercados_financas"), [
            "Instabilidade financeira com repercussao em varios paises",
            "Inflacao global em energia, alimentos ou materias-primas",
            "Crise de credito ou perturbacao dos mercados internacionais"
        ]),
        ("RISCO PANDEMICO", ("pandemia", "virus", "nipah", "hantavirus", "ebola_marburg", "gripe_aviaria_h5n1", "influenza_h1n1", "covid_sars", "mpox_lassa_zika", "outros_virus_emergentes"), [
            "Sinais de transmissao sustentada entre humanos ou em varios paises",
            "Novos surtos, variantes ou aumento incomum de casos",
            "Nipah, hantavirus, Ebola/Marburg, H5N1, H1N1 e COVID-19",
            "Mpox, MERS/SARS, Lassa, Zika, Oropouche e outros virus emergentes",
            "Alertas epidemiologicos, mudancas de transmissibilidade ou gravidade"
        ]),
        ("PANDEMIAS E SAUDE INTERNACIONAL", ("pandemia", "virus", "nipah", "hantavirus", "ebola_marburg", "gripe_aviaria_h5n1", "influenza_h1n1", "covid_sars", "mpox_lassa_zika", "outros_virus_emergentes", "doencas_animais", "saude_publica"), [
            "Surto com propagacao entre paises",
            "Doencas em animais afetando cadeias alimentares internacionais",
            "Escassez internacional de medicamentos ou insumos medicos"
        ]),
        ("RISCOS NUCLEARES, QUIMICOS E AMBIENTAIS", ("nuclear", "quimico_industrial", "poluicao_ar", "incendios_florestais", "vulcoes"), [
            "Incidente nuclear ou radiologico com potencial transfronteirico",
            "Poluicao ou contaminacao que ultrapasse fronteiras",
            "Grandes incendios ou erupcoes com efeitos regionais"
        ]),
        ("CIBERSEGURANCA GLOBAL", ("ciberataque", "telecomunicacoes", "cortes_internet"), [
            "Ciberataques simultaneos a servicos ou empresas de varios paises",
            "Falhas em sistemas internacionais de pagamentos ou comunicacoes",
            "Ataques a cadeias globais de fornecimento digital"
        ]),
        ("DESLOCAMENTO E CRISE HUMANITARIA", ("refugiados", "moradia_abrigo"), [
            "Deslocamentos em massa causados por guerra ou desastre",
            "Pressao internacional sobre abrigos e ajuda humanitaria"
        ])
    ]

    # Riscos nacionais: impactos dentro do pais monitorado. A coleta RSS usa
    # Google News em portugues/Brasil; por isso, "nacional" deve ser entendido
    # como Brasil e a classificacao geografica da manchete precisa ser conferida.
    national_categories = [
        ("ABASTECIMENTO DE ALIMENTOS", ("crise_alimentar", "cadeia_abastecimento"), [
            "Falta ou alta de alimentos em mercados e distribuidores",
            "Interrupcao regional de entregas e abastecimento",
            "Dependencia de rotas ou centros de distribuicao especificos"
        ]),
        ("AGUA E SANEAMENTO", ("crise_agua", "qualidade_agua", "residuos_saneamento"), [
            "Racionamento ou interrupcao de agua em municipios ou regioes",
            "Contaminacao da agua ou alerta de qualidade",
            "Falhas de esgoto, saneamento ou coleta de residuos"
        ]),
        ("ENERGIA E COMBUSTIVEIS", ("crise_energia", "petroleo", "gas_combustivel"), [
            "Apagoes, falhas na rede ou risco de racionamento",
            "Falta ou alta de gasolina, diesel, gas ou outros combustiveis",
            "Interrupcao local de servicos essenciais dependentes de energia"
        ]),
        ("TRANSPORTE E GREVES", ("greve", "greve_caminhoneiros", "transporte_publico", "portos_comercio"), [
            "Greves, bloqueios rodoviarios ou paralisacao de transportes",
            "Atraso de alimentos, combustiveis e medicamentos",
            "Interrupcao de portos, aeroportos, ferrovias ou transporte publico"
        ]),
        ("DESASTRES E CLIMA", ("desastre_natural", "climatico", "meteorologia", "incendios_florestais", "vulcoes"), [
            "Enchentes, deslizamentos, secas, tempestades ou calor extremo",
            "Incendios com evacuacoes ou piora da qualidade do ar",
            "Danos a estradas, redes eletricas e servicos de emergencia"
        ]),
        ("RISCO PANDEMICO", ("pandemia", "virus", "nipah", "hantavirus", "ebola_marburg", "gripe_aviaria_h5n1", "influenza_h1n1", "covid_sars", "mpox_lassa_zika", "outros_virus_emergentes"), [
            "Casos suspeitos ou confirmados e transmissao local",
            "Nipah, hantavirus, Ebola/Marburg, H5N1, H1N1 e COVID-19",
            "Mpox, MERS/SARS, Lassa, Zika, Oropouche e outros virus emergentes",
            "Alertas epidemiologicos, novas variantes ou aumento incomum de casos"
        ]),
        ("SAUDE PUBLICA", ("pandemia", "virus", "nipah", "hantavirus", "ebola_marburg", "gripe_aviaria_h5n1", "influenza_h1n1", "covid_sars", "mpox_lassa_zika", "outros_virus_emergentes", "saude_publica", "doencas_animais"), [
            "Surtos locais ou regionais sob investigacao",
            "Falta de medicamentos ou sobrecarga de hospitais",
            "Alertas sanitarios sobre agua, alimentos ou animais"
        ]),
        ("SEGURANCA E CONFLITOS INTERNOS", ("terrorismo", "conflitos_civis", "crime_seguranca"), [
            "Ameacas localizadas, atentados ou alertas de seguranca",
            "Disturbios, confrontos ou declaracao de emergencia",
            "Fechamento de areas, vias ou locais publicos"
        ]),
        ("ECONOMIA NACIONAL", ("colapso_economico", "mercados_financas"), [
            "Inflacao, desemprego ou perda de poder de compra",
            "Instabilidade bancaria ou falhas em pagamentos",
            "Alta de aluguel, alimentos, transporte e servicos essenciais"
        ]),
        ("CIBERATAQUES E COMUNICACOES", ("ciberataque", "telecomunicacoes", "cortes_internet"), [
            "Ataques a sistemas publicos, bancos ou empresas essenciais",
            "Interrupcao de internet, telefonia ou pagamentos",
            "Fraudes digitais e vazamentos de dados"
        ]),
        ("INFRAESTRUTURA E EMERGENCIAS", ("infraestrutura", "resgate_emergencia"), [
            "Falhas em pontes, barragens, redes de agua ou energia",
            "Sobrecarga de bombeiros, hospitais ou servicos de resgate",
            "Interrupcao de saneamento, coleta de lixo ou servicos municipais"
        ]),
        ("ABRIGOS E DESLOCAMENTO", ("refugiados", "moradia_abrigo"), [
            "Desabrigados por desastres ou conflitos",
            "Falta de vagas em abrigos ou necessidade de apoio humanitario",
            "Interrupcao de moradia, escolas ou servicos comunitarios"
        ]),
        ("ACIDENTES INDUSTRIAIS E RADIOLÓGICOS", ("nuclear", "quimico_industrial", "poluicao_ar"), [
            "Vazamento quimico, contaminacao industrial ou acidente radiologico",
            "Ordens locais de abrigo, evacuacao ou restricao de acesso"
        ])
    ]

    news = analysis.get("_news_categories", {})

    def add_section(section_title, categories):
        nonlocal emitted
        lines.append(section_title)
        section_emitted = False
        for title, keys, items in categories:
            # Categorias aparecem quando houve noticias em um dos topicos associados.
            if news and not any(news.get(k) for k in keys):
                continue
            lines.append(title)
            for item in items:
                lines.append("[ ] " + item)
            lines.append("")
            section_emitted = True
            emitted = True
        if not section_emitted:
            lines.append("[ ] Nenhuma noticia coletada nas categorias desta secao")
            lines.append("")

    emitted = False
    if scope in ("both", "global"):
        add_section("AMEACAS GLOBAIS", global_categories)
    if scope in ("both", "national"):
        add_section("AMEACAS NACIONAIS (BRASIL)", national_categories)

    if not emitted:
        lines.append("AMEACAS IDENTIFICADAS")
        threats = analysis.get("principais_ameacas", [])
        if threats:
            for item in threats:
                lines.append("[ ] {}".format(item))
        else:
            lines.append("[ ] Nenhuma ameaca especifica identificada nas noticias coletadas")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

def main():
    print("SISTEMA DE MONITORAMENTO DE AMEACAS GLOBAIS")
    print("Data: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    print("Categorias monitoradas: {}".format(len(TOPICS)))
    print("IA: LLM7 via API compativel com OpenAI ({})".format(LLM7_MODEL))
    print("Timeout IA: {}s".format(LLM7_TIMEOUT))
    print("")

    try:
        print("[1] Coletando noticias...")
        news = get_all_news()

        total_news = sum(len(items) for items in news.values())
        print("Total de noticias coletadas: {}".format(total_news))

        print("[2] Coletando cotacoes...")
        quotes = get_quotes()
        print("Cotacoes carregadas")

        print("[3] Analisando com LLM7...")
        analysis = analyze_with_llm7(news, quotes)

        if analysis is None:
            print("LLM7 indisponivel; usando analise manual")
            analysis = analyze_manual(news, quotes)
        else:
            print("Analise via LLM7 concluida")

        print("[4] Gerando relatorio...")
        analysis["_news_categories"] = news
        global_report = generate_report(analysis, quotes, scope="global")
        national_report = generate_report(analysis, quotes, scope="national")

        with open(GLOBAL_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(global_report)
        with open(NATIONAL_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(national_report)

        print("[5] Relatorio global salvo: {}".format(GLOBAL_OUTPUT_FILE))
        print("[6] Relatorio nacional salvo: {}".format(NATIONAL_OUTPUT_FILE))
        print("Nivel de Alerta: {}".format(analysis.get('nivel_alerta', 'MEDIO')))
        print("")
        print("SUCESSO - Execucao finalizada")

        return 0

    except Exception as e:
        print("ERRO: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())