import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from database import listar_transacoes, calcular_saldo, obter_resumo_por_tipo, obter_resumo_mensal, adicionar_transacao, adicionar_transacao_parcelada, remover_transacao_por_descricao
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import plotly.express as px
import plotly.graph_objects as go

import locale
#locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# def formatar_real(valor):
#     if isinstance(valor, str):
#         valor = valor.replace("R$", "").replace(".", "").replace(",", ".")
#         try:
#             valor = float(valor)
#         except Exception:
#             valor = 0.0
#     return locale.currency(valor, grouping=True, symbol=True)
def formatar_real(valor):
    if isinstance(valor, str):
        valor = valor.replace("R$", "").replace(".", "").replace(",", ".")
        try:
            valor = float(valor)
        except Exception:
            valor = 0.0
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def show_dashboard(usuario):
    st.set_page_config(layout="wide")

    st.markdown("""
        <style>
            .main { background-color: #f8f9fa; }
            .block-container { padding-top: 1rem; padding-bottom: 0rem; }
            h1, h2, h3, h4, h5, h6 { color: #202124; }
            .stButton button { background-color: #0066cc; color: white; border-radius: 6px; padding: 0.4rem 0.8rem; }
            .stButton button:hover { background-color: #005bb5; }
            .stDataFrame { margin-bottom: 0rem; }
            .st-expanderHeader { font-weight: bold; font-size: 16px; }
        </style>
    """, unsafe_allow_html=True)

    st.title(f"📊 Dashboard - {usuario}")

    if st.button("🔓 Logout"):
        st.session_state.clear()
        st.rerun()

    with st.expander("➕ Adicionar Receita ou Despesa", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"], key="tipo")
            descricao = st.text_input("Descrição", key="descricao")
        with col2:
            valor = st.text_input("Valor (use ponto ou vírgula)", key="valor")
            parcelas = st.text_input("Parcelas (opcional)", key="parcelas")
            data_cadastro = st.date_input("Data de cadastro", value=None)

        if st.button("Adicionar Transação"):
            try:
                valor_float = float(valor.replace("R$", "").replace(".", "").replace(",", "."))
                #data_transacao = datetime.now().strftime("%Y-%m-%d %H:%M")
                data_transacao = data_cadastro.strftime("%Y-%m-%d %H:%M")
                if parcelas.strip():
                    qtd = int(parcelas.strip())
                    if qtd > 1:
                        adicionar_transacao_parcelada(usuario, tipo, descricao, valor_float, data_transacao, qtd)
                    else:
                        adicionar_transacao(usuario, tipo, descricao, valor_float, data_transacao)
                else:
                    adicionar_transacao(usuario, tipo, descricao, valor_float, data_transacao)
                st.success("Transação adicionada com sucesso!")
                # Limpa os campos
                st.session_state["descricao"] = ""
                st.session_state["valor"] = ""
                st.session_state["parcelas"] = ""
            except Exception as e:
                st.error(f"Erro ao adicionar: {e}")

    st.markdown("---")
    st.subheader("🎯 Filtros de Transações")
    filtro_col1, filtro_col2, filtro_col3, filtro_col4 = st.columns(4)
    with filtro_col1:
        tipo_filtro = st.selectbox("Tipo", ["Todos", "Receita", "Despesa"])
    with filtro_col2:
        mes = st.selectbox("Mês", ["Todos"] + [f"{i:02d}" for i in range(1, 13)])
    with filtro_col3:
        ano = st.text_input("Ano", "Todos")
    with filtro_col4:
        data_ini = st.date_input("Data Inicial", value=None)
        data_fim = st.date_input("Data Final", value=None)

    data_ini_str = data_ini.strftime("%Y-%m-%d") if data_ini else None
    data_fim_str = data_fim.strftime("%Y-%m-%d") if data_fim else None

    transacoes = listar_transacoes(usuario, tipo_filtro, data_ini_str, data_fim_str, mes if mes != "Todos" else None, ano if ano != "Todos" else None)
    df = pd.DataFrame(transacoes)

    if not df.empty:
        df.rename(columns={
            "id": "ID",
            "tipo": "Tipo",
            "descricao": "Descrição",
            "valor": "Valor",
            "data": "Data"
        }, inplace=True)

        df = df[["ID", "Tipo", "Descrição", "Valor", "Data"]]
        df["Data"] = pd.to_datetime(df["Data"], format='mixed')
        df["Data"] = df["Data"].dt.strftime("%d/%m/%Y %H:%M")
        df_exibir = df.copy()
        df_exibir["Valor"] = df_exibir["Valor"].apply(formatar_real)
        df_exibir = df_exibir.drop(columns=["ID"])

        selected_rows = st.dataframe(df_exibir, use_container_width=True, height=220, hide_index=True)
    else:
        st.info("Nenhuma transação encontrada com esse filtro.")
   
    st.subheader("📄 Transações Registradas")

    if not df.empty:
        with st.expander("🗑️ Excluir Transação"):
            # Excluir pela descrição
            descricoes = df_exibir["Descrição"].unique()
            desc_sel = st.selectbox("Selecione a descrição para excluir", descricoes)
            if st.button("Excluir"):                
                remover_transacao_por_descricao(desc_sel, usuario)
                st.success("Transação(s) excluída(s) com sucesso!")
                st.session_state["trans_id"] = None
                st.rerun()
    #selected_rows = st.dataframe(df_exibir, use_container_width=True, height=220, hide_index=True)

    output_excel = BytesIO()
    with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Transações")
    output_excel.seek(0)

    st.download_button(
        label="📥 Exportar para Excel",
        data=output_excel,
        file_name="transacoes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🧾 Exportar para PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Relatório de Transações", ln=True, align="C")
        pdf.ln(10)
        for index, row in df.iterrows():            
            data_formatada = datetime.strptime(row['Data'], "%d/%m/%Y %H:%M").strftime("%Y-%m-%d")
            linha = f"{data_formatada} - {row['Tipo']}: {row['Descrição']} - {formatar_real(row['Valor'])}"
            pdf.multi_cell(0, 10, linha)
        pdf_output = BytesIO()
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        pdf_output.write(pdf_bytes)
        pdf_output.seek(0)
        st.download_button(
        label="⬇️ Baixar PDF",
        data=pdf_output.getvalue(),
        file_name="relatorio_transacoes.pdf",
        mime="application/pdf"
    )

    st.subheader("📈 Análise Gráfica")
    col_graf1, col_graf2 = st.columns(2)

    # with col_graf1:
    #     resumo_tipo = obter_resumo_por_tipo(usuario, tipo_filtro, data_ini_str, data_fim_str, mes if mes != "Todos" else None, ano if ano != "Todos" else None)
    #     if resumo_tipo:
    #         tipos, valores = zip(*resumo_tipo)
    #         fig1, ax1 = plt.subplots(figsize=(3.5, 3.5))
    #         ax1.pie(valores, labels=tipos, autopct="%1.1f%%", startangle=90)
    #         ax1.axis("equal")
    #         st.pyplot(fig1)
    #     else:
    #         st.info("Nenhum dado para o gráfico de pizza.")
    with col_graf1:
        resumo_tipo = obter_resumo_por_tipo(
        usuario, tipo_filtro, data_ini_str, data_fim_str,
        mes if mes != "Todos" else None,
        ano if ano != "Todos" else None
    )

    if resumo_tipo:
        tipos, valores = zip(*resumo_tipo)
        df_pizza = pd.DataFrame({
            "Tipo": tipos,
            "Valor": valores
        })

        fig = px.pie(
            df_pizza,
            names="Tipo",
            values="Valor",
            title="Distribuição por Tipo",
            hole=0.4  # ou coloque 0.4 para gráfico de rosca (donut chart)
        )

        fig.update_traces(
            textinfo="percent+label",
            textfont_size=14
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Nenhum dado para o gráfico de pizza.")

    # with col_graf2:
    #     resumo_mensal = obter_resumo_mensal(usuario, tipo_filtro, data_ini_str, data_fim_str, mes if mes != "Todos" else None, ano if ano != "Todos" else None)
    #     if resumo_mensal:
    #         df_resumo = pd.DataFrame(resumo_mensal, columns=["Mes", "Tipo", "Valor"])

    #         # Pivot para separar Receita e Despesa por mês
    #         df_pivot = df_resumo.pivot_table(index="Mes", columns="Tipo", values="Valor", aggfunc="sum").fillna(0)
           
    #         # Garante que todas as colunas existem
    #         for col in ["Receita", "Despesa", "Saldo"]:
    #             if col not in df_pivot.columns:
    #                 df_pivot[col] = 0
            
    #         # Calcula o saldo do mês            
    #         df_pivot["Saldo"] = df_pivot.get("Receita", 0) - df_pivot.get("Despesa", 0)

    #         df_pivot = df_pivot[["Receita", "Despesa", "Saldo"]]

    #         fig2, ax2 = plt.subplots(figsize=(max(10, len(df_pivot.index) * 1.2), 7))  # Aumenta largura e altura
    #         df_pivot[["Receita", "Despesa", "Saldo"]].plot(kind="bar", ax=ax2, width=0.7)  # barras mais largas

    #         ymax = df_pivot[["Receita", "Despesa", "Saldo"]].values.max() * 1.20
    #         ymin = min(0, df_pivot[["Receita", "Despesa", "Saldo"]].values.min() * 1.20)
    #         ax2.set_ylim(ymin, ymax)

    #         for container in ax2.containers:
    #             ax2.bar_label(container, fmt="%.2f", padding=4, fontsize=12, rotation=90, label_type='edge')  # fonte maior e mais espaçamento

    #         ax2.set_title("Receitas, Despesas e Saldo por Mês", fontsize=18)
    #         ax2.set_ylabel("Valor", fontsize=14)
    #         ax2.set_xlabel("Mês", fontsize=14)
    #         ax2.tick_params(axis='x', rotation=45, labelsize=12)
    #         ax2.tick_params(axis='y', labelsize=12)
    #         ax2.legend(fontsize=12)
    #         st.pyplot(fig2)
            
                      
    #     else:
    #         st.info("Nenhum dado para o gráfico de barras.")
    with col_graf2:
        resumo_mensal = obter_resumo_mensal(
        usuario, tipo_filtro, data_ini_str, data_fim_str, 
        mes if mes != "Todos" else None, 
        ano if ano != "Todos" else None
    )
    
    if resumo_mensal:
        df_resumo = pd.DataFrame(resumo_mensal, columns=["Mes", "Tipo", "Valor"])

        # Pivot para Receita, Despesa por mês
        df_pivot = df_resumo.pivot_table(index="Mes", columns="Tipo", values="Valor", aggfunc="sum").fillna(0)

        for col in ["Receita", "Despesa"]:
            if col not in df_pivot.columns:
                df_pivot[col] = 0

        df_pivot["Saldo"] = df_pivot.get("Receita", 0) - df_pivot.get("Despesa", 0)
        df_pivot = df_pivot.reset_index()

        # Traduz os nomes dos meses para pt-BR
        MESES_PT = {
            "January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril",
            "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto",
            "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro",
            "Jan": "Jan", "Feb": "Fev", "Mar": "Mar", "Apr": "Abr",
            "May": "Mai", "Jun": "Jun", "Jul": "Jul", "Aug": "Ago",
            "Sep": "Set", "Oct": "Out", "Nov": "Nov", "Dec": "Dez",
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }

        df_pivot["Mes"] = df_pivot["Mes"].map(MESES_PT).fillna(df_pivot["Mes"])

        # Converte para formato "long" para usar no plotly
        df_long = df_pivot.melt(id_vars="Mes", value_vars=["Receita", "Despesa", "Saldo"], 
                                var_name="Tipo", value_name="Valor")

        # Criação do gráfico com plotly
        fig = px.bar(
            df_long, 
            x="Mes", 
            y="Valor", 
            color="Tipo", 
            barmode="group", 
            text_auto=".2f",
            title="Receitas, Despesas e Saldo por Mês"
        )

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Valor",
            legend_title="Tipo",
            bargap=0.2,
            font=dict(size=14),
            height=600,
            xaxis_tickangle=-45
        )

        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("Nenhum dado para o gráfico de barras.")
