import streamlit as st
import json
import datetime
import csv
import os
import sys

def load_quiz_data(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        quiz_data = json.load(f)
    return quiz_data

def save_result(score, answers, user_id):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_header = ["タイムスタンプ", "スコア"] + [f"問{i+1}の回答" for i in range(len(answers))] + ["研修ID"]
    output_row = [timestamp, score] + answers + [user_id]
    file_exists = os.path.exists("quiz_result.csv")
    with open("quiz_result.csv", "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(output_header)
        writer.writerow(output_row)

def show_admin_download():
    st.title("管理者用ダウンロード画面")
    if os.path.exists("quiz_result.csv"):
        with open("quiz_result.csv", "rb") as f:
            st.download_button(
                label="結果CSVをダウンロード",
                data=f,
                file_name="quiz_result.csv",
                mime="text/csv"
            )
    else:
        st.info("結果ファイルがまだありません。")

def show_lines(x, style="markdown"):
    if isinstance(x, list):
        for line in x:
            if style == "title":
                st.title(line)
            elif style == "subheader":
                st.subheader(line)
            elif style == "header":
                st.header(line)
            else:
                st.markdown(line)
    elif isinstance(x, str):
        if style == "title":
            st.title(x)
        elif style == "subheader":
            st.subheader(x)
        elif style == "header":
            st.header(x)
        else:
            st.markdown(x)

def main():
    # コマンドライン引数からデータファイル名を取得
    # if len(sys.argv) > 1:
    #     quiz_file = sys.argv[1]
    # else:
    #     st.error("クイズデータファイル（JSON）を引数で指定してください。\n例: streamlit run streamlit_quiz_v2.py quiz_data_v2_array.json")
    #     return
    quiz_file = "quiz_data_v2.json"

    # 管理者用ダウンロード画面
    if st.query_params.get("admin", ["0"])[0] == "1":
        show_admin_download()
        return

    quiz_data = load_quiz_data(quiz_file)
    title = quiz_data.get("title", "クイズタイトル未設定")
    if isinstance(title, list):
        if len(title) > 0:
            st.title(title[0])
        if len(title) > 1:
            st.subheader(title[1])
        for line in title[2:]:
            st.markdown(f"**{line}**")
    else:
        st.title(title)

    user_id = st.query_params.get("user_id", [""])[0]
    if not user_id:
        user_id = st.text_input("研修IDを入力してください")
        if not user_id:
            st.warning("研修IDが必要です")
            return

    # セッション管理
    if "score" not in st.session_state:
        st.session_state["score"] = 100
    if "answers" not in st.session_state:
        st.session_state["answers"] = []
    if "current_stage" not in st.session_state:
        st.session_state["current_stage"] = 0  # 0: イントロダクション
    if "current_q" not in st.session_state:
        st.session_state["current_q"] = 0
    if "game_over" not in st.session_state:
        st.session_state["game_over"] = False
    if "answered" not in st.session_state:
        st.session_state["answered"] = False
    if "last_feedback" not in st.session_state:
        st.session_state["last_feedback"] = ""
    if "last_selected" not in st.session_state:
        st.session_state["last_selected"] = []
    if "result_saved" not in st.session_state:
        st.session_state["result_saved"] = False

    score = st.session_state["score"]
    answers = st.session_state["answers"]
    current_stage = st.session_state["current_stage"]
    current_q = st.session_state["current_q"]
    game_over = st.session_state["game_over"]
    answered = st.session_state["answered"]
    last_feedback = st.session_state["last_feedback"]
    last_selected = st.session_state["last_selected"]
    result_saved = st.session_state["result_saved"]

    stages = quiz_data.get("stages", [])

    # エンディング・ゲームオーバーのインデックス
    ending_index = None
    gameover_index = None
    for i, s in enumerate(stages):
        if isinstance(s.get("section_title", ""), list):
            title_str = "".join(s.get("section_title", ""))
        else:
            title_str = s.get("section_title", "")
        if "エンディング" in title_str:
            ending_index = i
        if "ゲームオーバー" in title_str:
            gameover_index = i

    # ゲームオーバー時はゲームオーバーステージへジャンプ
    if score <= 0 and gameover_index is not None and current_stage != gameover_index:
        st.session_state["current_stage"] = gameover_index
        st.session_state["current_q"] = 0
        st.session_state["game_over"] = True
        st.rerun()

    # 全ステージ終了時はエンディングへジャンプ
    if current_stage >= len(stages):
        if ending_index is not None:
            st.session_state["current_stage"] = ending_index
            st.session_state["current_q"] = 0
            st.rerun()
        else:
            st.success("クリア！全問終了しました。")
            st.info(f"最終スコア: {score}")
            if not result_saved:
                save_result(score, answers, user_id)
                st.session_state["result_saved"] = True
                st.success("結果をquiz_result.csvに保存しました。")
            return

    # 現在のステージ・問題
    stage = stages[current_stage]
    questions = stage.get("questions", [])

    # イントロ・エンディング・ゲームオーバー（questionsが空のステージ）
    if len(questions) == 0:
        show_lines(stage.get("section_title", ""), style="header")
        show_lines(stage.get("section_story", ""))
        
        if current_stage == ending_index or current_stage == gameover_index:
            if score == 100:
                # クリア時のお祝い演出
                st.markdown("""
                <div style='background:#ffd700;color:#222;padding:24px;border-radius:16px;text-align:center;font-size:2em;'>
                🎉 <b>MISSION COMPLETE!</b> 🎉<br>
                シールドポイント：<b>100</b>
                </div>
                """, unsafe_allow_html=True)
                st.success("パーフェクトクリア！あなたのサイバー衛生力は最高レベルです！")
                if not result_saved:
                    save_result(score, answers, user_id)
                    st.session_state["result_saved"] = True
                st.success("結果をquiz_result.csvに保存しました。")
                if st.button("終了"):
                    st.session_state.clear()
                    st.rerun()
                return
            else:
                # ゲームオーバー時の演出（例2）
                st.markdown(f"""
                <div style='background:#222;color:#fff;padding:24px;border-radius:16px;text-align:center;font-size:2em;'>
                💥 <b>GAME OVER</b> 💥<br>
                シールドポイント：<b>{score}</b>
                </div>
                """, unsafe_allow_html=True)
                st.warning("もう一度チャレンジして、サイバー衛生力を高めましょう！")
                if not result_saved:
                    save_result(score, answers, user_id)
                    st.session_state["result_saved"] = True
                st.success("結果をquiz_result.csvに保存しました。")
                # 再挑戦ボタン
                if st.button("再挑戦"):
                    st.session_state.clear()
                    st.rerun()
                return
        else:
            if st.button("スタート"):
                st.session_state["current_stage"] = current_stage + 1
                st.session_state["current_q"] = 0
                st.rerun()
            return

    if current_q == 0:
        show_lines(stage.get("section_title", ""), style="subheader")
        show_lines(stage.get("section_story", ""))

    if current_q < len(questions):
        q = questions[current_q]
        show_lines(q.get("question_text", ""))
        # チェックボックス形式で選択肢を表示
        selected = []
        for choice in q.get("choices", []):
            if st.checkbox(
                choice["text"],
                value=(choice["text"] in last_selected if answered else False),
                key=f"chk_{current_stage}_{current_q}_{choice['text']}"
            ):
                selected.append(choice["text"])

        if not answered:
            if st.button("回答する", key=f"btn_{current_stage}_{current_q}"):
                correct = [c["text"] for c in q.get("choices", []) if c.get("is_correct")]
                if set(selected) == set(correct) and selected:
                    st.session_state["last_feedback"] = q.get("feedback_correct", "")
                    score += q.get("score_correct", 0)
                else:
                    st.session_state["last_feedback"] = q.get("feedback_incorrect", "")
                    score += q.get("score_incorrect", -20)
                st.session_state["score"] = score
                answers.append(", ".join(selected))
                st.session_state["answers"] = answers
                st.session_state["answered"] = True
                st.session_state["last_selected"] = selected
                if score <= 0:
                    st.session_state["game_over"] = True
                st.rerun()
        else:
            show_lines(st.session_state["last_feedback"])
            if score == 100:
                st.success(f"🟢 シールドMAX！ポイント：{score}")
            elif score >= 70:
                st.info(f"🔵 まだまだ戦える！ポイント：{score}")
            elif score >= 30:
                st.warning(f"🟠 シールドが危ない！ポイント：{score}")
            else:
                st.error(f"🔴 シールドブレイク寸前！ポイント：{score}")

            if st.button("次へ"):
                if current_q + 1 < len(questions):
                    st.session_state["current_q"] = current_q + 1
                else:
                    st.session_state["current_stage"] = current_stage + 1
                    st.session_state["current_q"] = 0
                st.session_state["answered"] = False
                st.session_state["last_feedback"] = ""
                st.session_state["last_selected"] = []
                st.rerun()

if __name__ == "__main__":
    main()