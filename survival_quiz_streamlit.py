import streamlit as st
import datetime
import csv

questions = [
    {
        "section_title": "ステージ1：侵入の兆候",
        "question_text": "【任務1】都市の防御システムを起動せよ！\n次のうち、セキュリティ対象として正しいものをすべて選べ。",
        "choices": [
            ("端末（あなたの手元にある防衛装置）", True),
            ("ソフトウェア（都市の防御を支えるプログラム群）", True),
            ("オンラインアカウント（敵が狙うデジタルの鍵）", True),
        ],
        "answer_type": "multiple",
        "score_correct": 0,
        "score_incorrect": -20,
        "feedback_correct": "✅ 防御システムが作動！都市のセキュリティレベルを維持しました。",
        "feedback_incorrect": "❌ 防御に失敗…都市の一部が侵害されました。−20点。"
    }
]

def main():
    st.title("サバイバルクイズ")
    user_id = st.text_input("研修IDを入力してください")
    score = 100
    answers = []

    if user_id:
        for idx, q in enumerate(questions):
            st.subheader(q["section_title"])
            st.write(q["question_text"])
            selected = []
            for i, (choice, _) in enumerate(q["choices"]):
                if st.checkbox(choice, key=f"{idx}_{i}"):
                    selected.append(choice)
            if st.button(f"回答する（問{idx+1}）", key=f"btn_{idx}"):
                correct = [c[0] for c in q["choices"] if c[1]]
                if set(selected) == set(correct):
                    st.success(q["feedback_correct"])
                    score += q["score_correct"]
                else:
                    st.error(q["feedback_incorrect"])
                    score += q["score_incorrect"]
                st.info(f"現在のスコア: {score}")
                answers.append(", ".join(selected))
                if score <= 0:
                    st.warning("ゲームオーバー！")
                    break

        # 結果保存
        if st.button("結果を保存"):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            output_header = ["タイムスタンプ", "スコア"] + [f"問{i+1}の回答" for i in range(len(answers))] + ["研修ID"]
            output_row = [timestamp, score] + answers + [user_id]
            with open("quiz_result.csv", "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(output_header)
                writer.writerow(output_row)
            st.success("結果をquiz_result.csvに保存しました。")

main()
