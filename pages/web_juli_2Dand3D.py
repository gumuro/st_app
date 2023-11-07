import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
import streamlit as st
import io


st.set_page_config(layout="wide")
st.title("NTT Com DD株式会社_来場者の情報")
st.write("")
st.subheader("データの分布")
option = st.radio("", ['役職なし', '役職あり'])

# 公共的数据处理函数
def process_data(filename, columns):
    data = pd.read_excel(filename)
    data_one = data[columns].copy()
    data_one['関心度'] = data_one['関心度'].apply(lambda x: int(x) if x.isdigit() else 0)
    data_one['訪問回数'] = data_one.groupby('AiTag ID')['AiTag ID'].transform('count')
    return data_one

# 数据处理和聚类分析
if option == '役職なし':
    # 役職なしのデータ処理ロジックを記述
    data_one = process_data('NTT Com DD株式会社.xlsx', ['端末ID', 'AiTag ID', '関心度', 'ダウンロード回数', 'メール転送回数'])
    data_one['興味度スコア'] = (0.5 * data_one['ダウンロード回数']) + (0.3 * data_one['メール転送回数']) + (0.2 * data_one['訪問回数'])
else:
    # 役職ありのデータ処理ロジックを記述
    data_one = process_data('NTT Com DD株式会社_kojin_1.xlsx', ['端末ID', 'AiTag ID', '関心度', 'ダウンロード回数', 'メール転送回数', '役職の値'])
    data_one['興味度スコア'] = (0.4 * data_one['関心度']) + (0.3 * data_one['ダウンロード回数']) + (0.2 * data_one['メール転送回数']) + (0.1 * data_one['訪問回数'])
    data_one['役職の値'].fillna(0, inplace=True)

# 共通逻辑
data_one['distance_to_origin'] = np.sqrt(data_one['興味度スコア']**2 + data_one['関心度']**2)

# 使用原始数据进行分层
kmeans = KMeans(n_clusters=3, random_state=42)
fit_columns = ['興味度スコア', '関心度', 'distance_to_origin'] if option == '役職なし' else ['興味度スコア', '役職の値', 'distance_to_origin']
clusters = kmeans.fit_predict(data_one[fit_columns])

# 将clusters的结果加入到数据集中
data_one['クラスタ'] = clusters

# 获取每个类别的中心距离原点的均值
cluster_centers = kmeans.cluster_centers_
distance_to_origin_means = np.linalg.norm(cluster_centers, axis=1)

# 对距离进行排序并获取索引
sorted_clusters = np.argsort(distance_to_origin_means)

# 根据距离均值为clusters映射到高、中、低
cluster_map = {
    sorted_clusters[0]: '低',
    sorted_clusters[1]: '中',
    sorted_clusters[2]: '高'
}
data_one['重要度'] = data_one['クラスタ'].map(cluster_map)

# 根据选择来设置2D和3D散点图的y轴
y_column_2d = '関心度' if option == '役職なし' else '役職の値'

# 创建两个并排的列
col1, col2 = st.columns(2)

# 在第一列中显示2D散点图
with col1:
    fig_2d = px.scatter(data_one, x='興味度スコア', y=y_column_2d, color='重要度')
    st.plotly_chart(fig_2d, use_container_width=True)

# 在第二列中显示3D散点图
with col2:
    z_column_3d = 'distance_to_origin' if option == '役職なし' else '役職の値'
    fig_3d = px.scatter_3d(data_one, x='興味度スコア', y=y_column_2d, z=z_column_3d, color='重要度')
    st.plotly_chart(fig_3d, use_container_width=True)


st.write("")
st.write("")
st.subheader("来場者の重要度を選択してください")
relevance_option = st.radio("", ['高', '中', '低'])

# 显示相应的数据表格
data_display = data_one[data_one['重要度'] == relevance_option]
st.write(data_display)


# 准备session_state
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False


towrite = io.BytesIO()
downloaded_file = data_display[['端末ID', 'AiTag ID', '関心度', 'ダウンロード回数', 'メール転送回数', '興味度スコア', '重要度']]
downloaded_file.to_excel(towrite, index=False, engine='openpyxl')  # 将数据写入Excel格式
towrite.seek(0)  # 从文件的开头开始读取

# 添加下载按钮
st.download_button(
       label='📥 ダウンロード',
       data=towrite,
       file_name="data.xlsx",
       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )