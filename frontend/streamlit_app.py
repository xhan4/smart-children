# ui/streamlit_app.py
import streamlit as st
from agent.agent import get_agent
from db.mongodb import get_db

st.title("智能鸡禽养殖问答系统")

# 用户输入问题
question = st.text_input("请输入您的问题：")

if st.button("提交"):
    agent = get_agent()
    answer = agent.run(question)
    st.write("回答：", answer)
    # 保存到 MongoDB
    db = get_db()
    db.interactions.insert_one({"question": question, "answer": answer})
    st.success("记录已保存。")

st.sidebar.title("历史问答记录")
db = get_db()
records = db.interactions.find().sort("_id", -1).limit(10)
for record in records:
    st.sidebar.write(f"问：{record['question']}")
    st.sidebar.write(f"答：{record['answer']}")
    st.sidebar.markdown("---")
