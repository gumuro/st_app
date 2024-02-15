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
def process_data(filename, columns):
    data_one = pd.read_excel(filename)
    data = data_one[columns].copy()
    data['関心度'] = data['関心度'].apply(lambda x: int(x) if x.isdigit() else 0)
    data['訪問回数'] = data.groupby('AiTag ID')['AiTag ID'].transform('count')
    data['スキャン/AiBoxタッチ日時'] = pd.to_datetime(data['スキャン/AiBoxタッチ日時'], errors='coerce')
    # 移除含有NaT的行
    data = data.dropna(subset=['スキャン/AiBoxタッチ日時'])
    data['date'] = data['スキャン/AiBoxタッチ日時'].dt.date
    data['hour'] = data['スキャン/AiBoxタッチ日時'].dt.hour
    return data
data = process_data('NTT Com DD株式会社.xlsx', ['出展社名', '製品','AiTag ID', '関心度','スキャン/AiBoxタッチ日時', 'ダウンロード回数', 'メール転送回数'])


# 计算汇总数据
visitors_per_product = data.groupby('製品')['AiTag ID'].count().reset_index()
total_visitors = visitors_per_product['AiTag ID'].sum()
visit_count_per_product = data.groupby('製品')['訪問回数'].sum().reset_index()
download_count_per_product = data.groupby('製品')['ダウンロード回数'].sum().reset_index()
email_forward_count_per_product = data.groupby('製品')['メール転送回数'].sum().reset_index()

# 读取alldata.xlsx文件
alldata = process_data('alldata.xlsx',['出展社名', '製品','AiTag ID', '関心度','スキャン/AiBoxタッチ日時', 'ダウンロード回数', 'メール転送回数'])

# 计算总来访者数量
total_visitors = alldata['AiTag ID'].nunique()

# 计算NTT Com DD株式会社的来访者数量
ntt_com_visitors = alldata[alldata['出展社名'] == 'NTT Com DD株式会社']['AiTag ID'].nunique()

    
# 修改后的绘制圆形图的函数，调整图例位置
def plot_visitor_circles(total, ntt_com):
    # 大圆半径
    radius_large = 3  # 可以根据需要调整这个值
    # 小圆半径，根据比例计算
    radius_small = radius_large * (ntt_com / total) ** 0.5

    # 创建图形和坐标轴
    fig, ax = plt.subplots()
    # 绘制大圆
    large_circle = plt.Circle((0, 0), radius_large, color='blue', alpha=0.5, label=f'Total Visitors: {total}')
    ax.add_artist(large_circle)
    # 绘制小圆
    small_circle = plt.Circle((0, -radius_large + radius_small), radius_small, color='red', alpha=0.5, label=f'NTT Com Visitors: {ntt_com}')
    ax.add_artist(small_circle)

    # 设置坐标轴范围，确保图形居中显示
    ax.set_xlim(-radius_large, radius_large)
    ax.set_ylim(-radius_large, radius_large)
    ax.set_aspect('equal', adjustable='box')  # 保持等比例

    # 隐藏坐标轴
    ax.axis('off')

    # 添加图例，位置在右上角
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # 使用Streamlit的pyplot方法显示图形
    st.pyplot(fig)

    
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
st.markdown("<h4>当社の来場者人数と来場者総数</h4>", unsafe_allow_html=True)
# 新增的部分


# 在Streamlit应用中调用函数绘制并显示图形
plot_visitor_circles(total_visitors, ntt_com_visitors)


st.header("")
st.header("")
# 来场者时间分布图
# 使用实际的文件名和列名调用process_data函数



# 使用单选按钮选择要显示的图表类型
st.markdown("<h4>来場者人数の時間分布</h4>", unsafe_allow_html=True)
chart_option = st.radio(
    "",
    ('当社来場者人数と来場者総数の時系列', '日別来場者人数の時系列')
)

# 根据所选的单选按钮显示不同的图表
if chart_option == '当社来場者人数と来場者総数の時系列':
    # 调用绘制堆叠区域图的函数
    # 显示 network.png 图像
    st.image("614.png", caption="  ")
    st.image("615.png", caption="  ")
    st.image("616.png", caption="  ")
    
elif chart_option == '日別来場者人数の時系列':
    # 来场者时间分布图
    st.markdown("<h4>来場者人数の時間分布</h4>", unsafe_allow_html=True)
    unique_dates = data['date'].unique()
    unique_dates.sort()
    for product in visitors_per_product['製品']:
        product_data = data[data['製品'] == product]
        plt = plot_hourly_visitor_distribution(product_data, product, unique_dates)
        st.pyplot(plt)
        



st.header("")
st.header("")
st.markdown("<h4>製品ごとのダウンロード数</h4>", unsafe_allow_html=True)  # 设置字体大小为 h4，标题为日语
fig, ax = plot_horizontal_bar_chart(download_count_per_product.set_index('製品')['ダウンロード回数'], 
                                    "製品ごとのダウンロード数", "ダウンロード数", "製品")
st.pyplot(fig)


st.header("")
st.header("")
st.markdown("<h4>製品ごとのメール転送数</h4>", unsafe_allow_html=True)  # 设置字体大小为 h4，标题为日语
fig, ax = plot_horizontal_bar_chart(email_forward_count_per_product.set_index('製品')['メール転送回数'], 
                                    "製品ごとのメール転送数", "メール転送数", "製品")
st.pyplot(fig)


st.header("")
# 使用st.markdown设置不同字体大小
st.markdown("<h4>来場者の関心度</h4>", unsafe_allow_html=True)  # 设置字体大小为 h4，标题为日语

# 为每个产品绘制关心度分布图
unique_products = data['製品'].unique()

# 设置子图布局，每行显示两个饼图
cols = st.columns(2)
for index, product in enumerate(unique_products):
    # 筛选特定产品的数据
    product_data = data[data['製品'] == product]
    # 计算该产品的关心度分布
    interest_level_counts = product_data['関心度'].value_counts()

    # 创建一个固定大小的饼图
    fig, ax = plt.subplots(figsize=(4, 4))  # 这里可以调整饼图的大小
    ax.pie(interest_level_counts, labels=interest_level_counts.index, autopct='%1.1f%%', startangle=20)
    ax.set_title(product)

    # 保持宽高比例一致
    ax.set_aspect('equal')

    # 在Streamlit的布局中显示饼图
    with cols[index % 2]:
        st.pyplot(fig)

