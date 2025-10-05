import streamlit as st
import json
import datetime
import csv
import os

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

def get_rank(score):
    if score == 100:
        return "マスター"
    elif score >= 80:
        return "上級者"
    elif score >= 60:
        return "中級者"
    elif score >= 40:
        return "初級者"
    elif score >= 20:
        return "初心者"
    else:
        return "入門者"

def get_rank_emoji(rank):
    if rank == "マスター":
        return "🏆"
    elif rank == "上級者":
        return "🥈"
    elif rank == "中級者":
        return "🥉"
    elif rank == "初級者":
        return "🌱"
    elif rank == "初心者":
        return "🔰"
    else:  # 入門者
        return "🚩"

def main():
    quiz_file = "quiz_data_v4.json"
    banner_file = "cyber_banner.jpg"
    quiz_data = load_quiz_data(quiz_file)

    st.title("サイバー衛生レベルアップクイズ")
    st.markdown("入門者からスタートし、正解するごとにレベルアップ！目指せマスター！")
    st.image(banner_file, width="stretch")

    user_id = st.text_input("研修IDを入力してください")
    if not user_id:
        st.warning("研修IDが必要です")
        return

    if "score" not in st.session_state:
        st.session_state["score"] = 0
    if "answers" not in st.session_state:
        st.session_state["answers"] = []
    if "current_q" not in st.session_state:
        st.session_state["current_q"] = 0
    if "answered" not in st.session_state:
        st.session_state["answered"] = False
    if "last_feedback" not in st.session_state:
        st.session_state["last_feedback"] = ""
    if "last_selected" not in st.session_state:
        st.session_state["last_selected"] = []
    if "last_judgement" not in st.session_state:
        st.session_state["last_judgement"] = ""
    if "last_correct" not in st.session_state:
        st.session_state["last_correct"] = []
    if "result_saved" not in st.session_state:
        st.session_state["result_saved"] = False
    if "previous_rank" not in st.session_state:
        st.session_state["previous_rank"] = get_rank(0)

    score = st.session_state["score"]
    answers = st.session_state["answers"]
    current_q = st.session_state["current_q"]
    answered = st.session_state["answered"]
    last_feedback = st.session_state["last_feedback"]
    last_selected = st.session_state["last_selected"]
    result_saved = st.session_state["result_saved"]

    questions = quiz_data.get("questions", [])
    if current_q >= len(questions):
        rank = get_rank(score)
        st.markdown(f"**あなたのランク：{rank}**")
        st.markdown(f"**最終スコア：{score}点**")
        if score == 100:
            st.markdown("""
<div style='background:#ffd700;color:#222;padding:24px;border-radius:16px;text-align:center;font-size:2em;'>
🎉 <b>おめでとうございます！</b> 🎉<br>
🎉 <b>マスター認定です！</b> 🎉<br>
サイバー衛生スコア：<b>100</b><br>
修了証をお送りします<br>                        
</div>
""", unsafe_allow_html=True)
        else:
            rank = get_rank(score)
            emoji = get_rank_emoji(rank)
            st.markdown(f"スコア：{score}点　ランク：{rank} {emoji}")
            st.warning("再チャレンジして、マスターを目指しましょう！")
            if st.button("再チャレンジ"):
                st.session_state.clear()
                st.session_state["current_q"] = 0
                st.session_state["answered"] = False
                st.session_state["last_feedback"] = ""
                st.session_state["last_selected"] = []
                st.session_state["last_judgement"] = ""
                st.session_state["last_correct"] = []
                st.rerun()

        if not result_saved:
            save_result(score, answers, user_id)
            st.session_state["result_saved"] = True

        st.markdown("---")
        st.markdown("📋 **事後アンケートにご協力ください**")
        st.markdown("アンケートページ（ダミー）")
        return

    q = questions[current_q]
    st.subheader(q.get("section_title", f"第{current_q+1}問"))
    question_text = q.get("question_text", "")
    if isinstance(question_text, list):
        for line in question_text:
            st.markdown(line)
    else:
        st.markdown(question_text)

    selected = []
    for choice in q.get("choices", []):
        if st.checkbox(
            choice["text"],
            value=(choice["text"] in last_selected if answered else False),
            key=f"chk_{current_q}_{choice['text']}"
        ):
            selected.append(choice["text"])

    if not answered:
        if st.button("回答する", key=f"btn_{current_q}"):
            correct = [c["text"] for c in q.get("choices", []) if c.get("is_correct")]
            if set(selected) == set(correct) and selected:
                st.session_state["last_judgement"] = "**✅ 正解！**"
                st.session_state["last_feedback"] = q.get("feedback_correct", "")
                score += q.get("score_correct", 20)
            else:
                st.session_state["last_judgement"] = "**❌ 不正解**"
                st.session_state["last_feedback"] = q.get("feedback_incorrect", "")
                score += q.get("score_incorrect", 0)
            st.session_state["last_correct"] = correct
            st.session_state["score"] = score
            answers.append(", ".join(selected))
            st.session_state["answers"] = answers
            st.session_state["answered"] = True
            st.session_state["last_selected"] = selected
            st.rerun()

    if answered:
        st.markdown('---')
        st.markdown(st.session_state.get("last_judgement", ""))
        correct_choices = st.session_state.get("last_correct", [])
        if correct_choices:
            correct_str = "」「".join(correct_choices)
            st.markdown(f'正解は「{correct_str}」です。')
        feedback = st.session_state["last_feedback"]
        if isinstance(feedback, list):
            for line in feedback:
                st.markdown(line)
        else:
            st.markdown(feedback)
        current_rank = get_rank(score)
        if current_rank != st.session_state["previous_rank"]:
            st.markdown(f"スコア：{score}点　ランク：{current_rank} 🎉（ランクアップ）")
        else:
            st.markdown(f"スコア：{score}点　ランク：{current_rank}")
        st.session_state["previous_rank"] = current_rank

        if st.button("次へ"):
            st.session_state["current_q"] = current_q + 1
            st.session_state["answered"] = False
            st.session_state["last_feedback"] = ""
            st.session_state["last_selected"] = []
            st.session_state["last_judgement"] = ""
            st.session_state["last_correct"] = []
            st.rerun()

if __name__ == "__main__":
    main()