import os
import re
import shutil

# 設定：操作対象のHTMLファイル名
HTML_FILE = "index.html"

def add_character_to_html_v4():
    if not os.path.exists(HTML_FILE):
        print(f"エラー: {HTML_FILE} が見つかりません。同じフォルダにスクリプトを配置してください。")
        input("\nEnterキーを押して終了します...")
        return

    # 安全対策：実行前に自動バックアップを作成
    backup_file = HTML_FILE + ".bak"
    shutil.copy2(HTML_FILE, backup_file)

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    print("--- 星之翼 キャラクター管理外部ツール Part2 (インデント自動整列型) ---")
    
    # 1. 最初にコストを選択してもらう
    cost = input("最初に追加したいキャラクターのコストを入力してください (3.0, 2.5, 2.0): ").strip()
    if cost not in ["3.0", "2.5", "2.0"]:
        print("エラー: コストは 3.0, 2.5, 2.0 のいずれかで入力してください。")
        input("\nEnterキーを押して終了します...")
        return

    # 指定されたコストに応じた目印の作成
    start_marker = f"// --- COST {cost} START ---"
    end_marker = f"// --- COST {cost} END ---"

    # HTML内にコスト用の目印（範囲）があるかチェック
    if start_marker not in content or end_marker not in content:
        print(f"\nエラー: HTML内にコスト {cost} の目印（STARTまたはEND）が見つかりません。")
        print("index.html内に対象コストのコメントが正しく記述されているか確認してください。")
        input("\nEnterキーを押して終了します...")
        return

    # 2. 選択されたコストの「エリア内だけ」を抽出してIDを割り振る
    cost_section_pattern = f"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
    cost_section_match = re.search(cost_section_pattern, content, re.DOTALL)
    
    if not cost_section_match:
        print("エラー: コストエリアの抽出に失敗しました。")
        input("\nEnterキーを押して終了します...")
        return
        
    cost_section_text = cost_section_match.group(1)

    # そのコストエリア内だけで、登録されているID（cXXX）をスキャン
    ids_in_cost = re.findall(r"id:\s*['\"]c(\d+)['\"]", cost_section_text)
    
    if ids_in_cost:
        last_id_num = max(int(num) for num in ids_in_cost)
        next_id = f"c{str(last_id_num + 1).zfill(3)}"
    else:
        # 初回登録時の初期化
        if cost == "3.0": next_id = "c001"
        elif cost == "2.5": next_id = "c101"
        else: next_id = "c201"
        next_id = "c001" if not ids_in_cost else next_id

    print("-" * 40)
    print(f"★ コスト {cost} エリア内の最新状況をスキャンしました。")
    print(f"⇒ 次の自動割り当てID: {next_id}")
    print("-" * 40)

    # 3. IDが確定した後に、名前などの詳細を入力してもらう
    name = input("キャラクター名を入力してください: ").strip()
    if not name:
        print("名前が入力されなかったため、処理を中止しました。")
        input("\nEnterキーを押して終了します...")
        return

    kana = input("キャラクターのよみがな（ひらがな）を入力してください: ").strip()
    if not kana:
        print("よみがなが入力されなかったため、処理を中止しました。")
        input("\nEnterキーを押して終了します...")
        return

    try:
        has_rare_input = input("レア画像の枚数を入力してください (ない場合は 0): ").strip()
        has_rare = int(has_rare_input) if has_rare_input else 0
    except ValueError:
        print("無効な数値です。レア画像なし(0)として処理します。")
        has_rare = 0

    # 4. 【ここを修正】HTML側の「END目印」の直前にある空白（インデント）を正確に抽出する
    # 例: "    // --- COST 3.0 END ---" の左側のスペースを取得
    indent_pattern = f"^([ \\t]*){re.escape(end_marker)}"
    indent_match = re.search(indent_pattern, content, re.MULTILINE)
    
    if indent_match:
        current_indent = indent_match.group(1) # 元のHTMLと同じだけの空白を取得
    else:
        current_indent = "    " # 万が一取得できなかった場合のセーフティ（スペース4つ）

    # 5. 抽出したインデントを使って新しいキャラクターのテキスト行を作成
    new_line = f'{current_indent}{{ id: "{next_id}", name: "{name}", kana: "{kana}", cost: "{cost}", hasRare: {has_rare} }},'

    # 6. 「選択されたコストの終了目印」の直前に、綺麗にインデントを合わせて差し込む
    # 元のインデントを維持したEND目印の手前に改行を挟んで挿入します
    old_target = f"{current_indent}{end_marker}"
    new_target = f"{new_line}\n{current_indent}{end_marker}"
    
    updated_content = content.replace(old_target, new_target, 1)

    # 7. ファイルへの書き込み
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)
        
    print(f"\n成功: {HTML_FILE} の コスト {cost} エリアに「{name}」({next_id}) を追加しました！")
    print("★ 列（インデント）のズレも自動調整して綺麗に揃えました。")
    print(f"※ 安全のため実行直前のバックアップを '{backup_file}' として保存しています。")
    input("\nEnterキーを押して終了します...")

if __name__ == "__main__":
    add_character_to_html_v4()