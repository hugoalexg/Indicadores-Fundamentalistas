# Indicadores Fundamentalistas

Programa que gera planilha no Excel com alguns indicadores fundamentalistas de ações 
listadas na B3, com base em uma lista de ações fornecidas pelo usuário. Os indicadores 
também podem ser escolhidos pelo usuário nas 'checkbox'.

Esse programa está dividido em 2 arquivos:

Indicadores_GUI.py - Arquivo onde estão definidos os elementos da interface gráfica (GUI) 
e as funções que serão associadas a cada botão dessa GUI.

Fundamento.py - Arquivo onde está a classe chamada 'Fundamento'. Nessa classe ficam
armazenados os dados de DRE, balanço patrimonial, dividendos, etc. Além disso nessa classe 
tambem são definidos os métodos de 'scraping' desses dados na web, alem dos métodos que 
calculam os indicadores fundamentalistas com base nos dados obtidos. Será instânciado um 
objeto dessa classe para cada uma das ações fornecidas pelo usuário, e todos esses objetos
ficarão armazenados em uma lista.

Lembrando que esse programa foi feito unicamente para fins ditáticos.
