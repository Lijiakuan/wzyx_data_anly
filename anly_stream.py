# 使用auto-py-to-exe进行打包 mysql-client
# Auther:Lijiakuan
# version: 1.0
import pandas as pd
import numpy as np
import sys
import streamlit as st
import os

# df = pd.read_excel('血压数据2023_06_30.xlsx', header=0)
# print(df.head())
# df = df.head(1000)

# 读取上传文件


def read_file(filename):
    df = pd.read_excel(filename, header=0)
    return df

# 完成周平均血压的测量


def avg_bloodany(filepath, num):
    df = read_file(filepath)
    # df = df.head(3000)
    df['测量日期'] = pd.to_datetime(df['测量日期'])
    # 分组统计
    df['week'] = (df['测量日期'].dt.strftime(
        '%d').astype(int) - 1) // 7 + 1  # 增加周字段

    df['month'] = df['测量日期'].dt.strftime('%Y%m')  # 增加月字段
    df['是否绑定血压计'] = np.where(df['血压计序列号'].isin(
        ['None', 'NaN', '']) == False, '是', '否')
    # df['患者身份证'] = df['患者身份证'].astype(str).apply(
    #     lambda x: x[:6] + '*'*4 + x[10:])
    # df['患者手机号'] = df['患者手机号'].astype(str).apply(
    #     lambda x: x[:3] + '*'*4 + x[7:])

    df2 = df[['医院', '医生姓名', '医生手机号', '患者编码', '患者身份证', '患者姓名',
              '患者手机号', '年龄', '性别', '医生姓名', '上线日期', '血压计序列号', '是否绑定血压计', 'month']]

    df2 = df2.drop_duplicates()
    weekly = df.groupby(['医院', 'week', '患者编码']).agg({
        '收缩压': ['mean'],
        '舒张压': ['mean'],
        '心率': ['mean'],
        '测量日期': 'count'
    }).reset_index()

    weekly = weekly.pivot(index=['医院', '患者编码'],
                          columns='week',
                          values=['收缩压', '舒张压', '心率', '测量日期'])
    # print(weekly.head())
    # sys.exit()

    monthly = df.groupby(['医院', 'month', '患者编码']).agg({
        '收缩压': ['mean'],
        '舒张压': ['mean'],
        '心率': ['mean'],
        '测量日期': 'count'
    }).reset_index()
    # monthly = monthly.rename(columns={
    #     '收缩压': '月平均收缩压',
    #     '舒张压': '月平均舒张压',
    #     '心率': '月平均心率',
    #     '测量日期': '月有效测量数'
    # })

    # 合并统计结果到原表

    result = df2.merge(weekly, how='left', on=['医院', '患者编码']) \
        .merge(monthly, how='left', on=['医院', 'month', '患者编码'])

    # result.fillna(0)
    # print(type(result))
    num = int(num) + 1  # 用变量替换
    a = ([[f'第{i}周_平均收缩压',]
         for i in range(1, num)])
    c = ([[f'第{i}周_平均舒张压', ]
         for i in range(1, num)])
    d = ([[f'第{i}周_平均心率',]
          for i in range(1, num)])
    e = ([[f'第{i}周_有效测量次数',]
         for i in range(1, num)])
    f = a + c + d + e
    new_cols = ['项目中心名称', '医生姓名', '医生手机号', '患者id', '身份证号', '就诊人姓名', '手机号', '年龄', '性别', '随访医生',
                '注册上线时间', '血压计编号', '是否绑定血压计', '统计测量年月', '月平均收缩压', '月平均舒张压', '月平均心率', '月有效测量次数']
    for i in f:
        for j in i:
            new_cols.insert(-4, j)

    # new_cols = ['项目中心名称', '医生姓名', '医生手机号', '患者id', '身份证号', '就诊人姓名', '手机号', '年龄', '性别', '随访医生',
    #             '注册上线时间', '血压计编号', '是否绑定血压计', '统计测量年月', '第一周_平均收缩压', '第二周_平均收缩压', '第三周_平均收缩压', '第四周_平均收缩压', '第五周_平均收缩压',
    #             '第一周_平均舒张压', '第二周_平均舒张压', '第三周_平均舒张压', '第四周_平均舒张压', '第五周_平均舒张压', '第一周_平均心率', '第二周_平均心率', '第三周_平均心率', '第四周_平均心率', '第五周_平均心率',
    #             '第一周_有效测量次数', '第二周_有效测量次数', '第三周_有效测量次数', '第四周_有效测量次数', '第五周_有效测量次数', '月平均收缩压', '月平均舒张压', '月平均心率', '月有效测量次数']
    # df = result.reindex(columns=new_cols)
    result.columns = new_cols
    for i in range(1, num):
        # conditions = [
        #     result[f'第{i}周_有效测量次数'].notnull(),
        #     result[f'第{i}周_有效测量次数'].isnull()
        # ]

        # choices = [
        #     np.where(
        #         result[f'第{i}周_平均收缩压'].all() < 140 and
        #         result[f'第{i}周_平均舒张压'].all() < 90,
        #         '达标', '不达标'
        #     ),
        #     '未测量'
        # ]

        # result[f'第{i}周_血压是否达标'] = np.select(conditions, choices)

        conditions = [
            (result[f'第{i}周_有效测量次数'].notnull()) &
            (result[f'第{i}周_平均收缩压'] < 140) & (result[f'第{i}周_平均舒张压'] < 90),
            (result[f'第{i}周_有效测量次数'].isnull())
        ]
        choices = ['达标', '未测量']

        result[f'第{i}周_血压是否达标'] = np.select(conditions, choices, default='不达标')

    # result['月血压是否达标'] = np.where(
    #     result['月平均收缩压'].any() < 140 and result['月平均舒张压'].all() < 90,
    #     '达标',
    #     '不达标'
    # )
    result['月血压是否达标'] = np.nan

    # 根据条件填入值
    result.loc[(result['月平均收缩压'] < 140) & (
        result['月平均舒张压'] < 90), '月血压是否达标'] = '达标'
    result.loc[(result['月平均收缩压'] >= 140) | (
        result['月平均舒张压'] >= 90), '月血压是否达标'] = '不达标'

    # 输出结果
    # 项目中心名称	患者id	身份证号	就诊人姓名	手机号	年龄	性别	随访医生	注册上线时间  血压计编号	是否绑定血压计	统计测量年月
    # 第一周_平均收缩压	第二周_平均收缩压	第三周_平均收缩压	第四周_平均收缩压	第五周_平均收缩压	第一周_平均舒张压	第二周_平均舒张压	第三周_平均舒张压
    # 第四周_平均舒张压	第五周_平均舒张压	第一周_平均心率	第二周_平均心率	第三周_平均心率	第四周_平均心率	第五周_平均心率	第一周_有效测量次数	第二周_有效测量次数
    # 第三周_有效测量次数	第四周_有效测量次数	第五周_有效测量次数	月平均收缩压	月平均舒张压	月平均心率	月有效测量次数	序号	第一周_血压是否达标	第二周_血压是否达标
    # 第三周_血压是否达标	第四周_血压是否达标	第五周_血压是否达标  月血压是否达标
    new_cols1 = ['项目中心名称', '医生姓名', '医生手机号', '就诊人姓名', '年龄', '性别', '身份证号', '手机号', '血压计编号', '是否绑定血压计', '注册上线时间', '统计测量年月',
                 '月有效测量次数', '月平均收缩压', '月平均舒张压', '月平均心率', '月血压是否达标']

    b = ([[f'第{i}周_有效测量次数', f'第{i}周_平均收缩压', f'第{i}周_平均舒张压',
         f'第{i}周_平均心率', f'第{i}周_血压是否达标'] for i in range(1, num)])
    for m in b:
        for n in m:
            new_cols1.insert(-5, n)

    # result = result[['项目中心名称', '医生姓名', '医生手机号', '就诊人姓名', '年龄', '性别', '身份证号', '手机号', '血压计编号', '是否绑定血压计', '注册上线时间', '统计测量年月',
    #                 '第一周_有效测量次数', '第一周_平均收缩压', '第一周_平均舒张压', '第一周_平均心率', '第一周_血压是否达标',
    #                  '第二周_有效测量次数', '第二周_平均收缩压', '第二周_平均舒张压', '第二周_平均心率', '第二周_血压是否达标',
    #                  '第三周_有效测量次数', '第三周_平均收缩压', '第三周_平均舒张压', '第三周_平均心率', '第三周_血压是否达标',
    #                  '第四周_有效测量次数', '第四周_平均收缩压', '第四周_平均舒张压', '第四周_平均心率', '第四周_血压是否达标',
    #                  '第五周_有效测量次数', '第五周_平均收缩压', '第五周_平均舒张压', '第五周_平均心率', '第五周_血压是否达标',
    #                  '月有效测量次数', '月平均收缩压', '月平均舒张压', '月平均心率', '月血压是否达标']]
    result = result[new_cols1]
    result = result.sort_values(by=['项目中心名称', '就诊人姓名'])
    col_names = result.columns
    result['序号'] = np.array(range(1, len(result)+1))
    result = result.fillna(0)
    for i in range(1, num):
        result[f'第{i}周_平均收缩压'] = np.ceil(result[f'第{i}周_平均收缩压']).astype(int)
        result[f'第{i}周_平均舒张压'] = np.ceil(result[f'第{i}周_平均舒张压']).astype(int)
        result[f'第{i}周_平均心率'] = np.ceil(result[f'第{i}周_平均心率']).astype(int)
    result['月平均收缩压'] = np.ceil(result['月平均收缩压']).astype(int)
    result['月平均舒张压'] = np.ceil(result['月平均舒张压']).astype(int)
    result['月平均心率'] = np.ceil(result['月平均心率']).astype(int)
    result = result[['序号'] + list(col_names)]

    return result


