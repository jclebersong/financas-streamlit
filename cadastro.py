import streamlit as st
from database import criar_usuario, buscar_usuario
from utils import hash_senha


def cadastro():
    st.title("\U0001F4DD Cadastro de Novo Usuário")
    
    novo_usuario = st.text_input("Novo Usuário")
    nova_senha = st.text_input("Nova Senha", type="password")
    confirmar_senha = st.text_input("Confirmar Senha", type="password")

    if st.button("Cadastrar"):
        if not novo_usuario or not nova_senha:
            st.warning("Preencha todos os campos.")
        elif nova_senha != confirmar_senha:
            st.error("As senhas não coincidem.")
        elif buscar_usuario(novo_usuario):
            st.error("Usuário já existe.")
            st.session_state.clear()
            st.rerun() 
        else:
            senha_hash = hash_senha(nova_senha)          
            try:
                print(f"Usuário: {novo_usuario}, Senha Hash: {senha_hash}")
                if criar_usuario(novo_usuario, senha_hash):
                    st.success("Usuário cadastrado com sucesso!")
                    st.session_state.clear()
                    st.rerun()                    
                else:
                    st.error("Erro ao cadastrar usuário.")
            except Exception as e:
                st.error(f"Erro ao cadastrar usuário: {e}")
