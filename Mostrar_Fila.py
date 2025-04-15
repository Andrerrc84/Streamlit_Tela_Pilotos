import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime, date


def ler_arquivo_xls(caminho):
    try:
        if os.path.exists(caminho):
            # Recebe as informações do arquivo a partir da 5 linha
            df = pd.read_excel(caminho, skiprows=4)
            return df
        else:
            st.error("Arquivo não encontrado. Verifique o caminho.")
            return None
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None

def buscar_primeiras_linhas_vazias(df, coluna):
    try: 
        # Localiza o índice da primeira ocorrência de None na coluna 
        indice_none = df[coluna].isnull().idxmax() 
        # Verifica se há linhas suficientes antes e depois da ocorrência 
        inicio = max(indice_none - 1, 0) 
        # Garante que não acesse índices negativos 
        fim = inicio + 10 
        # Define o intervalo de 6 linhas (uma antes do None e as seguintes) 
        df_separado = df.iloc[inicio:fim]
        return df_separado 
    except Exception as e: 
        st.error(f"Erro ao processar o DataFrame: {e}") 
        return None

def definir_cor(destino, origem):
    #Retorna a cor de fundo com base no destino
    if destino == "SAM":
        return "#FF8C00", None
    
    elif destino == "CEI":
        return "#2E8B57", None
    
    elif destino in ["REC", "PAC", "TF1", "TF2", "TF3"]:
        return "#DCDCDC", None
    
    elif destino == "CTL":
        if origem in ["SAM",'SAS','FUR','TAS','TF1','TF3']:
            #retorna a cor do destino e a plataforma de CLA que o trem passará
            return "#4169E1", 'P4'
        if origem in ['CEI','CEN','CEC','GBA','X26','CES','MET','ONO','REL','TF2','EPQ','CON']:
            #retorna a cor do destino e a plataforma de CLA que o trem passará
            return "#4169E1", 'P2'
        else:
            return "#4169E1", None
    
    elif destino in ["PAS","TF4","TF5",'X30','X31']:
        if origem in ["SAM",'SAS','FUR','TAS','TF1','TF3']:
            #retorna a cor do destino e a plataforma de CLA que o trem passará
            return "#DCDCDC", 'P4'
        if origem in ['CEI','CEN','CEC','GBA','X26','CES','MET','ONO','REL','TF2','EPQ','CON']:
            #retorna a cor do destino e a plataforma de CLA que o trem passará
            return "#DCDCDC", 'P2'
        else:
            return "#DCDCDC", None
    
    elif destino == "RENDER":
        return "#CD5C5C", None
    
    else:
        return "#DCDCDC", None

def intervalo_manha_tarde(dataframe, coluna):
    try:
        # Localiza a linha com o texto "MANHÃ - Horário do Início de Seu Intervalo:"
        linha_manha = dataframe[dataframe[coluna] == "MANHÃ - Horário do Início de Seu Intervalo:"].index
        # Localiza a linha com o texto "TARDE - Horário do Início de Seu Intervalo:"
        linha_tarde = dataframe[dataframe[coluna] == "TARDE - Horário do Início de Seu Intervalo:"].index
        # Captura a célula abaixo da linha encontrada com os dados do intervalos concedidos da manha e da tarde
        manha = dataframe.iloc[linha_manha[0] + 1][coluna]
        tarde = dataframe.iloc[linha_tarde[0] + 1][coluna]
        
        # Concatena as informações a depender de cada cenário
        if not pd.isna(manha) and not pd.isna(tarde):
            return manha+tarde
        elif pd.isna(manha) and (not pd.isna(tarde)):
            return tarde
        elif pd.isna(tarde) and (not pd.isna(manha)):
            return manha
        else:
            return ''
    except Exception as e:
        st.error(f"Erro ao processar o DataFrame: {e}")
        return None

