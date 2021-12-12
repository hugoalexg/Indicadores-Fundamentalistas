from tkinter import messagebox
from urllib.request import Request, urlopen
import requests
import pandas as pd
import bs4
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Fundamento:
    def __init__(self, codigo, link):
        self.ticker = codigo
        self.link = link #link principal Investing.com
        self.periodo = ''
        #balanço (mais recente)
        self.ativoCirculante = 0.0 #x1000
        self.ativoTotal = 0.0 #x1000
        self.passivoCirculante = 0.0 #x1000
        self.passivoTotal = 0.0 #x1000
        self.patrimonioLiquido = 0.0 #x1000
        #DRE (ultimos 12 meses)
        self.ROL = 0.0 #x1000
        self.EBIT = 0.0 #x1000
        self.lucroLiquido = 0.0 #x1000
        #outros
        self.precoAtual = 0.0
        self.valorMercado = 0.0 #x1000
        self.dividendos12meses = 0.0
    
    def atualizar_preco_vm(self): 
        #Pegar preço atual e valor de mercado(Statusinvest)
        url = 'https://statusinvest.com.br/acoes/' + self.ticker
        logging.debug('Atualizando preço e valor de mercado de ' + self.ticker)
        try:
            res = requests.get(url)
            res.raise_for_status()
            soup = bs4.BeautifulSoup(res.text, 'html.parser')

            elemento = (soup.find('div', {'title': 'Valor atual do ativo'})).find_all('strong')[0].get_text()
            self.precoAtual = float(elemento.split(',')[0]) + float(elemento.split(',')[1])*0.01

            elemento = soup.find("div", {'title': 'O valor da ação multiplicado pelo número de ações existentes'}).get_text()
            self.valorMercado = float(elemento.split('\n')[8].replace('.',''))/1000   

        except Exception as exc:
            logging.debug('ERRO: ' + str(exc))
            messagebox.showinfo('Aviso','ERRO: ' + str(exc))

    def atualizar_balanco(self):
        #Pegar dados de balanço patrimonial e periodo do ultimo balanço(Investing.com)
        url = self.link + '-balance-sheet'
        logging.debug('Atualizando balanço patrimonial de ' + self.ticker)
        try:
            req = Request(url , headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            soup = bs4.BeautifulSoup(webpage, 'html.parser')

            lista = soup.find_all('tr')

            #buscando dados do balanço patrimonial
            for i in range(len(lista)):
                if lista[i].find_all('td'): #se lista não esta vazia

                    nome_linha = lista[i].find_all('td')[0].get_text()
                    elemento1 = lista[i].find_all('td')[1].get_text()

                    func = lambda val: float(val.split(',')[0])*1000 if val != '-' else 0.0

                    if nome_linha == 'Total do Ativo Circulante':
                        self.ativoCirculante = func(elemento1)
                    elif nome_linha == 'Total do Ativo':
                        self.ativoTotal = func(elemento1)
                    elif nome_linha == 'Total do Passivo Circulante':
                        self.passivoCirculante = func(elemento1)
                    elif nome_linha == 'Total do Passivo':
                        self.passivoTotal = func(elemento1)
                    elif nome_linha == 'Total do Patrimônio Líquido':
                        self.patrimonioLiquido = func(elemento1)

            #buscando periodo do ultimo balanço
            ano = soup.find('table', {'class': 'genTbl reportTbl'}).find_all('span')[1].get_text()
            data = soup.find('table', {'class': 'genTbl reportTbl'}).find_all('div')[0].get_text()

            if '03' in data.split('/')[1]:
                tri = '1T'
            elif '06' in data.split('/')[1]:
                tri = '2T'
            elif '09' in data.split('/')[1]:
                tri = '3T'
            elif '12' in data.split('/')[1]:
                tri = '4T'
            self.periodo = tri + '-' + ano

        except Exception as exc:
            logging.debug('ERRO: ' + str(exc))
            messagebox.showinfo('Aviso','ERRO: ' + str(exc))

    def atualizar_DRE(self):
        #Pegar dados de DRE(Investing.com)
        url = self.link + '-income-statement'
        logging.debug('Atualizando dados de DRE de ' + self.ticker)
        try:
            req = Request(url , headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            soup = bs4.BeautifulSoup(webpage, 'html.parser')

            lista = soup.find_all('tr')

            for i in range(len(lista)):
                #vai pegar os valores dos ultimos 4 trimestres e somar.
                #'Receita Líquida de Juros' serve para os bancos, pois não aparece 'Receita Total' na DRE
                if ('Receita Total' in lista[i].get_text()) or ('Receita Líquida de Juros' in lista[i].get_text()):
                    lista_rol = [float(var.get_text().split(',')[0]) for var in lista[i].find_all('td')[1:5]]
                    self.ROL = sum(lista_rol)*1000

                elif 'Receitas Operacionais' in lista[i].get_text():
                    lista_ebit = [float(var.get_text().split(',')[0]) for var in lista[i].find_all('td')[1:5]]
                    self.EBIT = sum(lista_ebit)*1000

                elif 'Lucro Líquido Antes de Ítens Extraordinários' in lista[i].get_text():
                    lista_ll = [float(var.get_text().split(',')[0]) for var in lista[i].find_all('td')[1:5]]
                    self.lucroLiquido = sum(lista_ll)*1000

        except Exception as exc:
            logging.debug('ERRO: ' + str(exc))
            messagebox.showinfo('Aviso','ERRO: ' + str(exc))

    def atualizar_dividendos(self):     
        #Pegar a soma dos dividendos pagos por ação nos ultimos 12 meses (Statusinvest)
        url = 'https://statusinvest.com.br/acoes/' + self.ticker.lower()
        logging.debug('Atualizando dividendos do ultimos 12 meses de ' + self.ticker)
        try:
            res = requests.get(url)
            res.raise_for_status()
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            
            alist = soup.find_all('table')

            for i in range(len(alist)): #buscando tabela de Dividendos/JCP
                if ('Dividendo' in alist[i].get_text()) or ('JCP' in alist[i].get_text()):
                    #convertendo tabela html em um dataframe
                    df = pd.read_html(str(alist[i]))[0] 

                    #tratando os dados do dataframe
                    df['Valor'] = df['Valor'].apply(str)
                    df['Valor'] = df['Valor'].apply(lambda var: var.split()[0] if 'report' in var else var)
                    df['Valor'] = df['Valor'].apply(lambda numb: float(numb.replace(',','.')) if ',' in numb else float(numb)*0.00000001)
                    df['DATA COM'] = pd.to_datetime(df['DATA COM'],format='%d/%m/%Y')

                    #novo dataframe com os dividendos/JCP dos ultimos 12 meses (DATA COM)
                    hoje = pd.Timestamp('today')
                    df_novo = df[(df['DATA COM'] >= (hoje - pd.DateOffset(years=1))) & (df['DATA COM'] <= hoje)]
                    self.dividendos12meses = df_novo['Valor'].sum()
                    break

        except Exception as exc:
            logging.debug('ERRO: ' + str(exc))
            messagebox.showinfo('Aviso','ERRO: ' + str(exc))
    
    '''Liquidez corrente (AC/PC): Indicador que mostra a capacidade da empresa de quitar suas dívidas de 
    curto-prazo. O ideal é que esse indicador esteja acima de 1, pois caso fique abaixo disso, pode indicar 
    que a empresa podera ter dificuldade em honrar seus compromissos de curto-prazo'''
    def liquidez_corrente(self):
        try:
            valor = self.ativoCirculante/self.passivoCirculante
        except:
            valor = 0.0
        return str("{:.2f}".format(valor))

    '''Alavancagem financeira (PT/AT): Indicador que mostra o tamanho da dívida em relação ao patrimônio 
    total da empresa. Quanto mais próximo de zero, mais saudável está a empresa. Valores acima de 1 indicam 
    uma situação grave, onde o endividamento ja é maior que tudo que a empresa possui, o que é comum em 
    empresas em processo de recuperação judicial'''
    def alavancagem_financeira(self):
        try:
            valor = self.passivoTotal/self.ativoTotal
        except:
            valor = 0.0
        return str("{:.2f}".format(valor))

    '''Margem Liquida (LL/ROL): Indicador que mostra a porcentagem do lucro líquido em relação a receita total
    liquida obtida com a venda de produtos/serviços de uma determinada empresa. No caso aqui é pego tanto o 
    somatório dos lucros quanto das receitas dos ultimos 12 meses. lembrando que o lucro líquido é aquilo que 
    sobra apos todas as deduções de despesas administrativas, financeiras, custos de produção, impostos etc.'''
    def margem_liquida(self):
        try:
            valor = self.lucroLiquido/self.ROL
        except:
            valor = 0.0
        return str("{:.2f}".format(valor*100)) + '%'

    '''Margem EBIT (EBIT/ROL): Indicador que mostra a porcentagem do EBIT (Lucro Antes de Impostos e Resultados 
    Financeiros) em relação a receita total líquida da empresa. Esse indicador é importante pois mostra a eficiência 
    operacional da empresa. Diferente do lucro líquido, ele considera apenas o lucro obtido com a atividade fim do 
    négocio e exclui todas as despensas ou receitas financeiras. Lucros obtidos com aplicações financeira por 
    exemplo, ficam de fora desse indicador.'''
    def margem_EBIT(self):
        try:
            valor = self.EBIT/self.ROL
        except:
            valor = 0.0
        return str("{:.2f}".format(valor*100)) + '%'

    '''ROE(LL/PL): Indicador que mostra a porcentagem do lucro líquido dos ultimos 12 meses em relação ao 
    patrimônio líquido atual. E um excelente indicador que mostra a capacidade da empresa de gerar lucro e retorno
    aos seus acionistas com base apenas em seus recursos próprios. Empresas com um ROE mais alto em relação aos seus 
    concorrentes tendem a ter uma gestão mais eficiente de seus recursos.'''
    def ROE(self):
        try:
            valor = self.lucroLiquido/self.patrimonioLiquido
        except:
            valor = 0.0
        return str("{:.2f}".format(valor*100)) + '%'

    '''ROA(LL/AT): Indicador que mostra a porcentagem do lucro líquido dos ultimos 12 meses em relação a soma
    de todos os ativos da empresa. Esse indicador mostra o quão eficiente é uma empresa na utilização de seus ativos
    para geração de retorno aos acionistas. Empresas com estoques muito elevados ou imoveis parados por exemplo, 
    tentem a ter um ROA menos, pois parte do seus ativos não estão sendo utilizados para gerar lucro.'''
    def ROA(self):
        try:
            valor = self.lucroLiquido/self.ativoTotal
        except:
            valor = 0.0
        return str("{:.2f}".format(valor*100)) + '%'

    '''P/L(Valor Mercado/LL): Uma das formas de calcular esse indicador é dividindo o valor de mercado da empresa
    pelo lucro líquido dos últimos 12 meses. É um dos indicadores mais importantes e mostra o quanto o mercado está
    disposto a pagar pelo lucro da empresa. Empresas sólidas com um baixo valor de P/L podem ser ótimas oportunidades
    de investimento, e empresas com P/L muito elevado podem sinalizar bolhas.'''
    def P_L(self):
        try:
            valor = self.valorMercado/self.lucroLiquido
        except:
            valor = 0.0
        return str("{:.2f}".format(valor)) 

    '''P/VP (Valor Mercado/PL): Uma das formas de calcular esse indicador é dividindo o valor de mercado pelo patrimônio 
    líquido da empresa. Esse é um excelente indicador para mostrar se uma ação está 'cara' ou 'barata'. Ele mostra o quanto 
    os investidores estão dispostos a pagar pelo patrímonio líquido da empresa, que na prática é o patrimonio que pertence 
    aos acionistas de fato. O P/VP também pode ser utilizado como indicativo de bolha, caso esteja muito elevado.'''
    def P_VP(self):
        try:
            valor = self.valorMercado/self.patrimonioLiquido
        except:
            valor = 0.0
        return str("{:.2f}".format(valor)) 

    '''P/A (Valor Mercado/AT): Esse indicador pode ser calculado a partir da divisão o Valor de Mercado pela soma dos ativos da 
    empresa. É mais um importante indicador de valuation utilizado pela analise fundamentalista, que mostra o quanto o mercado
    está disposto a pagar pelos ativos da empresa.'''
    def P_A(self):
        try:
            valor = self.valorMercado/self.ativoTotal
        except:
            valor = 0.0
        return str("{:.2f}".format(valor)) 

    '''Dividend Yield (Proventos 12M/Preço Atual): Indicador que mostra a porcentagem do total de proventos (Dividendos + JCP) 
    pagos por ação nos últimos 12 meses em relação ao preço atual dessa mesma ação. Em geral empresas grandes e ja consolidadas 
    no mercado, com lucros elevados, constantes e previsíveis, tendem a ser melhores pagadoras de dividendo. Ja empresas que 
    planejam crescer e aumentar seu market share, acabam preferindo reinvestir os lucros do que distribui-los aos acionistas.'''
    def dividend_yield(self):
        try:
            valor = self.dividendos12meses/self.precoAtual
        except:
            valor = 0.0
        return str("{:.2f}".format(valor*100)) + '%'

    #Retorna o ticker ou ação associado a esse objeto
    def retorna_ticker(self):
        return self.ticker

    #Retorna periodo (trimestre) do ultimo balanço/DRE obtido no site ADVFN
    def retorna_periodo(self):
        return self.periodo