from tkinter import *
from tkinter import messagebox
from urllib.request import Request, urlopen
import pandas as pd
import re
import bs4
import time
import logging
import os
import xlsxwriter
import Fundamento as fd

Tickers = [] #lista de tickers das ações que serão pesquisadas
Objetos_fundamentos = [] #lista de objetos da classe 'Fundamento'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#-------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------DEFINIÇÃO DAS FUNÇÕES------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------
def gerar_indicadores(): #função que gera a planilha no excel com os indicadores selecionados.  

    if len(Objetos_fundamentos) > 0:        
        logging.debug('Criando Dataframe e salvando em planilha Indicadores_OUTPUT.xlsx')
        #Criando dicionario que servira de base para criação do Dataframe
        dados = {'Ticker': [i.retorna_ticker() for i in Objetos_fundamentos],
            'Periodo': [i.retorna_periodo() for i in Objetos_fundamentos]}

        #Adicionando as colunas que foram selecionadas para vizualização nos checkboxs
        if lc.get() == 1:
            dados['Liquidez Corrente'] = [i.liquidez_corrente() for i in Objetos_fundamentos]
        if af.get() == 1:
            dados['Alavancagem'] = [i.alavancagem_financeira() for i in Objetos_fundamentos]
        if ml.get() == 1:
            dados['Margem Líquida'] = [i.margem_liquida() for i in Objetos_fundamentos]
        if me.get() == 1:
            dados['Margem EBIT'] = [i.margem_EBIT() for i in Objetos_fundamentos]
        if roe.get() == 1:
            dados['ROE'] = [i.ROE() for i in Objetos_fundamentos]
        if roa.get() == 1:
            dados['ROA'] = [i.ROA() for i in Objetos_fundamentos]
        if pl.get() == 1:
            dados['P/L'] = [i.P_L() for i in Objetos_fundamentos]
        if pvp.get() == 1:
            dados['P/VP'] = [i.P_VP() for i in Objetos_fundamentos]
        if pa.get() == 1:
            dados['P/Ativo'] = [i.P_A() for i in Objetos_fundamentos]
        if dy.get() == 1:
            dados['Dividend Yield'] = [i.dividend_yield() for i in Objetos_fundamentos]
    
        #criando o Dataframe com todos os dados
        main_df = pd.DataFrame(dados)

        #Configurações inciais para criar o arquivo no Excel
        writer = pd.ExcelWriter('Indicadores_OUTPUT.xlsx', engine='xlsxwriter')
        main_df.to_excel(writer, sheet_name='indicadores', startrow=1, header=False, index=False)

        #criando objeto 'worksheet'
        worksheet = writer.sheets['indicadores']

        #ajustando largura das colunas de acordo com o nome da coluna
        for i in range(len(main_df.columns)):
            larg = len(main_df.columns[i])
            if larg<5:          
                worksheet.set_column(i, i, (larg + 5))
            elif larg<10:
                worksheet.set_column(i, i, (larg + 4))
            else:
                worksheet.set_column(i, i, (larg + 3))

        #criando tabela Excel
        column_settings = [{'header': column} for column in main_df.columns]
        (max_row, max_col) = main_df.shape
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})

        #salvando o arquivo na pasta de fato
        writer.save()
        time.sleep(2)

        #Abrindo planilha Excel com os indicadores
        logging.debug('Abrindo planilha Indicadores_OUTPUT.xlsx')
        os.system('start excel.exe Indicadores_OUTPUT.xlsx')

    else:
        messagebox.showinfo('Aviso','Favor clicar em "Baixar Dados" antes.')

#-------------------------------------------------------------------------------------------------------------------------
def baixar_dados(): #funçao que obtem os dados necessarios para gerar a planilha de indicadores
    
    if len(Tickers) > 0:
        #instanciando objetos da classe 'Fundamento'
        for tick in Tickers:
            Objetos_fundamentos.append(fd.Fundamento(tick))

        #atualizando as informaçoes para cada ação      
        for item in Objetos_fundamentos:

            item.link_principal()
            
            #vai buscar dados na web apenas se a ação for válida, e tiver link disponivel na investing.com
            if item.tem_link():
                item.atualizar_preco_vm()
                item.atualizar_balanco()
                item.atualizar_DRE()
                item.atualizar_dividendos()

        messagebox.showinfo('Aviso','Todos os dados foram baixados da Web!')
        
    else:
        messagebox.showinfo('Aviso','Favor adicionar pelo menos uma ação a lista.')

