import pandas as pd
import numpy as np
import seaborn as sns
import io
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
plt.rcParams['font.family'] = 'meiryo'

@st.cache_data
def load_data():
    # 请确保文件路径正确
    data = pd.read_excel('NTT Com DD株式会社.xlsx')
    return data

@st.cache_data
def process_data(data):
    data_one = data[['端末ID', 'AiTag ID', '関心度', 'ダウンロード回数', 'メール転送回数']]
    data_one = data_one.copy()
    data_one['関心度'] = data_one['関心度'].apply(lambda x: int(x) if x.isdigit() else 0)
    data_one['訪問回数'] = data_one.groupby('AiTag ID')['AiTag ID'].transform('count')
    data_one['興味度スコア'] = (0.5 * data_one['ダウンロード回数']) + (0.3 * data_one['メール転送回数']) + (0.2 * data_one['訪問回数'] )

    features = data_one[['興味度スコア', '関心度']]

    # データの正規化
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # データを3つのクラスタに分割
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(scaled_features)
    
    # クラスタの結果を元のデータフレームに追加
    data_one['クラスタ'] = clusters
    
    # 计算'関心度'和'興味度スコア'的总和
    data_one['total_score'] = data_one['興味度スコア'] + data_one['関心度']
    # 获取total_score的最大和最小值
    max_score = data_one['total_score'].max()
    min_score = data_one['total_score'].min()

    # 根据最大和最小值定义高、中和低的阈值
    # 这里，我使用了最大值的80%作为高的阈值，和最大值的50%作为中的阈值，您可以根据需要调整这些百分比。
    high_threshold = max_score * 0.80
    medium_threshold = max_score * 0.40

    # 判断'興味度スコア'或'関心度'是否为最小值
    is_min_value = (data_one['興味度スコア'] <= 0.1) | (data_one['関心度'] == 0)

    # 为满足最小值条件的记录分配低值
    data_one['重要度'] = np.where(is_min_value, '低', '未分类')

    # 对于未被分类为'低'的记录，基于定义的阈值进行分类
    data_one['重要度'] = np.where(data_one['重要度'] != '未分类', data_one['重要度'], 
                            np.where(data_one['total_score'] > high_threshold, '高', 
                            np.where(data_one['total_score'] > medium_threshold, '中', '低')))
    return data_one

def main():
    st.title("来場者の情報")

    data = load_data()
    data_one = process_data(data)

    # 创建交互式散点图
    fig = px.scatter(data_one, x='興味度スコア', y='関心度', color='重要度', 
                     hover_data=['端末ID', 'AiTag ID', '関心度', 'ダウンロード回数', 'メール転送回数'],
                     color_discrete_map={"高": "red", "中": "blue", "低": "green"})
    st.plotly_chart(fig)

    # 选择要查看的客户类别
    cluster = st.selectbox("来場者の重要度", ["高", "中", "低"])

    # 显示对应类别的表格信息
    filtered_data = None
    if cluster == "高":
        filtered_data = data_one[data_one['重要度'] == "高"]
    elif cluster == "中":
        filtered_data = data_one[data_one['重要度'] == "中"]
    else:
        filtered_data = data_one[data_one['重要度'] == "低"]

    # 准备下载按钮
    towrite = io.BytesIO()
    downloaded_file = filtered_data[['端末ID', 'AiTag ID', '関心度', 'ダウンロード回数', 'メール転送回数', '興味度スコア', '重要度']]
    downloaded_file.to_excel(towrite, index=False, engine='openpyxl')  # 将数据写入Excel格式
    towrite.seek(0)  # 从文件的开头开始读取

    # 添加下载按钮
    st.download_button(
        label="ダウンロード",
        data=towrite,
        file_name="data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 显示表格
    st.dataframe(filtered_data[['端末ID', 'AiTag ID', '関心度', 'ダウンロード回数', 'メール転送回数', '興味度スコア', '重要度']])

if __name__ == '__main__':
    main()