# result = avg_bloodany('hospital_血压数据2023_06_20_00_00.xlsx')
# result.to_excel('就诊人平均血压111.xlsx', index=False)
# sys.exit()

# 完成原始数据的转换，表1


def prj_original_file(filename):
    df = read_file(filename)
    df.columns = ['患者入组编码', '身份证号', '受试者姓名', '手机号', '出生年月', '年龄', '性别', '医生姓名', '医生手机号', '中心名称',
                  '项目id', '上线日期', '测量日期', '收缩压', '舒张压', '心率', '处理标记', '血压计序列号', '警报级别']
    df = df[['中心名称', '医生姓名', '医生手机号', '受试者姓名', '年龄', '性别', '血压计序列号',
            '上线日期', '患者入组编码', '测量日期', '收缩压', '舒张压', '心率', '警报级别']]

    # df.to_excel('原始数据.xlsx', index=False)
    return df

# 按医院名称导出


def hos_original_file(filename):
    df = read_file(filename)
    df.columns = ['患者入组编码', '身份证号', '受试者姓名', '手机号', '出生年月', '年龄', '性别', '医生姓名', '医生手机号', '中心名称',
                  '上线日期', '测量日期', '收缩压', '舒张压', '心率', '血压计序列号', '警报级别']
    df = df[['中心名称', '医生姓名', '医生手机号', '受试者姓名', '年龄', '性别', '血压计序列号',
            '上线日期', '患者入组编码', '测量日期', '收缩压', '舒张压', '心率', '警报级别']]

    # df.to_excel('原始数据.xlsx', index=False)
    return df


