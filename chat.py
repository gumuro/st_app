import streamlit as st
import json
import requests
import time


MODEL = "facebook/blenderbot-400M-distill"
credentials_dict = json.loads(st.secrets["hugging_face"])
API_TOKEN = credentials_dict["access_token"]


# Huggin Face とのインターフェース
class HuggingFace():


    def __init__(self, model_path, token):
        self.model_path = model_path
        self.api_url = f"https://api-inference.huggingface.co/models/{model_path}"
        self.headers = {"Authorization": f"Bearer {token}"}


    # API通信の基本メソッド
    def query(self, payload):
        data = json.dumps(payload)
        response = requests.request("POST", self.api_url, headers=self.headers, data=data)
        return response


    # APIの稼働状況の確認
    def check_status(self):
        data = self.query({"inputs":""})
        return data.status_code


    # APIにテキストを送り、稼働を待ってレスポンスを受け取る
    def inference(self, inputs, parameters={}, options={}, timeout=100):
        i = 0
        # API の稼働状況を3秒ごとに確認
        while self.check_status() == 503 and i*3 < timeout:
            if i == 0:
                print("アプリの立ち上げを待っています")
            time.sleep(3)
            i += 1
        # APIにテキストを送信
        print("推論結果の取得をしています")
        payload = {"inputs":inputs, "parameters":parameters, "options":options}
        data = self.query(payload)
        print("終了")
        # レスポンスのJSONデータを辞書型に変換
        result = json.loads(data.content)
        return result


# インターフェースのインスタンス化
bot = HuggingFace(MODEL, API_TOKEN)
# 会話ログの初期化
if "log" not in st.session_state:
    st.session_state["log"] = []


# ユーザーの入力
message = st.chat_input("Say something")
if message:
    # ユーザー入力の会話ログへの追加
    post = {"name":"user", "message":message}
    st.session_state["log"].append(post)


    # インターフェースからの返答
    response = bot.inference(message)["generated_text"]
    # インターフェースからの返答の会話ログへの追加
    post = {"name":"assistant", "message":response}
    st.session_state["log"].append(post)


    # 会話ログの表示
    for post in st.session_state["log"]:
        with st.chat_message(post["name"]):
            st.write(post["message"])
