from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
import gspread
import random
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from datetime import datetime
import time
import pandas as pd
import copy
from PIL import Image
import numpy as np

# Google Driveの認証設定
scopes = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

json_keyfile_dict = st.secrets["service_account"]

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    json_keyfile_dict, 
    scopes
)

gauth = GoogleAuth()
gauth.credentials = credentials
drive = GoogleDrive(gauth)

st.session_state.query_params = st.query_params
st.session_state.file_name = st.session_state.query_params.get("user_id")
 #st.session_state.file_name = "test"

st.session_state.custom_css = """
    <style>
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Rerunボタンだけを表示 */
    #MainMenu {visibility: visible;}
    </style>
    """

# 初期状態を設定
if "page" not in st.session_state:
    st.session_state.page = "home"
    #st.session_state.page = "t1p1"
    #st.session_state.page = "task1"

# ボタンを押すと状態を変更し再レンダリング
def go_to_page(page_name):
    st.session_state.page = page_name
    time.sleep(0.5)
    st.rerun()

# ページごとのコンテンツを表示
if st.session_state.page == "home":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "agreement" not in st.session_state:
        st.session_state.agreement = False
        st.session_state.agreement_check = False
        st.session_state.form_submitted = 0

    st.markdown('# ユーザアンケート トップページ')

    #st.markdown("<hr>", unsafe_allow_html=True)
    #st.warning("2025年1月28日に行った「【研究アンケート調査】AIのヒントを参考にして問題を解く」に参加された方は、申し訳ありませんがお断りさせていただきます。")
    #st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('この度は、調査にご協力いただき誠にありがとうございます。 <br> 以下の指示に従って、順番にタスクを行ってください。', unsafe_allow_html=True)

    st.markdown('1. 以下の同意書をお読みになり、必要事項を記入して提出ボタンを押してください。', unsafe_allow_html=True)

    form = st.form(key="research_form")

    with form:
        st.markdown("## 研究へのご協力のお願い", unsafe_allow_html=True)

        st.markdown(""" この文書は、あなたにご協力いただきたい研究の内容について説明したものです。この文書をよく読み、この研究に参加いただけるかどうかを検討してください。<br>
                    もし、お分かりになりにくいことがありましたら、遠慮なく連絡先までお問い合わせください。<br>""", unsafe_allow_html=True)
        
        st.markdown("#### 1. この研究の概要 ", unsafe_allow_html=True)

        st.markdown("###### 研究課題", unsafe_allow_html=True)

        st.markdown("""「人間の仮説に対してフィードバックを与える機械学習モデルが意思決定へ与える影響の調査」<br>
                    研究責任者氏名・所属・職名 <br> ・馬場 雪乃（東京大学大学院総合文化研究科・広域科学専攻・准教授）<br>
                    研究実施者氏名・所属・職名 <br> ・土屋 祐太（東京大学大学院総合文化研究科・広域科学専攻・博士課程学生）<br> """, unsafe_allow_html=True)

        st.markdown("###### 研究の目的・意義", unsafe_allow_html=True)

        st.markdown("""本研究の目的は、人間がAIと協力して意思決定を行う際に、AIから提示される情報が、
                    意思決定の精度や負荷にどのような影響を与えるかを調査することです。<br> """, unsafe_allow_html=True)
        
        st.markdown("###### 研究の方法", unsafe_allow_html=True)

        st.markdown("""本研究の実験は、クラウドソーシングプラットフォームからアプリケーションおよび回答フォームへアクセスして行います。
                    そのため、オンライン上で完結し、自宅など任意のインターネット接続環境で回答可能です。<br><br>
                    具体的に、以下の手順で取り組みます。<br>
                    1. 米国に住む成人のプロフィール情報(年齢や職業など)をもとに年収を予測する意思決定課題に、AIのサポートを受けながら取り組みます。<br>
                    ※課題に対する特別な事前知識は必要ありません。1つの課題につき1分程度、練習5問と本番20問の合計25問に取り組みます。<br>
                    ※各課題では、割り当てられたグループごとに異なる方法で、AIから提示される情報を参考にしながら回答します。<br>
                    2. すべての課題の終了後、AIの意思決定支援についての評価アンケートを行います。評価は7段階の尺度と自由記述で行います。<br><br>
                    実験の所要時間は約40分を予定しています。収集したデータは統計的に分析されます。個人を特定できる情報は収集しません。<br><br>""", unsafe_allow_html=True)        

        st.markdown("#### ２．研究協力の任意性と撤回の自由", unsafe_allow_html=True)

        st.markdown("""この研究にご協力いただくかどうかは、あなたの自由意思に委ねられています。回答中に取りやめることも可能です。
                    その場合は、途中までの回答は破棄され、研究に用いられることはありません。<br><br>
                    一旦ご同意いただいて実験を完了した後、もし同意を撤回される場合は「同意撤回書」に日付とIDを記載してご提出ください。
                    なお、研究にご協力いただけないことで、あなたの不利益に繋がることは一切ありません。
                    同意を撤回された場合には、提供いただいたアンケート回答は破棄され、以後研究に用いられることはありません。
                    ただし、本実験の内容が論文として出版された後には、同意を撤回しても、アンケート回答を破棄することができませんのでご理解ください。<br><br>
                    """, unsafe_allow_html=True)        

        st.markdown("#### ３．個人情報の保護", unsafe_allow_html=True)

        st.markdown("""研究にあたってはあなたに不利益が生じないように個人情報の保護、プライバシーの尊重に努力し最大限の注意を払います。
                    アンケートにおいて、あなたの年齢や性別などを聞きますが、この情報は、実験参加者の統計情報として用いるものです。
                    あなたの回答内容と紐づけられることはありません。<br><br>
                    """, unsafe_allow_html=True)    

        st.markdown("#### ４．研究成果の発表", unsafe_allow_html=True)

        st.markdown("""研究の成果は、氏名など個人が特定できないようにした上で、学会発表、学術雑誌及びホームページ等で公表します。<br><br>
                    """, unsafe_allow_html=True)    

        st.markdown("#### ５．研究参加者にもたらされる利益及びリスク・不利益  研究参加者への利益", unsafe_allow_html=True)

        st.markdown("""この研究が、あなたや社会に即座に有益な情報をもたらす可能性は、現在のところ低いと考えられます。
                    しかしながら、この研究の成果は、今後のAI研究の発展に重要な基礎的成果となることが期待されています。<br><br>
                    """, unsafe_allow_html=True)   
 
        st.markdown("###### 研究参加者へのリスク・不利益", unsafe_allow_html=True)

        st.markdown("""本研究は、身体的侵襲や精神的侵襲を伴いません。実験で用いる課題は、日常生活に影響を及ぼす可能性は低いです。
                    万が一、課題の内容が不快に感じられる場合は、回答を止めることが可能です。<br><br> """, unsafe_allow_html=True)

        st.markdown("#### ６．データの取扱方針", unsafe_allow_html=True)

        st.markdown("""あなたからいただいた匿名の回答データは、研究や分析等に用います。また、東京大学総合文化研究科馬場研究室において、
                    この研究成果の発表後少なくとも10年間保存いたします。<br><br>
                    """, unsafe_allow_html=True) 

        st.markdown("#### ７．謝礼の有無", unsafe_allow_html=True)

        st.markdown("""本研究に参加いただいた方には、謝礼として500円をクラウドソーシングプラットフォームを通してお支払いいたします。<br><br>
                    """, unsafe_allow_html=True) 

        st.markdown("#### ８．その他", unsafe_allow_html=True)

        st.markdown("""ご意見、ご質問などがございましたら、お気軽に下記までお寄せください。<br><br>
                    """, unsafe_allow_html=True)  

        st.markdown("###### 連絡先", unsafe_allow_html=True)

        st.markdown("""研究責任者<br>東京大学大学院総合文化研究科・広域科学専攻・准教授<br>馬場 雪乃<br>Mail: yukino-baba@g.ecc.u-tokyo.ac.jp<br>
                    研究実施者<br>東京大学大学院総合文化研究科・広域科学専攻・博士課程学生<br>土屋 祐太<br>Mail: ytsuchi28054@g.ecc.u-tokyo.ac.jp<br> """, unsafe_allow_html=True) 

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("上記の「研究へのご協力のお願い」をお読みになりましたか。", unsafe_allow_html=True)

        submitted = st.form_submit_button(label="はい、読みました。")
    
    if submitted:
        st.session_state.agreement_check = True

    if st.session_state.agreement_check == True:

        agreement_form = st.form(key="research_agreement_form")

        with agreement_form:
            st.markdown("###### 研究参加同意書", unsafe_allow_html=True)

            st.markdown("""東京大学大学院総合文化研究科・広域科学専攻・准教授<br>
                        馬場 雪乃 殿<br>
                        研究課題「人間の仮説に対してフィードバックを与える機械学習モデルが意思決定へ与える影響の調査」<br><br>
                        私は、上記研究への参加にあたり、「研究へのご協力のお願い」の記載事項について説明を受け、これを十分理解しましたので、本研究の研究参加者となることに同意いたします。<br>
                        以下の項目について、説明を受け理解しました。""", unsafe_allow_html=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if st.checkbox('この研究の概要について理解しました。'):
                st.session_state.form_submitted += 1
            st.markdown("<hr>", unsafe_allow_html=True)

            if st.checkbox('研究協力の任意性と撤回の自由について理解しました。'):
                st.session_state.form_submitted += 1     
            st.markdown("<hr>", unsafe_allow_html=True)

            if st.checkbox('個人情報の保護について理解しました。'):
                st.session_state.form_submitted += 1       
            st.markdown("<hr>", unsafe_allow_html=True)

            if st.checkbox('研究結果の発表について理解しました。'):
                st.session_state.form_submitted += 1
            st.markdown("<hr>", unsafe_allow_html=True)

            if st.checkbox('研究参加者にもたらされる利益及びリスク・不利益について理解しました。'):
                st.session_state.form_submitted += 1 
            st.markdown("<hr>", unsafe_allow_html=True)
           
            if st.checkbox('情報の取扱方針について理解しました。'):
                st.session_state.form_submitted += 1 
            st.markdown("<hr>", unsafe_allow_html=True)

            if st.checkbox('謝礼について理解しました。'):
                st.session_state.form_submitted += 1 
            st.markdown("<hr>", unsafe_allow_html=True)

            selected_date = st.date_input(
                "日付を入力してください。", 
                value=datetime.now().date()  # 初期値を今日の日付に設定
            )
            user_id = st.text_input("ユーザ名を入力してください。")

            submitted_form = st.form_submit_button(label="提出します。")

        if submitted_form:
            if not user_id.strip():
                st.error("ユーザ名は空白にできません。適切な値を入力してください。")
            elif st.session_state.form_submitted < 7:
                st.error("全ての同意事項にチェックを入れてください。")
            else:
                st.session_state.form_submitted = True

                #if st.session_state.form_submitted == True:
                    # クエリパラメータを取得
                    #query_params = st.experimental_get_query_params()

                    # パラメータの利用
                    #user_id = query_params.get("user_id")[0]

                max_retries=3

                retries = 0

                
                while retries <= max_retries:
                    try:

                        st.markdown("同意書を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)

                        f = drive.CreateFile({
                            'title': st.session_state.file_name,
                            'mimeType': 'application/vnd.google-apps.spreadsheet',
                            "parents": [{"id": st.secrets["folder_id"]}]
                        })
                        f.Upload()

                        st.session_state.file = f

                        # gspread用に認証
                        gc = gspread.authorize(credentials)

                        # スプレッドシートのIDを指定してワークブックを選択
                        workbook = gc.open_by_key(st.session_state.file['id'])
                        worksheet = workbook.sheet1

                        cell_list = worksheet.range(1, 1, 1, 9)
                        cell_list[0].value = 'この研究の概要について理解しました。'
                        cell_list[1].value = '研究協力の任意性と撤回の自由について理解しました。'
                        cell_list[2].value = '個人情報の保護について理解しました。'
                        cell_list[3].value = '研究結果の発表について理解しました。'
                        cell_list[4].value = '研究参加者にもたらされる利益及びリスク・不利益について理解しました。'
                        cell_list[5].value = '情報の取扱方針について理解しました。'
                        cell_list[6].value = '謝礼について理解しました。'
                        cell_list[7].value = str(selected_date)
                        cell_list[8].value = str(user_id)

                        # スプレッドシートを更新
                        worksheet.update_cells(cell_list)

                        st.session_state.agreement = True
                        retries += 5

                    except Exception as e:
                        st.error(f"しばらくお待ちください...")
                        if retries == max_retries:
                            st.error(f"申し訳ありませんが、同意書の提出がうまくいきませんでした。リロードして再度お試しいただけますと幸いです。")

                    # 再トライ準備
                    retries += 1

    if st.session_state.agreement == True:
        st.success("同意書の提出が完了しました！「次のページへ」をクリックしてください。")
        st.markdown("<hr>", unsafe_allow_html=True)

        st.session_state.page = "task1"

        if st.button("次のページへ"):
            if st.session_state.agreement == False:
                st.error("同意書に回答してください。提出がうまくいっていない場合は、申し訳ありませんがリロードして再度お試しください。")
            else:
                time.sleep(0.2)
                #go_to_page("task1")

    st.markdown("<hr>", unsafe_allow_html=True)

elif st.session_state.page == "task1":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked" not in st.session_state:
        st.session_state.start_button_clicked = False

    if st.button("ボタンを押してください"):
        st.session_state.start_button_clicked = True

    if st.session_state.start_button_clicked:
        st.markdown("同意書へのご回答ありがとうございました。これからタスクを開始します。<br>タスクは練習と本番に分けて、合計25問行います。また、最後に自由記述を含むアンケートへの回答もお願いします。所用時間は40分程度を見込んでいます。", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('# タスクの概要説明')

        st.markdown('## 概要')

        st.markdown("""
                    この調査では、米国に住む成人のプロフィール情報(年齢や職業など)をもとに、<b>複数のAI</b>と協力して年収を予想するタスクを行っていただきます。<br><br>
                    今回用いているデータは、1994年の米国国勢調査のデータをもとにした成人のプロフィール情報を用いています。全て公開情報です。<br>
                    プロフィールは、年齢、職業、職業分類、1週間の勤務時間、教育レベル、人種、性別、婚姻状況、出身国の9つの項目から構成されています。<br>
                    年収は<b>「5万ドル以下」</b>または<b>「5万ドルを超える」</b>の２つから選びます。<br><br>

                    それぞれのページで<b>「問題スタート」</b>ボタンをクリックすると、対象となるプロフィールが表示されます。<br>
                    まずは、AIの助けを借りずに自力で年収を予想しましょう。
                    年収の予想ができたら、該当するボタンとその自信を選んで、<b>「AIの予想を見る」</b>ボタンを押してください。<br>
                    すると、複数のAIがそれぞれの予測とその理由を説明します。
                    ただし、<b>AIの予想は必ずしも正しいわけではありません。</b>AIのグループ全員が間違っていることもあれば、一部のAIが正解していることもあります。<br><br>
                    プロフィール情報とAIの予想を考慮して、この人の年収を改めて予想しましょう。<br>
                    年収の予想ができたら、該当するボタンとその自信を選んで、最後に提出ボタンを押してください。<br><br>

                    練習を5問、本番を20問、合計25問に挑戦していただきます。<br><br>
                    """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('## 例')

        image_path = "./intro_1_red.png"  # ローカルの画像ファイルパス
        st.image(image_path, caption="問題を解く画面の例その1")
        image_path = "./intro_2_red.png"  # ローカルの画像ファイルパス
        st.image(image_path, caption="問題を解く画面の例その2")
        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('準備ができたら、下の「準備ができました」ボタンを押してください。練習問題(5問)が始まります。<br>', unsafe_allow_html=True)
        st.warning('【重要】画面の不具合がありましたら、右上の黒い点が3つあるボタンから「Rerun」を押してください。この先でURLをリロードすると最初からやり直しになります。')
        image_path = "./info.jpg"  # ローカルの画像ファイルパス
        st.image(image_path, caption="画面の不具合への対処方法")
        st.session_state.page = "t1p1"

        if st.button("準備ができました。"):
            time.sleep(0.2)
            st.session_state.page = "t1p1"
            st.rerun()
            #go_to_page("t1p1")

elif st.session_state.page == "t1p1":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t1p1" not in st.session_state:
        st.session_state.start_button_clicked_t1p1 = False
        st.session_state.question_t1p1_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t1p1 = True
        st.session_state.MORIAGE_YAKU_NAME = "moriage_yaku"
        st.session_state.MORIAGE_YAKU2_NAME = "moriage_yaku2"
        st.session_state.MORIAGE_YAKU3_NAME = "moriage_yaku3"
        st.session_state.img_moriyage_yaku1 = np.array(Image.open("./moriage_yaku1.png"))
        st.session_state.img_moriyage_yaku2 = np.array(Image.open("./moriage_yaku2.png"))
        st.session_state.img_moriyage_yaku3 = np.array(Image.open("./moriage_yaku3.png"))

        st.session_state.avator_img_dict = {
            st.session_state.MORIAGE_YAKU_NAME: st.session_state.img_moriyage_yaku1,
            st.session_state.MORIAGE_YAKU2_NAME: st.session_state.img_moriyage_yaku2,
            st.session_state.MORIAGE_YAKU3_NAME: st.session_state.img_moriyage_yaku3,
        }

        df1 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['26歳', '管理事務', '民間企業', '39時間', '高校卒業', '白人', '女性', '未婚', 'アメリカ合衆国']
        })
        df2 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['33歳', '管理事務', '民間企業', '35時間', '大学中退', '黒人', '女性', '未婚', 'アメリカ合衆国']
        })
        df3 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['36歳', '管理事務', '連邦政府', '40時間', '大学卒業', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df4 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['43歳', '経営・管理職', '民間企業', '50時間', '大学院修士', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df5 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['35歳', '機械操作・検査', '民間企業', '40時間', '高校卒業', '白人', '男性', '既婚', 'メキシコ']
        })


        st.session_state.df = [df1, df2, df3, df4, df5]


        AI_message_1 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>年齢が若く、学歴が高校卒であること、民間企業の管理事務職で勤務時間が平均的であることから、高収入に達しにくいと考え、5万ドル以下と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>未婚女性であり、扶養家族の有無や昇進の影響を受けにくい可能性があること、また当時の統計的に女性の平均年収が低めである点から、5万ドル以下と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>週39時間のフルタイム勤務であり、管理事務という安定職に従事している点から、勤続年数や業績次第では昇給の可能性があり、5万ドル超と予測しました。"
        ]

        AI_message_2 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>教育レベルが大学中退であり、勤務時間が週35時間とフルタイムよりやや少ないこと、また1994年当時の人種・性別格差を踏まえ、5万ドル以下と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>未婚で扶養の必要がない可能性があり、また管理事務職は昇給幅が比較的限られる職種であることから、高収入に届きにくいと判断し、5万ドル以下と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>年齢が33歳と中堅層である一方、民間企業における管理事務職は高度な専門職に比べ賃金水準が低めな傾向があり、5万ドル以下と予測しました。"
        ]

        AI_message_3 =[
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>大学卒で、安定性と給与水準の高い連邦政府勤務に就き、週40時間のフルタイム勤務をしていることから、5万ドル超の収入が見込まれると予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>年齢が36歳と中堅であり、既婚者として生活基盤が安定していることから、昇進や勤続年数による昇給の可能性が高く、5万ドル超と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>管理事務職は連邦政府勤務であっても専門職や技術職に比べ給与水準が抑えられる傾向があり、その点を重視して5万ドル以下と予測しました。"
        ]

        AI_message_4 =[
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>大学院修士の高学歴に加え、民間企業で経営・管理職に就き、週50時間の長時間勤務をしていることから、高収入が期待でき、5万ドル超と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>43歳で既婚、民間企業でのキャリアも長いと推察され、役職や業績に応じた報酬が見込まれる年齢層であるため、5万ドル超と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>性別が男性であることから、1994年当時の賃金格差の影響を受けにくく、特に管理職では平均年収が高めである傾向があり、5万ドル超と予測しました。"
        ]

        AI_message_5 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>高校卒で技能職に従事し、週40時間勤務と平均的であることに加え、出身国による当時の賃金格差の影響も考慮し、5万ドル以下と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>35歳既婚男性で勤続年数が長いと考えられ、フルタイム勤務かつ製造業などでは熟練度により昇給の可能性があるため、5万ドル超と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>機械操作・検査職は賃金水準が比較的低く、高校卒という学歴も昇給に制限がある可能性があり、また出身国がメキシコである点から移民労働者の賃金格差も考慮し、5万ドル以下と予測しました。"
        ]

        st.session_state.AI_message = [AI_message_1, AI_message_2, AI_message_3, AI_message_4, AI_message_5]

        st.session_state.correct_answer = ["「5万ドル以下(≦$50,000)」", "「5万ドル以下(≦$50,000)」", "「5万ドル以下(≦$50,000)」", "「5万ドル超(>$50,000)」", "「5万ドル以下(≦$50,000)」"]

        st.session_state.cell_num = ["A", "B", "C", "D", "E"]

        st.session_state.page_num = 0
    
    if st.session_state.start_button_clicked_t1p1:
        st.title("練習問題 その1")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai1")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            st.session_state.already_ai_said = True

            form = st.form(key="t1p1")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}10', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}11', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}12', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}13', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}14', str(elapsed_time))

                            st.session_state.question_t1p1_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.markdown(f"#### 正解は{st.session_state.correct_answer[st.session_state.page_num]}でした。", unsafe_allow_html=True)

                            st.session_state.page = "t1p2"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t1p1",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t1p1_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t1p2"
                st.rerun()

elif st.session_state.page == "t1p2":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t1p2" not in st.session_state:
        st.session_state.start_button_clicked_t1p2 = False
        st.session_state.question_t1p2_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t1p2 = True
        st.session_state.page_num = 1

    if st.session_state.start_button_clicked_t1p2:
        st.title("練習問題 その2")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai2")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t1p2")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}10', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}11', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}12', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}13', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}14', str(elapsed_time))

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.markdown(f"#### 正解は{st.session_state.correct_answer[st.session_state.page_num]}でした。", unsafe_allow_html=True)

                            st.session_state.question_t1p2_finished = True
                            st.session_state.page = "t1p3"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t1p2",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t1p2_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t1p3"
                st.rerun()


elif st.session_state.page == "t1p3":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t1p3" not in st.session_state:
        st.session_state.start_button_clicked_t1p3 = False
        st.session_state.question_t1p3_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t1p3 = True
        st.session_state.page_num = 2

    if st.session_state.start_button_clicked_t1p3:
        st.title("練習問題 その3")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai3")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t1p3")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}10', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}11', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}12', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}13', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}14', str(elapsed_time))

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.markdown(f"#### 正解は{st.session_state.correct_answer[st.session_state.page_num]}でした。", unsafe_allow_html=True)

                            st.session_state.question_t1p3_finished = True
                            st.session_state.page = "t1p4"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t1p3",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t1p3_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t1p4"
                st.rerun()


elif st.session_state.page == "t1p4":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t1p4" not in st.session_state:
        st.session_state.start_button_clicked_t1p4 = False
        st.session_state.question_t1p4_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t1p4 = True
        st.session_state.page_num = 3

    if st.session_state.start_button_clicked_t1p4:
        st.title("練習問題 その4")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai4")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t1p4")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}10', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}11', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}12', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}13', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}14', str(elapsed_time))

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.markdown(f"#### 正解は{st.session_state.correct_answer[st.session_state.page_num]}でした。", unsafe_allow_html=True)

                            st.session_state.question_t1p4_finished = True
                            st.session_state.page = "t1p5"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t1p4",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t1p4_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t1p5"
                st.rerun()

elif st.session_state.page == "t1p5":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t1p5" not in st.session_state:
        st.session_state.start_button_clicked_t1p5 = False
        st.session_state.question_t1p5_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t1p5 = True
        st.session_state.page_num = 4

    if st.session_state.start_button_clicked_t1p5:
        st.title("練習問題 その5")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai5")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t1p5")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}10', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}11', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}12', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}13', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}14', str(elapsed_time))

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.markdown(f"#### 正解は{st.session_state.correct_answer[st.session_state.page_num]}でした。", unsafe_allow_html=True)

                            st.session_state.question_t1p5_finished = True
                            st.session_state.page = "task2"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t1p5",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t1p5_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "task2"
                st.rerun()


