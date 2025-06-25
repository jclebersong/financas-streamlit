import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from database import listar_transacoes, calcular_saldo, obter_resumo_por_tipo, obter_resumo_mensal, adicionar_transacao, adicionar_transacao_parcelada, remover_transacao_por_descricao
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

def formatar_real(valor):
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

        if st.button("Adicionar Transação"):
            try:
                valor_float = float(valor.replace("R$", "").replace(".", "").replace(",", "."))
                data_transacao = datetime.now().strftime("%Y-%m-%d %H:%M")
                if parcelas.strip():
                    qtd = int(parcelas.strip())
                    if qtd > 1:
                        adicionar_transacao_parcelada(usuario, tipo, descricao, valor_float, data_transacao, qtd)
                    else:
                        adicionar_transacao(usuario, tipo, descricao, valor_float, data_transacao)
                else:
                    adicionar_transacao(usuario, tipo, descricao, valor_float, data_transacao)
                st.success("Transação adicionada com sucesso!")
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
    df = pd.DataFrame(transacoes, columns=["ID", "Tipo", "Descrição", "Valor", "Data"])
    #df["Data"] = pd.to_datetime(df["Data"])
    df["Data"] = pd.to_datetime(df["Data"], format='mixed')
    df["Data"] = df["Data"].dt.strftime("%d/%m/%Y %H:%M")
    df["Valor"] = df["Valor"].apply(formatar_real)
    df_exibir = df.drop(columns=["ID"])

    st.subheader("📄 Transações Registradas")

    # if not df.empty:
    #     with st.expander("🗑️ Excluir Transação"):
    #         trans_id = st.selectbox("Selecione o ID para excluir", df["ID"].astype(str))
    #         if st.button("Excluir"):
    #             from database import remover_transacao_por_id
    #             remover_transacao_por_id(trans_id)
    #             st.success("Transação excluída com sucesso!")
    #             st.rerun()
    # selected_rows = st.dataframe(df, use_container_width=True, height=220, hide_index=True)

    if not df.empty:
        with st.expander("🗑️ Excluir Transação"):
            # Excluir pela descrição
            descricoes = df_exibir["Descrição"].unique()
            desc_sel = st.selectbox("Selecione a descrição para excluir", descricoes)
            if st.button("Excluir"):                
                remover_transacao_por_descricao(desc_sel, usuario)
                st.success("Transação(s) excluída(s) com sucesso!")
                st.rerun()
    selected_rows = st.dataframe(df_exibir, use_container_width=True, height=220, hide_index=True)

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
            #linha = f"{row['Data'].strftime('%Y-%m-%d')} - {row['Tipo']}: {row['Descrição']} - R$ {row['Valor']:.2f}"
            linha = f"{row['Data'].strftime('%Y-%m-%d')} - {row['Tipo']}: {row['Descrição']} - {formatar_real(row['Valor'])}"
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

    with col_graf1:
        resumo_tipo = obter_resumo_por_tipo(usuario, tipo_filtro, data_ini_str, data_fim_str, mes if mes != "Todos" else None, ano if ano != "Todos" else None)
        if resumo_tipo:
            tipos, valores = zip(*resumo_tipo)
            fig1, ax1 = plt.subplots(figsize=(3.5, 3.5))
            ax1.pie(valores, labels=tipos, autopct="%1.1f%%", startangle=90)
            ax1.axis("equal")
            st.pyplot(fig1)
        else:
            st.info("Nenhum dado para o gráfico de pizza.")

    with col_graf2:
        resumo_mensal = obter_resumo_mensal(usuario, tipo_filtro, data_ini_str, data_fim_str, mes if mes != "Todos" else None, ano if ano != "Todos" else None)
        if resumo_mensal:
            df_resumo = pd.DataFrame(resumo_mensal, columns=["Mes", "Tipo", "Valor"])
            fig2, ax2 = plt.subplots(figsize=(max(8, len(df_resumo["Mes"].unique()) * 0.7), 4))
            sns.barplot(data=df_resumo, x="Mes", y="Valor", hue="Tipo", ax=ax2)
            for p in ax2.patches:
                height = p.get_height()
                if not pd.isna(height):
                    ax2.text(
                        p.get_x() + p.get_width() / 2.,
                        height + 0.5,
                        formatar_real(height),
                        ha="center", fontsize=7, color="black", rotation=90
                    )
            ax2.set_title("Receitas e Despesas por Mês")
            ax2.tick_params(axis='x', rotation=45)
            st.pyplot(fig2)
            # fig2, ax2 = plt.subplots(figsize=(6, 4))
            # sns.barplot(data=df_resumo, x="Mes", y="Valor", hue="Tipo", ax=ax2)
            # for p in ax2.patches:
            #     height = p.get_height()
            #     if not pd.isna(height):
            #         ax2.text(
            #             p.get_x() + p.get_width() / 2.,
            #             height + 0.5,
            #             formatar_real(height),
            #             #f"R$ {height:.2f}",
            #             ha="center", fontsize=8, color="black"
            #         )
            # ax2.set_title("Receitas e Despesas por Mês")
            # ax2.tick_params(axis='x', rotation=45)
            # st.pyplot(fig2)
        else:
            st.info("Nenhum dado para o gráfico de barras.")
