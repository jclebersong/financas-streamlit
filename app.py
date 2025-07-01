import streamlit as st
from database import buscar_usuario
from utils import verificar_senha
from dashboard import show_dashboard
from cadastro import cadastro

st.set_page_config(page_title="Login - Controle Financeiro", layout="wide")

# Acesso à tela de cadastro
if st.session_state.get("cadastro"):
    cadastro()

# Verifica se já está logado
elif st.session_state.get("usuario"):
    show_dashboard(st.session_state["usuario"])

# Exibe tela de login
else:
    st.title("🔐 Login - Controle de Finanças")

    usuario = st.text_input("Usuário", key="login_usuario")
    senha = st.text_input("Senha", type="password", key="login_senha")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Entrar"):
            hash_salvo = buscar_usuario(usuario)
            if hash_salvo and verificar_senha(senha, hash_salvo[0]):
                st.session_state["usuario"] = usuario
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    with col2:
        if st.button("Cadastrar novo usuário"):
            st.session_state["cadastro"] = True
            st.rerun()
