import streamlit as st
import requests

# 将这里的YOUR_API_TOKEN替换为您的Hugging Face API令牌
API_TOKEN = "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"
MODEL = "gpt2"  # 或者您想使用的任何其他模型

# 设置Hugging Face API的URL
api_url = f"https://api-inference.huggingface.co/models/{MODEL}"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

def query(model_input):
    """发送请求到Hugging Face模型API"""
    payload = {
        "inputs": model_input
    }
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

st.set_page_config(page_title="ChatGPT ", layout="wide")
st.title("Chatbot")

user_input = st.text_input("You:", key="user_input")

if user_input:
    # 发送用户输入到ChatGPT模型
    response = query(user_input)
    # 显示模型的回复
    if response:
        # 检查响应格式并提取生成的文本
        generated_text = response[0].get('generated_text', "") if isinstance(response, list) else response.get('generated_text', "")
        if generated_text:
            # 创建列以显示头像和文本
            col1, col2 = st.columns([1, 5])
            with col1:
                st.image("user_avatar.png", width=50)  # 确保你有一个用户头像文件
            with col2:
                st.write(f"You: {user_input}")

            col1, col2 = st.columns([1, 5])
            with col1:
                st.image("chatgpt_avatar.png", width=50)  # 确保你有一个ChatGPT头像文件
            with col2:
                st.write(f"chatbot: {generated_text}")
        else:
            st.error("Error getting response from the model.")
    else:
        st.error("Received no response from the model.")