elif st.session_state.page == "task2":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2" not in st.session_state:
        st.session_state.start_button_clicked_t2 = False

    if st.button("ボタンを押してください"):
        st.session_state.start_button_clicked_t2 = True

    if st.session_state.start_button_clicked_t2:

        st.markdown("""
                    練習問題お疲れ様でした。それでは、本番の20問に進みます。<br>
                    """, unsafe_allow_html=True)

        st.markdown('準備ができたら、下の「準備ができました」ボタンを押してください。')

        st.session_state.page = "t2p1"

        if st.button("準備ができました。"):
            time.sleep(0.2)
            #go_to_page("t2p1")
            st.session_state.page = "t2p1"
            st.rerun()

elif st.session_state.page == "t2p1":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p1" not in st.session_state:
        st.session_state.start_button_clicked_t2p1 = False
        st.session_state.question_t2p1_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p1 = True
        st.session_state.MORIAGE_YAKU_NAME = "moriage_yaku"
        st.session_state.MORIAGE_YAKU2_NAME = "moriage_yaku2"
        st.session_state.MORIAGE_YAKU3_NAME = "moriage_yaku3"
        st.session_state.img_moriyage_yaku1 = np.array(Image.open("./moriage_yaku1.png"))
        st.session_state.img_moriyage_yaku2 = np.array(Image.open("./moriage_yaku2.png"))
        st.session_state.img_moriyage_yaku3 = np.array(Image.open("./moriage_yaku3.png"))

        st.session_state.avator_img_dict = {
            st.session_state.MORIAGE_YAKU_NAME: st.session_state.img_moriyage_yaku1,
            st.session_state.MORIAGE_YAKU2_NAME: st.session_state.img_moriyage_yaku2,
            st.session_state.MORIAGE_YAKU3_NAME: st.session_state.img_moriyage_yaku3,
        }

        df1 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['18歳', 'その他のサービス', '民間企業', '20時間', '大学中退', '白人', '男性', '未婚', 'アメリカ合衆国']
        })
        df2 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['25歳', '専門職', '民間企業', '40時間', '大学卒業', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df3 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['28歳', '警護サービス', '地方政府', '40時間', '短大卒業', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df4 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['55歳', '経営・管理職', '民間企業', '50時間', '大学院修士', 'アジア太平洋諸島系', '女性', '未婚', 'タイ']
        })
        df5 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['29歳', '経営・管理職', '民間企業', '40時間', '専門学校卒業', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df6 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['47歳', '管理事務', '地方政府', '40時間', '高校卒業', '白人', '女性', '離婚', 'アメリカ合衆国']
        })
        df7 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['43歳', '管理事務', '民間企業', '30時間', '高校卒業', '白人', '女性', '既婚', 'アメリカ合衆国']
        })
        df8 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['34歳', '技術サポート', '民間企業', '47時間', '大学卒業', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df9 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['34歳', 'その他のサービス', '民間企業', '35時間', '大学中退', '黒人', '女性', '未婚', 'アメリカ合衆国']
        })
        df10 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['54歳', '工芸品・修理', '民間企業', '35時間', '高校卒業', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df11 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['23歳', '警護サービス', '地方政府', '40時間', '大学中退', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df12 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['36歳', '専門職', '地方政府', '40時間', '大学卒業', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df13 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['27歳', '工芸品・修理', '自営業（非法人）', '60時間', '高校卒業', '白人', '男性', '既婚', 'アイルランド']
        })
        df14 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['65歳', '専門職', '民間企業', '50時間', '大学院修士', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df15 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['44歳', '販売', '自営業（法人）', '45時間', '専門学校卒業', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df16 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['39歳', '運搬・清掃', '民間企業', '40時間', '高校卒業', '黒人', '男性', '離婚', 'アメリカ合衆国']
        })
        df17 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['50歳', '輸送・引越し', '民間企業', '40時間', '高校卒業', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df18 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['32歳', '警護サービス', '地方政府', '50時間', '大学中退', '白人', '男性', '既婚', 'キューバ']
        })
        df19 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['46歳', '専門職', '民間企業', '40時間', '大学院修士', '白人', '男性', '既婚', 'アメリカ合衆国']
        })
        df20 = pd.DataFrame({
            '項目': ['年齢', '職業', '職業分類', '1週間の勤務時間', '教育レベル', '人種', '性別', '婚姻状況', '出身国'],
            '内容': ['48歳', '管理事務', '地方政府', '40時間', '大学院修士', '黒人', '女性', '別居', 'アメリカ合衆国']
        })

        st.session_state.df = [df1, df2, df3, df4, df5, df6, df7, df8, df9, df10, df11, df12, df13, df14, df15, df16, df17, df18, df19, df20]


        AI_message_1 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>若年で学歴が大学中退、パートタイム勤務、職業も高収入職でないため、全体的に収入が高くなりにくい要素が多く、5万ドル以下と予想しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>勤務時間が週20時間と短く、職業も高賃金でない「その他のサービス」であることから、年収が5万ドルを超える可能性は低いと判断しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>若くして高収入を得る例外も存在し、アメリカ出身で英語が母語と想定される点や、企業内で特殊なスキルを持つ可能性を考慮し5万ドル超と予測しました。"
        ]

        AI_message_2 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>専門職で学歴もありフルタイム勤務ですが、年齢が若くキャリア初期と考えられるため、まだ年収が5万ドルを超えていない可能性が高いと判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>フルタイム勤務ではあるが、出身がアメリカで特別な移民スキル優遇などはなく、年齢的にも昇進経験が少ないと考え、収入は5万ドル以下と推定しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>既婚で民間企業に勤務しているものの、1994年当時の相場や年齢的に管理職ではないと推定され、収入がまだ5万ドルに達していないと予想しました。"
        ]

        AI_message_3 =[
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>地方政府に勤める警護職は安定した公務であり、フルタイム勤務かつ既婚・定職ありの28歳であれば、年収が5万ドルを超えている可能性が高いと判断しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>短大卒で専門性があり、地方政府勤務は福利厚生や昇給制度が整っている傾向があるため、安定したキャリア形成により5万ドル超と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>警護サービスは公共職でも必ずしも高給ではなく、28歳とまだ若いため昇給も限定的と考えられ、年収は5万ドル以下にとどまる可能性が高いと判断しました。"
        ]

        AI_message_4 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>高学歴かつ管理職ですが、1994年当時のアジア系女性・移民に対する賃金格差や昇進の壁を考慮し、5万ドル以下の可能性があると判断しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>55歳で週50時間勤務の経営・管理職という点から、長年のキャリアと責任ある立場がうかがえ、経験と役職に見合う収入で5万ドル超と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>民間企業勤務でも、出身国がタイであることから移民としての不利や昇進機会の制限が想定され、1994年当時の状況では5万ドル以下と見なしました。"
        ]

        AI_message_5 =[
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>29歳と若手ながらも経営・管理職に就き、フルタイム勤務をしていることから、職責と役職の影響で年収が5万ドルを超えている可能性が高いと判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>専門学校卒であり、29歳とまだキャリアの初期段階であることから、管理職でも役職が限定的で年収が5万ドル以下にとどまる可能性があると考えました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>民間企業勤務で週40時間と標準的な労働時間にとどまり、特に高収入が期待される業種や学歴でもないため、年収は5万ドル以下と推定しました。"
        ]

        AI_message_6 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>地方政府勤務で安定性はあるものの、学歴が高校卒であり、管理事務職は給与水準が高くないため、年収は5万ドル以下と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>週40時間の標準勤務で、年齢や職種から長年の経験はあるものの、女性で離婚歴があり、1994年当時の賃金格差の影響を受けている可能性があると判断しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>47歳で地方政府の管理事務に長く従事していると考えられ、勤続年数に応じた昇給や安定した福利厚生により、5万ドル超の年収に達している可能性があると判断しました。"
        ]

        AI_message_7 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>民間企業で管理事務に従事していますが、週30時間の短時間勤務であり、高校卒の学歴からも昇給幅が限られると考え、年収は5万ドル以下と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>43歳で既婚、長年の勤務により管理事務職でも役職や責任が上がっている可能性があり、勤続による昇給で5万ドル超に達していると判断しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>民間企業勤務で管理事務とはいえ、業種によっては高収入部門もあり、43歳という働き盛りの年齢と安定した生活環境から5万ドル超と予想しました。"
        ]    

        AI_message_8 =[
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>大学卒でフルタイム以上の勤務をこなす34歳の技術職男性は、民間企業内で経験も積んでいると考えられ、年収が5万ドルを超える可能性が高いと判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>技術サポート職は専門性があっても賃金水準が比較的低めな傾向があり、民間企業勤務でも管理職でない限り、年収は5万ドル以下にとどまると判断しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>47時間と長時間勤務をしており、既婚かつ大学卒のスキルを活かして成果を上げていると考えられるため、勤続年数と努力に見合う収入で5万ドル超と予想しました。"
        ]

        AI_message_9 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>大学中退で専門資格がなく、「その他のサービス」は高収入職種でない場合が多く、週35時間の短時間勤務でもあり、年収は5万ドル以下と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>民間企業勤務でフルタイム未満の労働時間に加え、1994年当時の黒人女性に対する賃金格差の影響も考慮し、5万ドル以下と判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>34歳で未婚、キャリアの安定性や扶養の有無が不明であり、「その他のサービス」は収入変動が大きく、安定した高収入には届きにくいと考え5万ドル以下と予測しました。"
        ]

        AI_message_10 =[
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>54歳で長年の経験と技能を積んでいると考えられ、工芸品・修理職でも熟練者として高単価の仕事を担っている可能性があり、5万ドル超と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>民間企業に所属しつつも週35時間の安定勤務を継続している点や、既婚で生活基盤が整っていることから、安定した収入で5万ドル超に達していると判断しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>高校卒ながらも職人系の工芸・修理職は実績に応じた報酬が得られることもあり、54歳という年齢から高い技能と信頼を積み重ねた結果と考え5万ドル超と予測しました。"
        ]

        AI_message_11 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>年齢が23歳と若く、キャリアの初期段階であることに加え、大学中退で昇進の機会が限られる可能性があり、年収は5万ドル以下と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>地方政府の警護職は公的安定職であり、既婚かつフルタイム勤務の責任ある立場にあることから、若くても手当等を含めて5万ドル超の可能性があると判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>地方政府勤務で安定性はあるものの、警護サービス職は初任給水準が低めであり、23歳という若さからも昇給がまだ進んでいないと考え、5万ドル以下と予測しました。"
        ]  

        AI_message_12 =[
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>大学卒の専門職で地方政府に勤務し、36歳・既婚・フルタイムという安定した生活基盤があるため、経験年数や職責に応じて5万ドル超の年収と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>地方政府の専門職は福利厚生や昇給制度が整っており、36歳で安定したキャリアを積んでいると考えられるため、年収は5万ドルを超えていると判断しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>専門職はスキルが求められる分野であり、白人男性として1994年当時の賃金構造上有利な立場にあることから、年収は5万ドル超と判断しました。"
        ]

        AI_message_13 =[
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>60時間の長時間労働を行う自営業者であり、職人系の仕事は技術次第で高収入も可能なため、努力と需要により5万ドル超の年収に達していると判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>27歳と若く、学歴が高校卒で自営業（非法人）のため、初期投資や経営安定に時間を要することが多く、収入はまだ5万ドル以下と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>自営業であることから収入上限が職種次第で高く、既婚かつアイルランド出身の白人男性という背景も米国での経済的機会に恵まれており、5万ドル超と予測しました。"
        ]

        AI_message_14 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>65歳という年齢からフルタイム勤務でも退職直前や再雇用の可能性があり、収入が抑えられている場合もあるため、5万ドル以下と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>大学院修士で専門職でも、65歳で民間企業に勤務している場合、年金受給との両立や役職引退により、年収が抑えられている可能性があると判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>週50時間勤務でも、65歳という年齢から非常勤やコンサル契約の形態で働いている可能性があり、正規雇用と比べて年収が低いと考え5万ドル以下と予測しました。"
        ]

        AI_message_15 =[
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>法人経営の自営業者であり、販売職でも規模や業績によって高収入が見込まれ、45時間勤務・44歳の働き盛りという点から5万ドル超と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>既婚で長年事業を継続していると考えられ、専門学校卒の実務スキルを活かして安定した売上を上げている可能性が高く、5万ドル超と判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>販売職の自営業でも競争が激しく、専門学校卒で資本規模が小さい可能性もあり、45時間勤務でも利益が限定的で年収は5万ドル以下と予測しました。"
        ]

        AI_message_16 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>運搬・清掃職は賃金水準が比較的低く、高校卒で昇進の機会も限られる傾向があり、40時間勤務でも5万ドル以下の年収にとどまると判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>39歳でフルタイム勤務でも、離婚歴があり、経済的に不安定な状況にある可能性や、1994年当時の黒人労働者への賃金格差を考慮し、5万ドル以下と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>39歳で民間企業における運搬・清掃職でも、長年の勤続により時給が上昇している可能性があり、フルタイム勤務の積み重ねで5万ドル超に達していると判断しました。"
        ]

        AI_message_17 =[
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>50歳で長年の経験を積み、輸送・引越し業でも昇給や役割の変化により収入が上がっている可能性があり、安定した勤務状況から5万ドル超と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>高校卒で輸送・引越し業に従事し、週40時間の標準勤務では賃金上昇の余地が限られるため、50歳でも年収が5万ドル以下にとどまると判断しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>輸送・引越し業は体力と経験が求められ、50歳で長年勤続していれば賃金も上昇していると考えられ、民間企業での安定収入により5万ドル超と予想しました。"
        ]

        AI_message_18 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>大学中退で学歴が限定されており、地方政府の警護職は安定していても賃金水準が高くないことが多く、移民背景も考慮し5万ドル以下と予測しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>週50時間勤務でも、32歳と比較的若く昇進の途中段階と考えられ、警護サービスは賃金上昇の幅が限られるため、年収は5万ドル以下と判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>地方政府勤務で安定性はあるものの、出身がキューバであることから1994年当時の移民に対する昇進や賃金面での制約が影響し、5万ドル以下と予測しました。"
        ]

        AI_message_19 =[
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>大学院修士卒の専門職であり、46歳・既婚・フルタイム勤務という安定した立場から、十分なキャリアと収入実績があると考え、5万ドル超と予測しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>民間企業で専門職に従事し、高度な学歴と年齢的に豊富な経験があることから、中堅以上の役職や責任ある立場についており、5万ドル超と判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>大学院修士卒でも専門職の分野によっては賃金が低めな場合もあり、46歳でフルタイム勤務でも業界や地域経済の影響を受け、5万ドル以下と判断しました。"
        ]

        AI_message_20 =[
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>大学院修士卒でも、地方政府の管理事務職は賃金上限が比較的低く、1994年当時の黒人女性に対する賃金格差の影響もあり、年収は5万ドル以下と判断しました。",
            "<strong>「5万ドル以下(≦$50,000)」</strong>と予想します。<br>週40時間勤務の公務でも、管理事務職は責任範囲が限定されることが多く、昇進機会も限られるため、修士卒でも年収は5万ドル以下と判断しました。",
            "<strong>「5万ドル超(>$50,000)」</strong>と予想します。<br>48歳で大学院修士の学歴を持ち、地方政府の管理職に長年勤務していると考えられ、経験と職責に見合う報酬として年収は5万ドル超と予測しました。"
        ]

        st.session_state.AI_message = [AI_message_1, AI_message_2, AI_message_3, AI_message_4, AI_message_5, AI_message_6, AI_message_7, AI_message_8, AI_message_9, AI_message_10, AI_message_11, AI_message_12, AI_message_13, AI_message_14, AI_message_15]

        st.session_state.cell_num = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]

        st.session_state.page_num = 0

    if st.session_state.start_button_clicked_t2p1:
        st.title("問題 その1")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ai6")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p1")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p1_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p2"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p1",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p1_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p2"
                st.rerun()



elif st.session_state.page == "t2p2":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p2" not in st.session_state:
        st.session_state.start_button_clicked_t2p2 = False
        st.session_state.question_t2p2_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p2 = True
        st.session_state.page_num = 1

    if st.session_state.start_button_clicked_t2p2:
        st.title("問題 その2")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h2")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p2")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p2_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p3"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p2",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p2_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p3"
                st.rerun()


elif st.session_state.page == "t2p3":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p3" not in st.session_state:
        st.session_state.start_button_clicked_t2p3 = False
        st.session_state.question_t2p3_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p3 = True
        st.session_state.page_num = 2

    if st.session_state.start_button_clicked_t2p3:
        st.title("問題 その3")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h3")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p3")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p3_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p4"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p3",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p3_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p4"
                st.rerun()



elif st.session_state.page == "t2p4":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p4" not in st.session_state:
        st.session_state.start_button_clicked_t2p4 = False
        st.session_state.question_t2p4_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p4 = True
        st.session_state.page_num = 3

    if st.session_state.start_button_clicked_t2p4:
        st.title("問題 その4")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h4")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p4")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p4_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p5"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p4",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p4_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p5"
                st.rerun()

elif st.session_state.page == "t2p5":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p5" not in st.session_state:
        st.session_state.start_button_clicked_t2p5 = False
        st.session_state.question_t2p5_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p5 = True
        st.session_state.page_num = 4

    if st.session_state.start_button_clicked_t2p5:
        st.title("問題 その5")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h5")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p5")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p5_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p6"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p5",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p5_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p6"
                st.rerun()


elif st.session_state.page == "t2p6":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p6" not in st.session_state:
        st.session_state.start_button_clicked_t2p6 = False
        st.session_state.question_t2p6_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p6 = True
        st.session_state.page_num = 5

    if st.session_state.start_button_clicked_t2p6:
        st.title("問題 その6")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h6")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p6")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p6_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p7"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p6",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p6_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p7"
                st.rerun()

elif st.session_state.page == "t2p7":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p7" not in st.session_state:
        st.session_state.start_button_clicked_t2p7 = False
        st.session_state.question_t2p7_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p7 = True
        st.session_state.page_num = 6

    if st.session_state.start_button_clicked_t2p7:
        st.title("問題 その7")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h7")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p7")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p7_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p8"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p7",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p7_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p8"
                st.rerun()

elif st.session_state.page == "t2p8":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p8" not in st.session_state:
        st.session_state.start_button_clicked_t2p8 = False
        st.session_state.question_t2p8_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p8 = True
        st.session_state.page_num = 7

    if st.session_state.start_button_clicked_t2p8:
        st.title("問題 その8")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h8")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p8")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p8_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p9"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p8",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p8_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p9"
                st.rerun()


elif st.session_state.page == "t2p9":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p9" not in st.session_state:
        st.session_state.start_button_clicked_t2p9 = False
        st.session_state.question_t2p9_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p9 = True
        st.session_state.page_num = 8

    if st.session_state.start_button_clicked_t2p9:
        st.title("問題 その9")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h9")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p9")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p9_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p10"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p9",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p9_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p10"
                st.rerun()

elif st.session_state.page == "t2p10":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p10" not in st.session_state:
        st.session_state.start_button_clicked_t2p10 = False
        st.session_state.question_t2p10_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p10 = True
        st.session_state.page_num = 9

    if st.session_state.start_button_clicked_t2p10:
        st.title("問題 その10")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h10")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p10")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p10_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p11"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p10",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p10_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p11"
                st.rerun()

elif st.session_state.page == "t2p11":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p11" not in st.session_state:
        st.session_state.start_button_clicked_t2p11 = False
        st.session_state.question_t2p11_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p11 = True
        st.session_state.page_num = 10

    if st.session_state.start_button_clicked_t2p11:
        st.title("問題 その11")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h11")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p11")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p11_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p12"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p11",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p11_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p12"
                st.rerun()

elif st.session_state.page == "t2p12":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p12" not in st.session_state:
        st.session_state.start_button_clicked_t2p12 = False
        st.session_state.question_t2p12_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p12 = True
        st.session_state.page_num = 11

    if st.session_state.start_button_clicked_t2p12:
        st.title("問題 その12")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h12")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p12")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p12_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p13"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p12",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p12_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p13"
                st.rerun()

elif st.session_state.page == "t2p13":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p13" not in st.session_state:
        st.session_state.start_button_clicked_t2p13 = False
        st.session_state.question_t2p13_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p13 = True
        st.session_state.page_num = 12

    if st.session_state.start_button_clicked_t2p13:
        st.title("問題 その13")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h13")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p13")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p13_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p14"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p13",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p13_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p14"
                st.rerun()

elif st.session_state.page == "t2p14":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p14" not in st.session_state:
        st.session_state.start_button_clicked_t2p14 = False
        st.session_state.question_t2p14_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p14 = True
        st.session_state.page_num = 13

    if st.session_state.start_button_clicked_t2p14:
        st.title("問題 その14")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h14")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p14")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p14_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p15"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p14",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p14_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p15"
                st.rerun()

elif st.session_state.page == "t2p15":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p15" not in st.session_state:
        st.session_state.start_button_clicked_t2p15 = False
        st.session_state.question_t2p15_finished = False
        st.session_state.human_prediction_finished = False
        st.session_state.already_ai_said = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p15 = True
        st.session_state.page_num = 14

    if st.session_state.start_button_clicked_t2p15:
        st.title("問題 その15")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h15")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p15")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p15_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p16"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p15",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p15_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p16"
                st.rerun()


elif st.session_state.page == "t2p16":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p16" not in st.session_state:
        st.session_state.start_button_clicked_t2p16 = False
        st.session_state.question_t2p16_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p16 = True
        st.session_state.page_num = 15

    if st.session_state.start_button_clicked_t2p16:
        st.title("問題 その16")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h16")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p16")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p16_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p17"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p16",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p16_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p17"
                st.rerun()



elif st.session_state.page == "t2p17":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p17" not in st.session_state:
        st.session_state.start_button_clicked_t2p17 = False
        st.session_state.question_t2p17_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p17 = True
        st.session_state.page_num = 16

    if st.session_state.start_button_clicked_t2p17:
        st.title("問題 その17")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h17")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p17")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p17_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p18"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p17",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p17_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p18"
                st.rerun()


elif st.session_state.page == "t2p18":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p18" not in st.session_state:
        st.session_state.start_button_clicked_t2p18 = False
        st.session_state.question_t2p18_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p18 = True
        st.session_state.page_num = 17

    if st.session_state.start_button_clicked_t2p18:
        st.title("問題 その18")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h18")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p18")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p18_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p19"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p18",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p18_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p19"
                st.rerun()


elif st.session_state.page == "t2p19":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p19" not in st.session_state:
        st.session_state.start_button_clicked_t2p19 = False
        st.session_state.question_t2p19_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p19 = True
        st.session_state.page_num = 18

    if st.session_state.start_button_clicked_t2p19:
        st.title("問題 その19")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h19")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p19")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p19_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "t2p20"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p19",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p19_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "t2p20"
                st.rerun()


elif st.session_state.page == "t2p20":
    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "start_button_clicked_t2p20" not in st.session_state:
        st.session_state.start_button_clicked_t2p20 = False
        st.session_state.question_t2p20_finished = False
        st.session_state.human_prediction_finished = False

    if st.button("問題スタート"):
        st.session_state.start = time.time()
        st.session_state.start_button_clicked_t2p20 = True
        st.session_state.page_num = 19

    if st.session_state.start_button_clicked_t2p20:
        st.title("問題 その20")
        st.markdown("以下のプロフィール情報をもとに、年収を予想してください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### プロフィール", unsafe_allow_html=True)
        # DataFrameを表示
        st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        form = st.form(key="ait2h20")
        with form:
            text0 = st.selectbox("年収はいくらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
            confidence0 = st.select_slider(
                "この予測にどれくらい自信がありますか？",
                options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                value="どちらでもない"
            )
            submitted = st.form_submit_button(label="AIの予想を見る")

        if submitted:
            if text0 == "選択してください":
                st.error("回答を選んでください。")
            else:
                if st.session_state.human_prediction_finished == False:
                    st.session_state.text0 = text0
                    st.session_state.confidence0 = confidence0
                st.session_state.human_prediction_finished = True


        if st.session_state.human_prediction_finished:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("続いて、複数のAIから得られた予測を提示します。", unsafe_allow_html=True)
            st.markdown("#### プロフィール", unsafe_allow_html=True)
            st.markdown(st.session_state.df[st.session_state.page_num].style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown("", unsafe_allow_html=True)
            #st.markdown("#### 複数のAIから得られた予測と理由", unsafe_allow_html=True)

            AI_message = st.session_state.AI_message[st.session_state.page_num]

            with st.chat_message(st.session_state.MORIAGE_YAKU_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU_NAME]):
                st.markdown(
                    f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                    f"{AI_message[0]}"
                    '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU2_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU2_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[1]}"
                        '</div>', unsafe_allow_html=True)
                st.markdown("", unsafe_allow_html=True)
            with st.chat_message(st.session_state.MORIAGE_YAKU3_NAME, avatar=st.session_state.avator_img_dict[st.session_state.MORIAGE_YAKU3_NAME]):
                if st.session_state.already_ai_said:
                    st.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
                else:
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("AIが考えています...", unsafe_allow_html=True)
                    time.sleep(5)
                    thinking_placeholder.markdown(
                        f'<div style="background-color: #fff2b8; border-radius: 10px; padding: 10px;">'
                        f"{AI_message[2]}"
                        '</div>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.session_state.already_ai_said = True
            form = st.form(key="t2p20")

            with form:
                text1 = st.selectbox("最終的に、年収はどちらだと思いますか？", ["選択してください", "5万ドル以下(≦$50,000)", "5万ドル超(>$50,000)"])
                confidence1 = st.select_slider(
                    "この予測にどれくらい自信がありますか？",
                    options=["全く自信がない", "自信がない", "あまり自信がない", "どちらでもない", "やや自信がある", "自信がある", "非常に自信がある"],
                    value="どちらでもない"
                )
                submitted_f = st.form_submit_button(label="回答を提出")

            if submitted_f:

                if text1 == "選択してください":
                    st.error("回答を選んでください。")
                else:
                    st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
                    max_retries=3
                    retries = 0
                    while retries <= max_retries:
                        scopes = ['https://spreadsheets.google.com/feeds',
                                'https://www.googleapis.com/auth/drive']
                        json_keyfile_dict = st.secrets["service_account"]
                        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                            json_keyfile_dict, 
                            scopes
                        )
                        # gspread用に認証
                        gc = gspread.authorize(credentials)
                        try:
                            # スプレッドシートのIDを指定してワークブックを選択
                            workbook = gc.open_by_key(st.session_state.file['id'])
                            worksheet = workbook.sheet1

                            st.session_state.end = time.time()

                            elapsed_time = st.session_state.end - st.session_state.start

                            # A1のセルに入力
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}20', st.session_state.text0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}21', st.session_state.confidence0)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}22', text1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}23', confidence1)
                            worksheet.update_acell(f'{st.session_state.cell_num[st.session_state.page_num]}24', str(elapsed_time))

                            st.session_state.question_t2p20_finished = True

                            st.success("回答を提出しました！次の問題に進んでください。")

                            st.session_state.page = "questionnaire"

                            retries += 5
                        except Exception as e:
                            print(e)
                            f = drive.CreateFile({
                                'title': st.session_state.file_name+"_t2p20",
                                'mimeType': 'application/vnd.google-apps.spreadsheet',
                                "parents": [{"id": st.secrets["folder_id"]}]
                            })
                            f.Upload()
                            st.session_state.file = f

                            if retries == max_retries:
                                st.error(f"申し訳ありませんが、課題の提出がうまくいきませんでした。右上の黒い点が3つあるボタンから「Rerun」を押してください。")

                        # 再トライ準備
                        retries += 1

        if st.session_state.question_t2p20_finished:
            if st.button("次の問題に進む"):
                time.sleep(0.2)
                st.session_state.page = "questionnaire"
                st.rerun()


elif st.session_state.page == "questionnaire":

    st.markdown(st.session_state.custom_css, unsafe_allow_html=True)

    # セッション状態の初期化
    if "questionnaire" not in st.session_state:
        st.session_state.questionnaire = False

    st.markdown('# ユーザアンケートページ')
    st.markdown('タスクの完了お疲れ様でした。 <br> 最後に、以下の評価アンケートを記入して提出をお願いします。', unsafe_allow_html=True)
    form = st.form(key="questionnaire_form")

    with form:
        # 質問リスト
        questions = [
            "AIに自分の意見を誘導されたと感じましたか。",
            "AIが提示した情報をもとに、自分の考えを変えようと思いましたか。AIのヒントに従おうと思いましたか。",
            "AAIからプレッシャーを感じましたか。あるいは押し付けがましく感じましたか。",
            "意思決定を主体的に行なったと感じますか。",
            "意思決定の結果に対する責任はAIにあると思いますか。",
            "AIはあなたよりも賢いと感じましたか。",
            "AIによる支援は、あなたを混乱させましたか。",
            "AIによる支援は、あなたの考えを整理させるのに役立ちましたか。",
            "意思決定の負荷はどう感じましたか。",
            "AIはより少ない労力で課題を完了するために役立ちそうですか？",
            "技術システムについて詳細に調べるのが好きですか。",
            "新しい技術システムの機能をテストするのが好きですか。",
            "技術システムを主に扱うのは、やらなければならないからですか。",
            "新しい技術システムを目の前にすると、徹底的に試しますか。",
            "新しい技術システムに慣れるために時間を費やすのが好きですか。",
            "技術システムが機能するだけで十分で、どのように、なぜ機能するかは気にしませんか。",
            "技術システムがどのように機能するかを正確に理解しようと努めますか。",
            "技術システムの基本的な機能を知っていれば十分ですか。",
            "技術システムの機能を最大限に活用しようと努めますか。",
            "あなた自身は、新しいことが好きで、変わった考えを持つと思いますか。",
            "あなた自身は、人に気をつかう、優しい人間だと思いますか。",
            "あなた自身は、発想力に欠けた、平凡な人間だと思いますか。",
            "あなた自身は、他人に不満を持ち、揉め事を起こしやすいと思いますか。",
            "普段、AI技術(ChatGPTなど)に触れる頻度は高いですか。",
            "AI技術を積極的に活用したいと考えていますか。",
            "AIから提示された情報は有益だと思いましたか。"
        ]

        # アンケートの表示
        st.title("AIの意思決定支援についての評価アンケート")
        st.markdown("自分の意見に近いものをスライダーで選んでください。", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        # 初期位置を設定
        default_value = "どちらでもない"

        st.session_state.responses = []
        st.session_state.reasons = []
        for i, question in enumerate(questions):
            response = st.select_slider(
                f"Q. {i + 1} {question}",
                options=["全くそう思わない", "そう思わない", "あまりそう思わない", "どちらでもない", "ややそう思う", "そう思う", "非常にそう思う"],
                key=f"slider_q{i + 1}",
                value=default_value 
            )
            st.session_state.responses.append(response)
            if i < 10:
                text1_q1 = st.text_input(f"Q.{i+1} においてそのように回答した理由を教えてください(15文字以上)。", key=f"q{i+1}")
                st.session_state.reasons.append(text1_q1)
            st.markdown("<hr>", unsafe_allow_html=True)
        
        q_submitted = st.form_submit_button(label="回答を提出")

    if q_submitted:

        try:
            count = 0
            for i in range(len(st.session_state.reasons)):
                if len(st.session_state.reasons) < 10:
                    st.error("全ての理由に回答してください。")
                    break
                elif len(st.session_state.reasons[i]) < 15:
                    st.error("理由は15文字以上で回答してください。")
                    break
                elif not st.session_state.reasons[i].strip():
                    st.error("理由は15文字以上で回答してください。")
                    break
                else:
                    count += 1
        except:
            st.error("理由は15文字以上で回答してください。")
        if count == len(st.session_state.reasons):
            st.markdown("回答を提出しています。しばらくお待ちください......(10秒程度かかる場合があります)", unsafe_allow_html=True)
            max_retries=3
            retries = 0
            while retries <= max_retries:
                scopes = ['https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/drive']
                json_keyfile_dict = st.secrets["service_account"]
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    json_keyfile_dict, 
                    scopes
                )
                # gspread用に認証
                gc = gspread.authorize(credentials)
                try:
                    # スプレッドシートのIDを指定してワークブックを選択
                    workbook = gc.open_by_key(st.session_state.file['id'])
                    worksheet = workbook.sheet1

                    cell_list = worksheet.range(30, 1, 30, len(st.session_state.responses)+len(st.session_state.reasons)+1)
                    for i in range(len(st.session_state.responses)):
                        cell_list[i].value = st.session_state.responses[i]
                    for i in range(len(st.session_state.responses), len(st.session_state.responses)+len(st.session_state.reasons)):
                        cell_list[i].value = st.session_state.reasons[i-len(st.session_state.responses)]

                    # スプレッドシートを更新
                    worksheet.update_cells(cell_list)

                    st.session_state.questionnaire = True

                    st.success("回答を提出しました！")

                    retries += 5
                except Exception as e:
                    print(e)
                    f = drive.CreateFile({
                        'title': st.session_state.file_name + "_questionnaire",
                        'mimeType': 'application/vnd.google-apps.spreadsheet',
                        "parents": [{"id": st.secrets["folder_id"]}]
                    })
                    f.Upload()
                    st.session_state.file = f

                    if retries == max_retries:
                        st.error(f"申し訳ありませんが、提出がうまくいきませんでした。再度「回答を提出」ボタンを押してください。")

                # 再トライ準備
                retries += 1

    if st.session_state.questionnaire:
        st.markdown("これでアンケートは終了です。お疲れ様でした。<br>この度は、調査にご協力いただき誠にありがとうございました。", unsafe_allow_html=True)

        st.markdown("最後に、ランサーズのフォームに入力する合言葉を表示します。<br>こちらが正しくないと、謝礼をお支払いできませんので、お間違いないよう確実に入力してください。", unsafe_allow_html=True)

        st.markdown("合言葉："+st.session_state.file_name, unsafe_allow_html=True)

        st.markdown("では、ランサーズのフォームに戻って合言葉を入力してください。", unsafe_allow_html=True)

        #st.markdown("また、もし研究参加への同意を撤回される場合は、以下の同意撤回書をダウンロードしてください。", unsafe_allow_html=True)

        #st.download_button(
        #    label="同意撤回書をダウンロードする",
        #    data= "./disagreement.docx",
        #    file_name="同意撤回書.docx",
        #    mime="application/msword"
        #)
