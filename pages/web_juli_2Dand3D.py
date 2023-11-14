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
clusters = kmeans.fit_predict(data_one[['興味度スコア', '関心度', 'distance_to_origin']]) if option == '役職なし' else kmeans.fit_predict(data_one[['興味度スコア', '役職の値', 'distance_to_origin']])
data_one['クラスタ'] = clusters

# 将clusters的结果加入到数据集中并映射到高中低
cluster_centers = kmeans.cluster_centers_
distance_to_origin_means = np.linalg.norm(cluster_centers, axis=1)
sorted_clusters = np.argsort(distance_to_origin_means)
cluster_map = {sorted_clusters[0]: '低', sorted_clusters[1]: '中', sorted_clusters[2]: '高'}
data_one['重要度'] = data_one['クラスタ'].map(cluster_map)

# 根据关心度调整重要度
if option == '役職なし':
    data_one['重要度'] = np.where(data_one['関心度'] >= 5, '高',
                                  np.where(data_one['関心度'].between(3, 4), '中', '低'))
else:
    # 如果选择了“役職あり”，则同时考虑“関心度”和“役職の値”来判定重要度
    conditions = [
        (data_one['関心度'] >= 5) & (data_one['役職の値'] > 6),
        (data_one['関心度'].between(3, 4)) | ((data_one['役職の値'] >= 4) & (data_one['役職の値'] <= 6))
    ]
    choices = ['高', '中']
    data_one['重要度'] = np.select(conditions, choices, default='低')

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
    fig_3d = px.scatter_3d(
        data_one,
        x='興味度スコア',
        y='関心度' if option == '役職なし' else '役職の値',
        z='distance_to_origin',
        color='重要度',
        hover_data={'興味度スコア': True, '関心度' if option == '役職なし' else '役職の値': True, '重要度': True, 'distance_to_origin': False}
    )
    fig_3d.update_traces(marker=dict(size=5, opacity=0.8))
    fig_3d.update_layout(scene=dict(zaxis=dict(title='重要度')))
    st.plotly_chart(fig_3d, use_container_width=True)



st.write("")
st.write("")

# 显示单选按钮和来场者的重要度统计信息
st.subheader("来場者の重要度を選択してください")
# 计算每个重要度的数量
important_counts = data_one['重要度'].value_counts()  # 具体数量
total_counts = len(data_one)  # 总数
important_percentages = (important_counts / total_counts) * 100  # 百分比形式

# 显示选择框和统计数据
relevance_option = st.radio(
    "",
    ['高', '中', '低'],
    format_func=lambda x: f"{x} ({important_counts.get(x, 0)}/{total_counts} 約 {important_percentages.get(x, 0):.2f}%)" if x in important_counts else x
)



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
       label=':inbox_tray: ダウンロード',
       data=towrite,
       file_name="data.xlsx",
       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )