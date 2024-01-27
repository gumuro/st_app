import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.family'] = 'meiryo'

# 定义绘制时间分布图的函数
def plot_hourly_visitor_distribution(product_data, product_name, unique_dates):
    plt.figure(figsize=(12, 6))
    colors = ['blue', 'green', 'red']  # 三天的颜色
    for i, date in enumerate(unique_dates):
        daily_data = product_data[product_data['date'] == date]
        hourly_count = daily_data.groupby('hour').count()['製品']
        hourly_count = hourly_count[hourly_count.index.isin(range(9, 20))]
        plt.plot(hourly_count, label=f'Date: {date}', color=colors[i], marker='o')
        # 添加数据点标签
        for x, y in hourly_count.items():
            plt.text(x, y, str(y), color=colors[i], fontsize=8)
    plt.title(f'Hourly Visitor Count Distribution for "{product_name}" (9AM-7PM)')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Visitors')
    plt.xticks(range(9, 20))
    plt.legend()
    plt.grid(True)
    return plt

# 加载数据
@st.cache_data
def load_data():
    data = pd.read_excel('NTT Com DD株式会社.xlsx')
    data['スキャン/AiBoxタッチ日時'] = pd.to_datetime(data['スキャン/AiBoxタッチ日時'], errors='coerce')
    # 移除含有NaT的行
    data = data.dropna(subset=['スキャン/AiBoxタッチ日時'])
    data['date'] = data['スキャン/AiBoxタッチ日時'].dt.date
    data['hour'] = data['スキャン/AiBoxタッチ日時'].dt.hour
    return data
data = load_data()

# 计算汇总数据
visitors_per_product = data.groupby('製品')['AiTag ID'].count().reset_index()
total_visitors = visitors_per_product['AiTag ID'].sum()
#visit_count_per_product = data.groupby('製品')['訪問回数'].sum().reset_index()
download_count_per_product = data.groupby('製品')['ダウンロード回数'].sum().reset_index()
email_forward_count_per_product = data.groupby('製品')['メール転送回数'].sum().reset_index()


# 新增的绘图函数
def plot_horizontal_bar_chart(data, title, x_label, y_label, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = plt.gcf()
    
    data.plot(kind='barh', ax=ax)
    ax.set_title(title, fontsize=24)  # 设置标题字体大小为 24
    ax.set_xlabel(x_label, fontsize=20)  # 设置X轴标签字体大小为 20
    ax.set_ylabel(y_label, fontsize=20)  # 设置Y轴标签字体大小为 20
    
    # 在条形旁边添加数值标签
    for i in ax.patches:
        ax.text(i.get_width() + 0.2, i.get_y() + 0.1, str(round(i.get_width(), 2)), fontsize=10)  # 设置数值字体大小为 16
    
    return fig, ax




# 设置页面布局
st.title("NTT Com DD株式会社 基本情報")



# 显示总来场者人数

st.header("")
st.header("")
st.markdown("<h4>来場者の総数</h4>", unsafe_allow_html=True)
st.write(f"来場者の総数：{total_visitors}")

st.header("")
# 使用st.markdown设置不同字体大小
st.markdown("<h4>製品ごとの来場者人数</h4>", unsafe_allow_html=True)  # 设置字体大小为 h4，标题为日语
view_data = data.groupby('製品').size()
fig, ax = plot_horizontal_bar_chart(view_data, "製品ごとの閲覧数", "閲覧数", "製品")
st.pyplot(fig)

st.table(visitors_per_product)


st.header("")
# 来场者时间分布图
st.markdown("<h4>来場者人数の時間分布</h4>", unsafe_allow_html=True)
unique_dates = data['date'].unique()
unique_dates.sort()
for product in visitors_per_product['製品']:
    product_data = data[data['製品'] == product]
    plt = plot_hourly_visitor_distribution(product_data, product, unique_dates)
    st.pyplot(plt)



st.header("")
st.markdown("<h4>製品ごとの訪問回数</h4>", unsafe_allow_html=True)  # 设置字体大小为 h4，标题为日语
fig, ax = plot_horizontal_bar_chart(visit_count_per_product.set_index('製品')['訪問回数'], 
                                    "製品ごとの訪問回数", "訪問回数", "製品")

st.pyplot(fig)
st.table(download_count_per_product)


st.header("")
st.markdown("<h4>製品ごとのダウンロード数</h4>", unsafe_allow_html=True)  # 设置字体大小为 h4，标题为日语
fig, ax = plot_horizontal_bar_chart(download_count_per_product.set_index('製品')['ダウンロード回数'], 
                                    "製品ごとのダウンロード数", "ダウンロード数", "製品")
st.pyplot(fig)
st.table(download_count_per_product)


st.header("")
st.markdown("<h4>製品ごとのメール転送数</h4>", unsafe_allow_html=True)  # 设置字体大小为 h4，标题为日语
fig, ax = plot_horizontal_bar_chart(email_forward_count_per_product.set_index('製品')['メール転送回数'], 
                                    "製品ごとのメール転送数", "メール転送数", "製品")
st.pyplot(fig)
st.table(email_forward_count_per_product)

st.header("")
# 使用st.markdown设置不同字体大小
st.markdown("<h4>来場者の関心度</h4>", unsafe_allow_html=True)  # 设置字体大小为 h4，标题为日语

# 来场者的关心度分布
interest_level_counts = data['関心度'].value_counts()
fig, ax = plt.subplots(figsize=(4, 4))
ax.pie(interest_level_counts, labels=interest_level_counts.index, autopct='%1.1f%%', startangle=10)

st.pyplot(fig)

