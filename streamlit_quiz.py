import streamlit as st
import json
import datetime
import csv
import os

def load_quiz_data(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        quiz_data = json.load(f)
    parsed_quiz = []
    for stage in quiz_data:
        section_title = stage.get("section_title", "")
        section_story = stage.get("section_story", "")
        questions = stage.get("questions", [])
        for question in questions:
            parsed_quiz.append({
                "section_title": section_title,
                "section_story": section_story,
                "question_text": question.get("question_text", ""),
                "choices": question.get("choices", []),
                "answer_type": question.get("answer_type", "multiple"),
                "score_correct": question.get("score_correct", 0),
                "score_incorrect": question.get("score_incorrect", 0),
                "feedback_correct": question.get("feedback_correct", ""),
                "feedback_incorrect": question.get("feedback_incorrect", "")
            })
    return parsed_quiz

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

def main():
    # 管理者用ダウンロード画面
    if st.query_params.get("admin", ["0"])[0] == "1":
        show_admin_download()
        return

    st.title("サイバーセキュリティ サバイバルクイズ")
    user_id = st.query_params.get("user_id", [""])[0]
    if not user_id:
        user_id = st.text_input("研修IDを入力してください")
    if not user_id:
        st.warning("研修IDが必要です")
        return

    quiz = load_quiz_data("quiz_data.json")
    if "score" not in st.session_state:
        st.session_state["score"] = 100
    if "answers" not in st.session_state:
        st.session_state["answers"] = []
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
    current_q = st.session_state["current_q"]
    game_over = st.session_state["game_over"]
    answered = st.session_state["answered"]
    last_feedback = st.session_state["last_feedback"]
    last_selected = st.session_state["last_selected"]
    result_saved = st.session_state["result_saved"]

    if game_over:
        st.warning("ゲームオーバー！")
        st.info(f"最終スコア: {score}")
        if not result_saved:
            save_result(score, answers, user_id)
            st.session_state["result_saved"] = True
            st.success("結果をquiz_result.csvに保存しました。")
    elif current_q < len(quiz):
        q = quiz[current_q]
        st.subheader(q["section_title"])
        st.write(q["section_story"])
        st.write(q["question_text"])
        # チェックボックス形式で選択肢を表示
        selected = []
        for choice in q["choices"]:
            if st.checkbox(choice["text"], value=(choice["text"] in last_selected if answered else False), key=f"chk_{current_q}_{choice['text']}"):
                selected.append(choice["text"])
        if not answered:
            if st.button(f"回答する（問{current_q+1}）", key=f"btn_{current_q}"):
                correct = [c["text"] for c in q["choices"] if c["is_correct"]]
                if set(selected) == set(correct) and selected:
                    st.session_state["last_feedback"] = q["feedback_correct"]
                    score += q["score_correct"]
                else:
                    st.session_state["last_feedback"] = q["feedback_incorrect"]
                    score += q["score_incorrect"]
                st.session_state["score"] = score
                answers.append(", ".join(selected))
                st.session_state["answers"] = answers
                st.session_state["answered"] = True
                st.session_state["last_selected"] = selected
                if score <= 0:
                    st.session_state["game_over"] = True
                st.rerun()
        else:
            st.write(st.session_state["last_feedback"])
            st.info(f"現在のスコア: {score}")
            if st.button("次へ"):
                st.session_state["current_q"] = current_q + 1
                st.session_state["answered"] = False
                st.session_state["last_feedback"] = ""
                st.session_state["last_selected"] = []
                st.rerun()
    else:
        st.success("クリア！全問終了しました。")
        st.info(f"最終スコア: {score}")
        if not result_saved:
            save_result(score, answers, user_id)
            st.session_state["result_saved"] = True
            st.success("結果をquiz_result.csvに保存しました。")

main()

### 実行イメージ (ローカル)
### python -m streamlit run streamlit_quiz.py <データファイル>
