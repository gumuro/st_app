import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px
import numpy as np


def load_data():
    data = pd.read_excel('株式会社テクサー_ok_updated.xlsx')
    
    
    data['興味度スコア'] = (0.5 * data['ダウンロード回数']) + (0.3 * data['メール転送回数']) + (0.2 * data['訪問回数'])

    
    data['来場者コード_1'] = data['来場者コード']
    data['来場者コード_1'] = data['来場者コード_1'].str.strip('B')

    return data





def preprocess_data(data):
    filtered_df = data[~data['来場者コード_1'].isin([pd.NA, '-'])]
    filtered_df = filtered_df[filtered_df['来場者コード_1'] != 1170066]
    filtered_df = filtered_df.groupby('来場者コード_1').agg({
        '興味度スコア': 'max',
        'Job Title Num': 'max'
    }).reset_index()
    filtered_df.fillna(filtered_df.mean(), inplace=True)
    return filtered_df

def run_clustering(filtered_df):
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(filtered_df[['興味度スコア', 'Job Title Num']])
    n_clusters = 3
    kmeans = KMeans(n_clusters=n_clusters)
    filtered_df['cluster'] = kmeans.fit_predict(scaled_features)
    cluster_means = filtered_df.groupby('cluster')['興味度スコア'].mean()
    sorted_clusters = cluster_means.sort_values().index
    cluster_mapping = {old_cluster: new_cluster for new_cluster, old_cluster in enumerate(sorted_clusters)}
    filtered_df['cluster'] = filtered_df['cluster'].map(cluster_mapping)
    return filtered_df

def main():
    
    
    data = load_data()
    filtered_df = preprocess_data(data)
    filtered_df = run_clustering(filtered_df)
    
    # 更新颜色字典
    color_dict = {0: '#FF5733', 1: '#33FF57', 2: '#3357FF'}  # 您可以根据偏好修改颜色值
    
    selected_columns_1 = data[['来場者コード_1', '氏名', '会社名', '役職名', '国籍', '都道府県', 'E-mail']].drop_duplicates(subset=['来場者コード_1'])
    sorted_visitor_counts = filtered_df.merge(selected_columns_1, on='来場者コード_1', how='left')
    
    sorted_visitor_counts['氏名_会社名'] = sorted_visitor_counts['氏名'] + '<br>' + sorted_visitor_counts['会社名']
    
    fig = px.scatter(sorted_visitor_counts, 
                     x='興味度スコア', 
                     y='Job Title Num', 
                     color='cluster',
                     color_discrete_map=color_dict, 
                     hover_name='氏名_会社名',
                     title='株式会社テクサーの来場者の重要度',
                     labels={'興味度スコア': '興味度スコア', 'Job Title Num': 'Job Title Num'},
                     height=600,
                     width=900)
    
    fig.update_traces(marker=dict(size=10, opacity=0.7, line=dict(width=0.5, color='white')))
    fig.update_layout(legend_title_text='Cluster')
    
    st.plotly_chart(fig)

    # ... [rest of your code]


    # 排除 cluster0 的数据，并根据 cluster 降序排列数据
    sorted_by_cluster = sorted_visitor_counts[sorted_visitor_counts['cluster'] != 0]
    sorted_by_cluster = sorted_by_cluster.sort_values(by='cluster', ascending=False)

    # 为滑轮设置最小和最大值
    max_value = len(sorted_by_cluster)
    slider_value = st.slider("表示する顧客数を選択します。", 1, max_value, 5)  # 5 是默认值

    # 修改 E-mail 列为一个超链接
    sorted_by_cluster['E-mail'] = sorted_by_cluster['E-mail'].apply(lambda x: f'<a href="mailto:{x}">{x}</a>' if pd.notnull(x) else x)

    # 使用 st.markdown 显示表格，并设置unsafe_allow_html=True来允许HTML渲染
    st.markdown(sorted_by_cluster[['氏名', '会社名', '役職名', 'E-mail']].head(slider_value).to_html(escape=False, index=False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
