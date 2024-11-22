import streamlit as st
import app as ai
import textwrap
from knowledge_base import create_knowledge_base, del_index_if_exist

st.title("Azure Project Generator")

btn = st.button("Create Knowledgebase")

index_name: str = "langchain-vector-demo"

if btn:
    msg = del_index_if_exist(index_name)
    st.write(msg)
    create_knowledge_base(index_name)

certification = st.selectbox(
    'Microsoft Azure Certification',
    ('AZ-104', 'AZ-204', 'AZ-305', 'AZ-400'))

level = st.selectbox(
    'Project Level',
    ('beginner', 'intermediate', 'advanced'))


if certification and level:
    response = ai.project_idea(certification, level)
    st.text(response)
