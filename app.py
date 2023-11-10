from openai import OpenAI
import streamlit as st
import mysql.connector

st.title("Ainnov1 ChatGPT.")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# MySQL 연결 설정
mysql_config = {
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "host": st.secrets["DB_HOST"],
    "database": st.secrets["DB_NAME"],
}
connection = mysql.connector.connect(**mysql_config)
cursor = connection.cursor()

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("안녕하세요. 에이이노브입니다. 무엇을 도와드릴까요?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            # full_response += response.choices[0].delta.get("content", "")
            # print(response.choices[0].delta.content)
            if response.choices[0].delta.content is not None:
                full_response += response.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

        # MySQL에 INSERT 하기
        insert_query = "INSERT INTO streamlit_chat_logs (user_prompt, assistant_response) VALUES (%s, %s)"
        insert_values = (prompt, full_response)
        cursor.execute(insert_query, insert_values)
        connection.commit()

    st.session_state.messages.append({"role": "assistant", "content": full_response})


# MySQL 연결 종료
cursor.close()
connection.close()