# result = hos_original_file('hospital_血压数据2023_06_30_00_00.xlsx')
# result.to_excel('原始数据.xlsx', index=False)
# sys.exit()




# 按照项目生成医生患者的对应关系
# 查询数据库中截止至该月末的医生与患者对应关系

# 生成月平均统计表

# df = Doc_patientinfo('2023-06-30')
# df.to_excel('doc_patient.xlsx', index=False)
# sys.exit()


def avg_monthly(filename, filename1):
    df = hos_original_file(filename)
    df['测量日期'] = pd.to_datetime(df['测量日期'])
    # 分组统计
    # df['month'] = df['测量日期'].dt.strftime('%m')  # 增加月字段
    # df['是否绑定血压计'] = np.where(df['血压计序列号'].isin(
    #     ['None', 'NaN', '']) == False, '是', '否')

    # df2 = Doc_patientinfo('2023-06-30')
    df2 = read_file(filename1)
    # df2['测量日期'] = pd.to_datetime(df['测量日期'])

    df2 = df2.drop_duplicates()

    monthly = df.groupby(['中心名称', '医生姓名', '受试者姓名']).agg({
        '收缩压': ['mean'],
        '舒张压': ['mean'],
        '心率': ['mean'],
        '测量日期': 'count'
    }).reset_index()

    result = df2.merge(monthly, how='left', on=['中心名称', '医生姓名', '受试者姓名'])

    result.columns = ['医生姓名', "医生手机号", '受试者姓名', '性别', '年龄', '血压计序列号', '上线日期',
                      '患者入组编码', '中心名称', '是否绑定血压计', '平均收缩压', '平均舒张压', '平均心率', '测量次数']
    # 新增一列并初始化为NaN
    result['血压状态'] = np.nan

    # 根据多个条件填入值
    conditions = [
        (result['测量次数'].notnull()) &
        (result['平均收缩压'] < 140) & (result['平均舒张压'] < 90),
        (result['测量次数'].isnull())
    ]
    choices = ['正常', '未测量']

    result['警报级别'] = np.select(conditions, choices, default='异常')
    result = result[['中心名称', '医生姓名', "医生手机号", '受试者姓名', '性别', '年龄', '血压计序列号', '上线日期', '患者入组编码',
                    '是否绑定血压计', '测量次数', '平均收缩压', '平均舒张压', '平均心率', '警报级别']].sort_values(by=['医生姓名', '中心名称'])
    result = result.fillna({
        '平均收缩压': 0,
        '平均舒张压': 0,
        '平均心率': 0,
        '测量次数': 0
    })
    result['平均收缩压'] = np.ceil(result['平均收缩压']).astype(int)
    result['平均舒张压'] = np.ceil(result['平均舒张压']).astype(int)
    result['平均心率'] = np.ceil(result['平均心率']).astype(int)

    col_names = result.columns
    result['序号'] = np.array(range(1, len(result)+1))
    result = result[['序号'] + list(col_names)]
    return result


# df = avg_monthly('hospital_血压数据2023_06_30_00_00.xlsx')
# df.to_excel('受试者月平均数据.xlsx', index=False)
# sys.exit()

# 医生名单及数据


def doc_use(filename, filename1):
    df = avg_monthly(filename, filename1)
    df['有测量记录'] = ((df['是否绑定血压计'] == '是') & (df['测量次数'] != 0)).astype(int)
    df['未测量血压人数'] = ((df['是否绑定血压计'] == '是') & (df['测量次数'] == 0)).astype(int)
    df['平均血压正常人数'] = ((df['是否绑定血压计'] == '是') & (
        df['警报级别'] == '正常')).astype(int)
    df['平均血压异常人数'] = ((df['是否绑定血压计'] == '是') & (
        df['警报级别'] == '异常')).astype(int)

    doctor_group = df.groupby(['医生姓名', '中心名称']).agg({
        '是否绑定血压计': lambda x: (x == '是').sum(),
        '有测量记录': 'sum',
        '未测量血压人数': 'sum',
        '平均血压正常人数': 'sum',
        '平均血压异常人数': 'sum'
    }).reset_index()
    doctor_group['测量率'] = np.where(
        doctor_group['是否绑定血压计'] != 0,
        doctor_group['有测量记录'] / doctor_group['是否绑定血压计'],
        np.nan
    )
    try:
        doctor_group['测量率'] = doctor_group['测量率'].apply(
            lambda x: format(x*100, '.0f') + '%')
    except Exception as e:
        pass
    doctor_group['血压达标率'] = np.where(
        doctor_group['是否绑定血压计'] != 0,
        doctor_group['平均血压正常人数'] / doctor_group['是否绑定血压计'],
        np.nan
    )
    try:
        doctor_group['血压达标率'] = doctor_group['血压达标率'].apply(
            lambda x: format(x*100, '.0f') + '%')
    except Exception as e:
        pass
    doctor_group['序号'] = np.array(range(1, len(doctor_group)+1))
    doctor_group.columns = ['医生姓名', '医院', '名下受试者绑定血压计人数', '有测量记录',
                            '未测量血压人数', '平均血压正常人数', '平均血压异常人数', '测量率', '血压达标率', '序号']
    doctor_group = doctor_group[['序号', '医生姓名', '医院', '名下受试者绑定血压计人数',
                                '有测量记录', '未测量血压人数', '测量率', '平均血压正常人数', '平均血压异常人数', '血压达标率']]
    doctor_group = doctor_group.replace(to_replace='nan%', value='')
    return doctor_group


# print(doctor_group)
# doctor_group.to_excel('医生名单数据.xlsx', index=False)
# df = doc_use('hospital_血压数据2023_06_30_00_00.xlsx')
# df.to_excel('医生数据.xlsx', index=False)
# sys.exit()


def hospital_use(filename, filename1):
    df = doc_use(filename, filename1)
    hospital_group = df.groupby(['医院']).agg({
        '名下受试者绑定血压计人数': 'sum',
        '有测量记录': 'sum',
        '未测量血压人数': 'sum',
        '平均血压正常人数': 'sum',
        '平均血压异常人数': 'sum'
    }).reset_index()
    # print(hospital_group)
    hospital_group['测量率'] = np.where(
        hospital_group['名下受试者绑定血压计人数'] != 0,
        hospital_group['有测量记录'] / hospital_group['名下受试者绑定血压计人数'],
        np.nan
    )
    try:
        hospital_group['测量率'] = hospital_group['测量率'].apply(
            lambda x: format(x*100, '.0f') + '%')
    except Exception as e:
        pass
    hospital_group['血压达标率'] = np.where(
        hospital_group['名下受试者绑定血压计人数'] != 0,
        hospital_group['平均血压正常人数'] / hospital_group['名下受试者绑定血压计人数'],
        np.nan
    )
    try:
        hospital_group['血压达标率'] = hospital_group['血压达标率'].apply(
            lambda x: format(x*100, '.0f') + '%')
    except Exception as e:
        pass
    hospital_group['序号'] = np.array(range(1, len(hospital_group)+1))
    hospital_group.columns = ['医院', '绑定血压计入组人数', '有测量记录人数',
                              '未测量血压人数', '平均血压正常人数', '平均血压异常人数', '测量率', '血压达标率', '序号']
    hospital_group = hospital_group[['序号', '医院', '绑定血压计入组人数',
                                     '有测量记录人数', '未测量血压人数', '测量率', '平均血压正常人数', '平均血压异常人数', '血压达标率']]
    hospital_group = hospital_group.replace(to_replace='nan%', value='')
    return hospital_group


# df = hospital_use('hospital_血压数据2023_06_30_00_00.xlsx')
# df.to_excel('医院数据.xlsx', index=False)
# st程序开始
UPLOAD_FOLDER = r"./"
# 读取上传文件


