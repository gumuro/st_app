import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("製品について分析")
st.write("")
st.subheader("自社製品と類似度分布")

# 读取数据
# 公共的数据处理函数
def process_data(filename, columns):
    data = pd.read_excel(filename)
    data = data[columns].copy()
    return data

data = process_data('cos_with_describe_end.xlsx')

# 过滤出 Tufinと類似度 不是 0% 的数据
filtered_data_tufin = data[data['Tufinと類似度'] > 0]
# 过滤出 Managedと類似度 不是 0% 的数据
filtered_data_managed = data[data['Managedと類似度'] > 0]

# 为 Tufin 相似度热图准备数据，并按照 Tufinと類似度 降序排序
heatmap_data_tufin = filtered_data_tufin[['出展社名', '製品', 'Tufinと類似度', '人気度']].sort_values(by='Tufinと類似度', ascending=False)
heatmap_data_tufin['Tufinと類似度'] = heatmap_data_tufin['Tufinと類似度']  * 100# 转换为百分比
# 为 Managed 相似度热图准备数据，并按照 Managedと類似度 升序排序
heatmap_data_managed = filtered_data_managed[['出展社名', '製品', 'Managedと類似度', '人気度']].sort_values(by='Managedと類似度', ascending=False)
heatmap_data_managed['Managedと類似度'] = heatmap_data_managed['Managedと類似度'] * 100# 转换为百分比

# 创建 Tufin 相似度热图
fig_tufin = px.imshow(
    heatmap_data_tufin[['Tufinと類似度']].values.reshape(-1, 1),
    labels=dict(color="Tufinと類似度 (%)"),
    y=heatmap_data_tufin['製品'] + " 「" + heatmap_data_tufin['人気度'].astype(str) + ", " + heatmap_data_tufin['出展社名'] + "」",
    text_auto=True
)

# 创建 Managed 相似度热图
fig_managed = px.imshow(
    heatmap_data_managed[['Managedと類似度']].values.reshape(-1, 1),
    labels=dict(color="Managedと類似度 (%)"),
    y=heatmap_data_managed['製品'] + " 「" + heatmap_data_managed['人気度'].astype(str) + ", " + heatmap_data_managed['出展社名'] + "」",
    text_auto=True
)

# 更新布局以改善显示效果
for fig in [fig_tufin, fig_managed]:
    fig.update_layout(
        xaxis={'side': 'top', 'showticklabels': False},
        yaxis={'side': 'left'},
        margin=dict(l=100, r=100, t=100, b=100),
        autosize=False,
        height=600,  # 图表高度
        width=600    # 图表宽度
    )

# 使用 Streamlit 的 columns 创建两个并排列
col1, col2 = st.columns(2)

# 在左侧列显示 Tufin 相似度热图
with col1:
    st.plotly_chart(fig_tufin)

# 在右侧列显示 Managed 相似度热图
with col2:
    st.plotly_chart(fig_managed)
    
# 新的标题
st.subheader("自社製品の関連性")

# 显示 network.png 图像
st.image("network.png", caption="自社製品の関連性ネットワーク")

# 添加描述文字
st.write("自社製品との相関が高いほどつながりが太くなり、協力できる企業を見つけたり、今回展示した製品の市場分野を分布したりするのに役立ちます。")

