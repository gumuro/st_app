import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from sklearn.cluster import KMeans

def process_data(file_name):
    # 加载数据
    df = pd.read_excel(file_name)

    # 计算每个 AiTag ID 的訪問回数
    df['訪問回数'] = df.groupby('AiTag ID')['AiTag ID'].transform('count')
    # 确保関心度列是整数，如果不是数字则设为0
    df['関心度'] = df['関心度'].apply(lambda x: int(x) if str(x).isdigit() else 0)

    return df

# 加载数据
data_one = process_data('alldata.xlsx')

# 计算興味度スコア
data_one['興味度スコア'] = (0.5 * data_one['ダウンロード回数']) + (0.3 * data_one['メール転送回数']) + (0.2 * data_one['訪問回数'])
data_one['distance_to_origin'] = np.sqrt(data_one['興味度スコア']**2 + data_one['関心度']**2)


# 按出展社名分组，计算总数
grouped_data = data_one.groupby('出展社名').agg({
    'メール転送回数': 'sum',
    'ダウンロード回数': 'sum',
    '関心度': 'sum',
    '興味度スコア': 'sum'
})

# 计算 distance_to_origin
grouped_data['distance_to_origin'] = np.sqrt(grouped_data['興味度スコア']**2 + grouped_data['関心度']**2)

# 重新应用 KMeans 分群
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(grouped_data[['興味度スコア', '関心度', 'distance_to_origin']])
grouped_data['クラスタ'] = clusters

# 映射高中低
cluster_centers = kmeans.cluster_centers_
distance_to_origin_means = np.linalg.norm(cluster_centers, axis=1)
sorted_clusters = np.argsort(distance_to_origin_means)
cluster_map = {sorted_clusters[0]: '低', sorted_clusters[1]: '中', sorted_clusters[2]: '高'}
grouped_data['人気度'] = grouped_data['クラスタ'].map(cluster_map)

# 根据关心度调整重要度
grouped_data['人気度'] = np.where(grouped_data['関心度'] >= 5, '高',
                                  np.where(grouped_data['関心度'].between(3, 4), '中', '低'))

popularity_color_map = {
    '高': 'red',   # High popularity
    '中': 'blue',  # Medium popularity
    '低': 'green'  # Low popularity
}

# ...[之前的代码不变]...

# 创建交互式3D散点图
fig = go.Figure()

# 添加实际数据点（现在使用 grouped_data）
for _, row in grouped_data.iterrows():
    fig.add_trace(go.Scatter3d(
        x=[row['興味度スコア']],
        y=[row['関心度']],
        z=[row['distance_to_origin']],
        mode='markers',
        marker=dict(
            size=5,
            color=popularity_color_map[row['人気度']],  # Use the mapped color
            opacity=0.8
        ),
        hovertext=f'出展社名: {row.name}, 関心度: {row["関心度"]}, 興味度スコア: {row["興味度スコア"]}',
        name=row.name
    ))

# 特别标记 NTT Com DD株式会社（如果存在于数据中）
if 'NTT Com DD株式会社' in grouped_data.index:
    ntt_data = grouped_data.loc['NTT Com DD株式会社']
    fig.add_trace(go.Scatter3d(
        x=[ntt_data['興味度スコア']],
        y=[ntt_data['関心度']],
        z=[ntt_data['distance_to_origin']],
        mode='markers',
        marker=dict(
            size=10,
            color='yellow',  # Specific color for NTT Com DD株式会社
            opacity=0.9
        ),
        hovertext=f'出展社名: NTT Com DD株式会社, 関心度: {ntt_data["関心度"]}, 興味度スコア: {ntt_data["興味度スコア"]}',
        name='NTT Com DD株式会社'
    ))

# 特别标记 NTT Com DD株式会社
ntt_data = data_one[data_one['出展社名'] == 'NTT Com DD株式会社']
# 计算聚合值（例如，平均值）
ntt_avg = ntt_data[['興味度スコア', '関心度', 'distance_to_origin']].mean()
fig.add_trace(go.Scatter3d(
    x=[ntt_avg['興味度スコア']],
    y=[ntt_avg['関心度']],
    z=[ntt_avg['distance_to_origin']],
    mode='markers',
    marker=dict(
        size=10,
        color='yellow',
        opacity=0.9
    ),
    hovertext=f'出展社名: NTT Com DD株式会社, 関心度: {ntt_avg["関心度"]}, 興味度スコア: {ntt_avg["興味度スコア"]}',
    name='NTT Com DD株式会社'
))


# 用于显示图例的透明点
for label, color in [("高", "red"), ("中", "blue"), ("低", "green")]:
    fig.add_trace(go.Scatter3d(
        x=[None], y=[None], z=[None],
        mode='markers',
        marker=dict(size=10, color=color),
        name=label
    ))

fig.update_layout(scene=dict(
    xaxis_title='興味度スコア',
    yaxis_title='関心度',
    zaxis_title='人気度'
))

st.plotly_chart(fig)