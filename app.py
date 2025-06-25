# import streamlit as st
# from database import buscar_usuario
# from utils import verificar_senha
# from dashboard import show_dashboard

# st.set_page_config(page_title="Login - Controle Financeiro", layout="wide")

# def login():
#     st.title("\U0001F512 Login - Controle de Finanças")
#     usuario = st.text_input("Usuário")
#     senha = st.text_input("Senha", type="password")

#     if st.button("Entrar"):
#         hash_salvo = buscar_usuario(usuario)
#         if hash_salvo and verificar_senha(senha, hash_salvo[0]):
#             st.session_state["usuario"] = usuario
#             st.success("Login realizado com sucesso!")
#             st.rerun()
#         else:
#             st.error("Usuário ou senha inválidos.")

#     if st.button("Cadastrar novo usuário"):
#         from cadastro import cadastro
#         cadastro()
#         st.stop()

# if "usuario" not in st.session_state:
#     login()
# else:
#     show_dashboard(st.session_state["usuario"])
import streamlit as st
from database import buscar_usuario
from utils import verificar_senha
from dashboard import show_dashboard
from cadastro import cadastro

st.set_page_config(page_title="Login - Controle Financeiro", layout="wide")

if "usuario" in st.session_state:
    show_dashboard(st.session_state["usuario"])

elif st.session_state.get("cadastro"):
    cadastro()

else:
    st.title("🔐 Login - Controle de Finanças")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        hash_salvo = buscar_usuario(usuario)
        if hash_salvo and verificar_senha(senha, hash_salvo[0]):
            st.session_state["usuario"] = usuario
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    if st.button("Cadastrar novo usuário"):
        st.session_state["cadastro"] = True
        st.rerun()

