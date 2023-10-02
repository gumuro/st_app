import streamlit as st
import json
import requests
import time

MODEL = "facebook/blenderbot-400M-distill"
credentials_dict = json.loads(st.secrets["hugging_face"])
API_TOKEN = credentials_dict["access_token"]


class HuggingFace():
       
       def __init__(self,model_path,token):
              self.model_path = model_path
              self.api_url = f'https://api-inference.huggingface.co/models/{model_path}'
              self.headers = {"Authorization":f"Bearer{token}"}
       
      
       def query(self,payload):
              data = json.dumps(payload)
              response = requests.request("POST",self.api_url,headers=self.headers,data =data)
              return response
  
      
       def check_status(self):
              data = self.query({"inputs":""})
              return data.status_code
  
  
       def inference(self,inputs,parameters={},options = {},timeout = 100):
              i = 0
              while self.check_status() == 503 and i*3 < timeout:
                     if i == 0:
                            print("アプリの立ち上げを待っています")
              time.sleep(3)
              i += 1
              
              
              print("推論結果の取得をしています")
              payload = {"inputs":inputs,"parameters":parameters,"options":options}
              data = self.query(payload)
              print("終了")
              
              result = json.lodas(data.content)
              return result
  
  
bot = HuggingFace(MODEL,API_TOKEN)
if "log" not in st.session_state:
         st.session_state["log"] = []
         
         
         
message = st.chat_input("Say something")
if message:
       
       post = {"name":"user","message":message}
       st.session_state["log"].append(post)
       
       
       response = bot.inference(message)["generated_text"]

       post = {"name":"assistant","message":response}
       st.session_state["log"].append(post)


for post in st.session_state["log"]:
       with st.chat_message(post["name"]):
              st.write(post["message"])
              
