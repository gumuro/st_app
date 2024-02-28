import streamlit as st
import requests
from datetime import datetime
from joblib import load
import numpy as np
import joblib
import pandas as pd
from PIL import Image


# 定义城市和季节判断函数
cities = {
        "北海道":2130037,
        "青森県":2130656 ,
        "岩手県": 2112518,
        "宮城県":2111888,
        "秋田県":2113124 ,
        "山形県": 2110554,
        "福島県":2112922 ,
        "茨城県": 1862033,
        "栃木県":1850310 ,
        "群馬県": 1863501,
        "埼玉県":6940394 ,
        "千葉県":2113014 ,
        "東京都":1850144,
        "神奈川県": 1860291,
        "新潟県":1855429 ,
        "富山県":1849872 ,
        "石川県": 1861387,
        "福井県":1863983,
        "山梨県":1848649 ,
        "長野県":1856210 ,
        "岐阜県":1863640,
        "静岡県": 1851715,
        "愛知県":1865694 ,
        "三重県":1857352 ,
        "滋賀県":1852553,
        "京都府": 1857910,
        "大阪府": 1853909,
        "兵庫県":1862047,
        "奈良県": 1855608,
        "和歌山県": 1926004,
        "鳥取県":1849890 ,
        "島根県": 1852442,
        "岡山県":1854381 ,
        "広島県": 1862413,
        "山口県":1848681 ,
        "徳島県": 1850157,
        "香川県":1860834 ,
        "愛媛県": 1864226,
        "高知県":1859133 ,
        "福岡県": 1863958,
        "佐賀県":1853299 ,
        "長崎県": 1856156,
        "熊本県": 1858419,
        "大分県":1854484 ,
        "宮崎県": 1856710,
        "鹿児島県": 1860825,
        "沖縄県":1894616,
   
}

def determine_season(date):
    month = date.month
    if month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Autumn'
    else:
        return 'Winter'

# 初始化布局和样式
st.markdown("""
<style>
.weather-card {
    background-color: #90e0ee;
    color: #333;
    padding: 10px 10px;
    border-radius: 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: sans-serif;
}
.city-select {
    border: none;
    background-color: inherit;
    font-size: 1em;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

# 选择城市的下拉列表
st.write("都道府県を選択してください")
city_name = st.selectbox("", options=list(cities.keys()), format_func=lambda x: x, key="city")

# 获取选中城市的天气数据
API_KEY = "74559e2ae3ff7c8da2c4fe6c70609ee7"
city_id = cities[city_name]

def get_weather(city_id, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

weather_data = get_weather(city_id, API_KEY)

# 处理API数据并计算季节
current_date = datetime.now()
season = determine_season(current_date)
max_tem = weather_data['main']['temp_max']
min_tem = weather_data['main']['temp_min']
mean_tem = (max_tem + min_tem) / 2
average_humidity = weather_data['main']['humidity']
average_wind_speed = weather_data['wind']['speed']
sensible_temperature = weather_data['main']['feels_like']

# 加载模型和标签编码器
model_path = 'random_forest_classifier.joblib'
model = load(model_path)
season_encoder = joblib.load('season_encoder.joblib')

# 使用标签编码器转换新的输入数据
season_encoded = season_encoder.transform([season])

# 模型输入数据
input_data = [
    max_tem,
    min_tem,
    mean_tem,
    average_humidity,
    average_wind_speed,
    sensible_temperature,
    season_encoded[0]  # 季节编码
]


# 获取穿衣建议
clothing_advice_list = model.predict([input_data])[0]

# 创建天气卡片和展示穿衣建议
icon_code = weather_data['weather'][0]['icon']
icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
current_time = datetime.now().strftime("%H:%M %Y-%m-%d %a")

st.markdown(f"""
<div class="weather-card">
    <div>
        <h2>{city_name}</h2>
    </div>
    <div>
        <img src="{icon_url}" alt="weather icon">
    </div>
    <div>
        <p>気温： {weather_data['main']['temp_min']}~{weather_data['main']['temp_max']}°C</p>
        <p>体感気温：{weather_data['main']['feels_like']}°C</p>
        <p>風速： {weather_data['wind']['speed']} m/s</p>
        <p>湿度： {weather_data['main']['humidity']}%</p>
    </div>
    <div>
        <p>{current_time}</p>
    </div>
</div>
""", unsafe_allow_html=True)

#st.write(f"Clothing advice for today: {clothing_advice[0]}")


clothes_df = pd.read_excel('clothes.xlsx')
      
unique_clothing_types = set(clothing_advice_list)

# 设置Streamlit布局
st.write("　　　　　　")
st.write("　　　　　　")
col1, col2 = st.columns([1, 2])  # 左边一列，右边两列宽度

with col1:
    st.write("         ")
    st.write("選択した服")

# 显示每件衣服
for index, clothing_type in enumerate(unique_clothing_types):
    matched_rows = clothes_df[clothes_df['type'] == clothing_type]
    if not matched_rows.empty:
        # 取得图片路径
        image_path = matched_rows.iloc[0]['name']  # 确保这里是正确的列名
        try:
            # 使用Pillow加载图片
            image = Image.open(image_path)

            # 根据衣服数量分配到左边或右边列
            col = col1 if index == 0 else col2

            with col:
                # 直接使用 Streamlit 函数显示图片
                st.image(image, caption=clothing_type, width=150)
        except FileNotFoundError:
            st.error(f"无法找到文件：{image_path}")


