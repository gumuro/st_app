import streamlit as st
import requests 
import json

from datetime import date
from dateutil.relativedelta import relativedelta

# 関数の定義部分
## 年齢の計算
def calc_age(birth_day):
       today = date.today()
       age = relativedelta(today,birth_day).years
       return age

## サーバー側ファイルの読み込み
def check_known(family_name,first_name,birth_day):
# ファイルの読み込み、パスは作業ディレクトリからの相対パス
       with open("./assets/known_people.json","r",encoding = "utf-8") as f:
              people = json.loads(f.read())
       
# ユーザー入力を辞書へとまとめる
       user = {"first_name":first_name,
              "family_name":family_name,
              "birth_day":birth_day.strftime("%Y-%m-%d")}
# 照合結果を論理型で返す
       return user in people

## Webリソースの取得
@st.cache_data
def onomancy(family_name,first_name):
       url = f"https://enamae.net/result/{family_name}__{first_name}.webp"
       response = requests.get(url)
       return response.content

# 以下、表示部分
st.markdown("# 姓名判断アプリ")

## ユーザー入力の受け取り
### 名前の入力
family_name = st.text_input("姓を入力してください。")
first_name =st.text_input("名を入力してください")

### 誕生日の入力
birth_day = st.date_input("誕生日を選択してください",value=date(2003,8,28))

## ユーザーへの情報表示
if st.button("入力完了"):
       ### フルネームの計算
       full_name = family_name + first_name
       
       ### 年齢の計算
       
       age = calc_age(birth_day)
       if check_known(family_name,first_name,birth_day):
              st.text("あなたのことはよく知っているよ")
              
       ### 姓名判断結果の取得 
       st.text(f"{full_name} ({age}歳)さん、こちらがあなたの姓名判断結果です。。")
       st.image(onomancy(family_name,first_name))
       
       