def save_uploaded_file(uploaded_file, path):
    with open(os.path.join(path, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())


def handle_file_upload():
    uploaded_file = st.file_uploader("上传患者血压测量记录", accept_multiple_files=False)
    if uploaded_file is not None:
        save_uploaded_file(uploaded_file, UPLOAD_FOLDER)
        file_detail = {
            "FileName": uploaded_file.name,
            "FileType": uploaded_file.type,
            "FileSize": uploaded_file.size,
            "file_path": os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        }
        st.write("成功上传文件:", file_detail['FileName'])
        return file_detail


def handle_file_upload1():
    uploaded_file1 = st.file_uploader(
        "上传所有患者信息记录", accept_multiple_files=False)
    if uploaded_file1 is not None:
        save_uploaded_file(uploaded_file1, UPLOAD_FOLDER)
        file_detail = {
            "FileName": uploaded_file1.name,
            "FileType": uploaded_file1.type,
            "FileSize": uploaded_file1.size,
            "file_path": os.path.join(UPLOAD_FOLDER, uploaded_file1.name)
        }
        st.write("成功上传文件:", file_detail['FileName'])
        return file_detail


st.set_page_config(
    page_title="万众益心数据分析展示信息系统",
    page_icon='🏢',
    layout="wide",
    menu_items={
        'Get Help': 'https://github.com/Lijiakuan/wzyx_data_anly/issues',
        'About': '关于本系统: **由李家宽制作**'
    })
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
# st.title("万众益心数据统计分析展示")
st.image("b6.png", use_column_width=True)
# 侧边栏
st.sidebar.header("万众益心数据分析展示系统")
mode = st.sidebar.selectbox("数据分析展示", ["数据分析", "图表展示"])
############################################# 第一页 ############################################
if mode == "数据分析":
    st.header("患者血压数据分析")
    file_attsh = handle_file_upload()
    patient_info = handle_file_upload1()
    if file_attsh and patient_info:
        filename = file_attsh['FileName']
        filename1 = patient_info['FileName']
        st.write(filename, filename1)

        st.write("---")
        # 附件5 5周血压记录
        if st.checkbox("下载就诊人血压周_月平均血压记录"):
            st.warning("按照数据导出的天数计算周次，每月1号为第一周第一天，如6.23日，即属于是第4周,下面选择4,不可选择为空！！！")
            num = st.selectbox("共多少周数据", [1, 2, 3, 4, 5, None], 5)
            # print(num)
            if num is not None:
                df = avg_bloodany(filename, num)
                df.to_excel('就诊人平均血压.xlsx', index=False)
                st.success("就诊人周_月平均血压表已生成，请点击下载按钮进行下载！")
                expfilpth = '就诊人平均血压.xlsx'
                exfilname = '就诊人平均血压.xlsx'
                exp_btn1 = st.download_button(
                    label="周_月平均血压记录下载",
                    data=open(expfilpth, "rb"),
                    file_name=exfilname,
                )
                if st.button("预览前30行"):
                    st.write(df.head(30))
            # result.to_excel('就诊人平均血压.xlsx', index=False)
        # 附件1  生成规范化的原始表
        if st.checkbox("月原始血压记录"):
            df = hos_original_file(filename)
            df.to_excel('原始数据.xlsx', index=False)
            st.success("原始数据表已生成，请点击下载按钮进行下载！")
            expfilpth = '原始数据.xlsx'
            exfilname = '原始数据.xlsx'
            exp_btn2 = st.download_button(
                label="下载原始血压记录下载",
                data=open(expfilpth, "rb"),
                file_name=exfilname,
            )
            if st.button("预览前30行"):
                st.write(df.head(30))
        # 附件2 生成所有受试者名单及月平均记录，方便管理者查看测量情况
        if st.checkbox("所有受试者名单及月平均血压记录"):
            df = avg_monthly(filename, filename1)
            df.to_excel('受试者名单及月平均血压记录.xlsx', index=False)
            st.success("受试者名单及月血压记录表已生成，请点击下载按钮进行下载！")
            expfilpth = '受试者名单及月平均血压记录.xlsx'
            exfilname = '受试者名单及月平均血压记录.xlsx'
            exp_btn3 = st.download_button(
                label="受试者名单及月平均血压记录下载",
                data=open(expfilpth, "rb"),
                file_name=exfilname,
            )
            if st.button("预览前30行"):
                st.write(df.head(30))
        # 附件3 生成医生用的名单数据 ，统计评估医生的患者测量率和达标率
        if st.checkbox("医生名单及其名下患者的测量率和控制情况表"):
            df = doc_use(filename, filename1)
            df.to_excel('医生名单及数据.xlsx', index=False)
            st.success("医生名单及数据表已生成，请点击下载按钮进行下载！")
            expfilpth = '医生名单及数据.xlsx'
            exfilname = '医生名单及数据.xlsx'
            exp_btn4 = st.download_button(
                label="医生名单及数据下载",
                data=open(expfilpth, "rb"),
                file_name=exfilname,
            )
            if st.button("预览"):
                st.write(df)
        # 附件4 生成医院用的名单数据 ，统计评估医院的患者测量率和达标率
        if st.checkbox("各医院患者的测量率和控制情况表"):
            df = hospital_use(filename, filename1)
            df.to_excel('各医院数据.xlsx', index=False)
            st.success("各医院数据表已生成，请点击下载按钮进行下载！")
            expfilpth = '各医院数据.xlsx'
            exfilname = '各医院数据.xlsx'
            exp_btn4 = st.download_button(
                label="各医院数据下载",
                data=open(expfilpth, "rb"),
                file_name=exfilname,
            )
            if st.button("预览"):
                st.write(df)
    else:
        st.warning("请同时上传两个所需文件，第一个附件为桌面软件导出的血压测量记录，第二个附件为桌面软件导出导出的所有患者信息记录！！！")