#-------------------------------------------------------------------------------------------------------------------------          
def adicionar(): #função que adiciona novo ticker a lista
    novo = str(novoTicker.get())

    if re.compile(r'^[A-Za-z3]{4}\d{1,2}').search(novo) and len(novo)<=6:
        Tickers.append(novo.upper())
        listaTickers.insert(END, novo.upper())
    else:
        messagebox.showinfo('Aviso','Valor não é um Ticker!')
        
    novoTicker.delete(0, END)

#-------------------------------------------------------------------------------------------------------------------------
def limpar(): #função que limpa a lista de tickers
    Tickers.clear()
    Objetos_fundamentos.clear()
    listaTickers.delete(0,END)

#-------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------INTERFACE GRAFICA----------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------
root = Tk()
root.title('Indicadores v1.0')
root.geometry('290x420')

titulo = Label(root, text='   INDICADORES  \n  FUNDAMENTALISTAS', fg="blue", font=('Helvetica', 18))
titulo.grid(row=0, column=0, columnspan=2) 

Insira = Label(root, text='Insira o ticker:', fg="black", font=('Helvetica', 10))
Insira.grid(row=1, column=0) 

novoTicker = Entry(root, text='Novo', width=10)
novoTicker.grid(row=2, column=0)

#definindo botões
adicionarTicker = Button(root, text='Adicionar', command=adicionar, width='10')
adicionarTicker.grid(row=4, column=0)

limparTudo = Button(root, text='Limpar', command=limpar, width='10')
limparTudo.grid(row=6, column=0)

obterdados = Button(root, text='Baixar Dados', command=baixar_dados, width='10')
obterdados.grid(row=8, column=0)

gerar = Button(root, text='Gerar\nIndicadores', command=gerar_indicadores, width='10')
gerar.grid(row=10, column=0)

#definindo lista e scrollbar
yScroll = Scrollbar(root, orient=VERTICAL)
yScroll.grid(row=1, column=2, rowspan=10, sticky=N+S)

listaTickers = Listbox(root, yscrollcommand=yScroll.set)
listaTickers.grid(row=1, column=1, rowspan=10, sticky=N+S+E+W)
yScroll['command'] = listaTickers.yview

#abaixo são definidos todos os checkbox para escolher os indicadores
vazio = Label(root, text='', fg="black", font=('Helvetica', 10))#linha vazia
vazio.grid(row=12, column=0, columnspan=2) 

definir = LabelFrame(root, text='Selecione os indicadores:', fg="black", font=('Helvetica', 10))
definir.grid(column=0, row=13, columnspan=4, rowspan=10, padx=8, pady=4, sticky='N')

lc = IntVar()
check1 = Checkbutton(definir, text="Liquidez corrente  ", variable=lc)
check1.grid(row=14, column=0, sticky='W')

af = IntVar()
check2 = Checkbutton(definir, text="Alavancagem finan. ", variable=af)
check2.grid(row=14, column=1, sticky='W')

ml = IntVar()
check3 = Checkbutton(definir, text="Margem líquida", variable=ml)
check3.grid(row=15, column=0, sticky='W')

me = IntVar()
check4 = Checkbutton(definir, text="Margem EBIT", variable=me)
check4.grid(row=15, column=1, sticky='W')

roe = IntVar()
check5 = Checkbutton(definir, text="ROE", variable=roe)
check5.grid(row=16, column=0, sticky='W')

roa = IntVar()
check6 = Checkbutton(definir, text="ROA", variable=roa)
check6.grid(row=16, column=1, sticky='W')

pl = IntVar()
check7 = Checkbutton(definir, text="P/L", variable=pl)
check7.grid(row=17, column=0, sticky='W')

pvp = IntVar()
check8 = Checkbutton(definir, text="P/VP", variable=pvp)
check8.grid(row=17, column=1, sticky='W')

pa = IntVar()
check9 = Checkbutton(definir, text="P/Ativo", variable=pa)
check9.grid(row=18, column=0, sticky='W')

dy = IntVar() 
check10 = Checkbutton(definir, text="Dividend Yield", variable=dy)
check10.grid(row=18, column=1, sticky='W')

root.mainloop()
#-------------------------------------------------------------------------------------------------------------------------