def exibir_layout(df, df_ctl, intervalos):
    try:
        vias13, vias24 = st.columns([7,5])
        # mostra na coluna da esquerda os trens sentido CEI/SAM
        with vias13:
            st.title(":metro: SENTIDO CEI/SAM:")
            
            # Linha para mostrar o trem que acaba de seguir viagem
            with st.container(border=True):
                # Acha a linha FIM na planilha e encerra a operação
                if df.iloc[0]['Destino'] == 'FIM':
                    st.header("Operação Finalizada! Até Amanhã!")
                else:
                    st.header("Seguiu Viagem:")
                    destino_ultimo = df.iloc[0]['Destino']
                    cor_ultimo, plataforma_ultimo = definir_cor(destino_ultimo, None)
                    st.markdown(
                        f"""
                        <div style="background-color: {cor_ultimo}; border-radius: 10px; ">
                            <h2 style="color: black; padding: 10px;"> Trem: {df.iloc[0]['Trem']} - Destino: {destino_ultimo} - Piloto: {df.iloc[0]['Despacho']}</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.text('')
            # Mostrar o trem e o piloto que deve seguir para a plataforma
            with st.container(border=True):
                # Acha a linha FIM na planilha e encerra a operação
                if df.iloc[0]['Destino'] == 'FIM':
                    st.header("")
                else:    
                    st.header("Seguir Para a Plataforma:")
                    destino_proximo = df.iloc[1]['Destino']
                    cor_proximo, plataforma_proximo = definir_cor(destino_proximo, None)
                    c1,c2 = st.columns([1,7])
                    # Verifica e mostra a Foto na primeira coluna
                    with c1:
                        try:
                            # Caminho para a foto baseada no 'Despacho'
                            foto_path = f"fotos/{df.iloc[1]['Despacho']}.jpg"
                            # Verifica se a foto existe
                            if os.path.exists(foto_path):
                                st.image(foto_path)
                            else:
                                # Se não encontrar, exibe logo.jpg
                                st.image("fotos/logo.jpg")
                        except Exception as e:
                            # Trata erros e exibe uma mensagem
                            st.image("fotos/logo.jpg")
                    # Mostra as informações referentes a foto, trem e pilotos envolvidos
                    with c2:
                        desp = df.iloc[1]['Despacho']
                        cheg = df.iloc[1]['Chegada']
                        obs = df.iloc[1]['Observações']
                        if pd.isna(obs):  # ou use np.isnan(valor) para arrays numéricos
                            obs = ''
                        
                        if pd.isna(desp):
                            piloto = ' ????????? '
                        elif desp == cheg:
                            piloto = f' {desp.upper()} >>> seguir direto >>> '
                        else:
                            piloto = f' {desp.upper()} >>> render >>> {cheg}'
                        
                        st.markdown(
                            f"""
                            <div style="background-color: {cor_proximo}; border-radius: 10px; padding: 5px;">
                                <h2 style="color: black;padding: 15px;"> Trem: {df.iloc[1]['Trem']} Destino: {destino_proximo} <span style="color: red;"> {obs}</span> </h2>
                                <h2 style="color: black;padding: 15px;"> Piloto: {piloto}</h2>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.text('')
            # Linha para mostrar os próximos trens
            with st.container(border=True):
                # Verifica e mostra a Foto na primeira coluna
                if df.iloc[0]['Destino'] == 'FIM':
                    st.header("")
                # Mensagem para caso de último trem da operação
                elif df.iloc[2]['Destino'] == 'FIM':
                    st.markdown("<h1 style='text-align: center; color: red'> ATENÇÃO! Último trem do dia. </h1>", unsafe_allow_html=True)
                else:
                    st.header("Próximos Trens:")    
                    for i in range(2, 9):  # Índices de 0 a 9
                        # Acha a linha FIM na planilha e não mostra outros nomes
                        if df.iloc[i]['Destino'] == 'FIM':
                            break
                        else:
                            destino_proximo = df.iloc[i]['Destino']
                            cor_proximo, plataforma_proximo = definir_cor(destino_proximo, None)  # Define a cor dinamicamente
                            
                            if pd.isna(df.iloc[i]['Trem']):
                                trem = '??'
                            else:
                                trem = df.iloc[i]['Trem']

                            if pd.isna(df.iloc[i]['Despacho']):
                                piloto = ' ????????? '
                            else:
                                piloto = df.iloc[i]['Despacho']
                            
                            st.markdown(
                                f"""
                                <div style="background-color: {cor_proximo}; border-radius: 10px;">
                                    <h2 style="color: black; padding: 10px;"> Trem: {trem} - Destino: {destino_proximo} - Piloto: {piloto}</h2>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            st.text('')

        with vias24: 
            st.title(":metro: SENTIDO CENTRAL:")   
            with st.container(border=True):
                # Acha a linha FIM na planilha e encerra a operação
                if df_ctl.iloc[0]['ORIG'] == 'FIM':
                    st.header("Operação Finalizada! Até Amanhã!")
                else:
                    st.header("Próximos Trens:")
                    # Itera pelas linhas de 2 a 7 do DataFrame
                    for i in range(1, 6):  # Linhas 2 a 7 (index 1 a 6)
                        # Acha a linha FIM na planilha e nao mostra nomes abaixo
                        if df_ctl.iloc[i]['ORIG'] == 'FIM':
                            break
                        else:
                            # caso o destino linha seja vazia
                            if pd.isna(df_ctl.iloc[i]['Nº']) or df_ctl.iloc[i]['DEST'] in ['EST','TF2','TF3','TF1','REC']:
                                pass
                            else:
                                orig = df_ctl.iloc[i]['ORIG']
                                dest = df_ctl.iloc[i]['DEST']
                                cor_proximo, plataforma_proximo = definir_cor(dest, orig)  # Define a cor dinamicamente
                                
                                # Verifica se haverá rendição
                                rendicao = df_ctl.iloc[i]['RENDIÇÃO']
                                if pd.isna(rendicao):  # Caso seja NaN, usa 'RETORNO' e piloto segue o mesmo no trem
                                    rendicao = df_ctl.iloc[i]['RETORNO']
                                    st.markdown(
                                        f"""
                                        <div style="background-color: {cor_proximo}; border-radius: 10px;">
                                            <h2 style="color: black; padding: 10px;"> Trem: {df_ctl.iloc[i]['Nº']} - {rendicao}</h2>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                                # o piloto será rendido por outro
                                else:
                                    ret = df_ctl.iloc[i]['RETORNO']
                                    render = f'<span style="color: black;"> {ret} </span>'  # Adiciona estilo ao texto
                                    # Exibe o layout dinamicamente para cada linha
                                    st.markdown(
                                        f"""
                                        <div style="background-color: #e74d2b; border-radius: 10px;">
                                            <h2 style="color: white; padding: 10px;"> Trem: {df_ctl.iloc[i]['Nº']} - {rendicao.upper()} >>> seguir {plataforma_proximo} <br> render >>> {render} </h2>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                        if df_ctl.iloc[2]['ORIG'] == 'FIM':
                            st.markdown("<h2 style='text-align: center; color: red'> ATENÇÃO! Último trem neste sentido. </h2>", unsafe_allow_html=True)
                        st.text('')
            # Intervalos em andamento
            with st.container(border=True):
                if df.iloc[0]['Destino'] == 'FIM' and df_ctl.iloc[0]['ORIG'] == 'FIM':
                    st.balloons()
                    st.snow()
                else:
                    novo_intervalos = intervalos.split('☻')
                    lista = []
                    for item in novo_intervalos:
                        lista.extend(item.split('-'))
                    
                    hora_atual = datetime.now()
                    st.markdown("<h3 style='text-align: center; color: yellow'> >>>>> INTERVALOS EM ANDAMENTO <<<<< </h3>", unsafe_allow_html=True)
                            
                    for i in range(2, len(lista), 2):  # Percorre índices de horários
                        try:
                            # Tenta converter o item atual em um formato de hora
                            hora_item = datetime.strptime(lista[i], "%H:%M")
                            hora_com_data_atual = datetime.combine(date.today(), hora_item.time())
                            # Calcula a diferença de minutos
                            diferenca = int((hora_atual - hora_com_data_atual).total_seconds() // 60)
                            if diferenca >= 0 and diferenca <= 15:
                                # Exibe o progresso e os detalhes se estiver no limite de 20 minutos
                                progresso = int((diferenca / 15) * 100)
                                st.subheader(f"{lista[i-1].upper()} Inicio: {lista[i]} e resta(m): {15-diferenca}min.")
                                st.progress(progresso)
                            else:
                                pass # verificar
                        except ValueError:
                            # Ignora casos onde o item não é um formato de hora válido
                            pass
            # Intervalos: todos os registros
            with st.container(border=True):
                st.markdown("<h5 style='text-align: center; color: yellow'> >>>>>>>>> REGISTROS DE INTERVALOS <<<<<<<<< </h5>", unsafe_allow_html=True)
                st.text(intervalos)

    except KeyError:
            st.error("Erro ao acessar os dados: Verifique se as colunas 'Despacho', 'Hora', 'RENDIÇÃO', e 'RETORNO' estão presentes no DataFrame.")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")


# Configuração inicial do Streamlit ##################################################################################################
# Ajuste da página do streamlit, otimiza o espaço de cabeçalho
st.set_page_config(page_title="Espelho - Fila de Pilotos", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Placeholder para exibição dinâmica
placeholder = st.empty()

# Botão para carregar o caminho do arquivo na rede
col1, col2 = st.columns([6,2])
with col1:
    caminho_arquivo = st.text_input("Insira o caminho para o arquivo .xls:", "\\\cti-16222\FILA-CLARAS\Fila 2025\\04 - Abril\Semana 3 CLA.xls") 
with col2:
    st.text('') 
    st.text('') 
    carregar = st.button('CARREGAR', use_container_width=True)

# Lógica de monitoramento e atualização dinâmica
if caminho_arquivo and carregar:
    
    while True:
        
        # Lê o arquivo Excel
        df = ler_arquivo_xls(caminho_arquivo)
        # Prepara os intervalos "manhã" e "tarde"
        int_fila = intervalo_manha_tarde(df, "Trem")

        if df is not None:  # Verifica se o DataFrame foi lido com sucesso
            # Busca informações das colunas
            vazias_cei_sam = buscar_primeiras_linhas_vazias(df, "Chegada Saída")
            vazias_ctl = buscar_primeiras_linhas_vazias(df, "Hora")
            # Verifica os resultados
            if vazias_cei_sam is not None or vazias_ctl is not None:
                
                with placeholder.container():
                # Substitui o conteúdo anterior com o layout atualizado
                    exibir_layout(vazias_cei_sam, vazias_ctl, int_fila)
            else:
                
                with placeholder.container():
                # Substitui o conteúdo com uma mensagem de erro
                    st.text("Nenhuma linha encontrada com a condição especificada.")
        else:
            # Substitui o conteúdo com uma mensagem informativa
            st.text("Aguardando um arquivo válido...")

        # Aguarda 10 segundos antes de atualizar novamente
        time.sleep(10)
        # Limpa a tela
        placeholder.text("")