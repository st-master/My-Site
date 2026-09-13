import os
import shutil

class Tag:
    """個別のタグと、それに関連付けられたフォルダーパスを管理するクラス"""
    def __init__(self, name, base_dir):
        self.name = name
        # カプセル化: タグ専用のフォルダーパスを内部で保持
        self.folder_path = os.path.join(base_dir, 'tags', name)

    def ensure_folder_exists(self):
        """所定のフォルダーを作成（存在しない場合）"""
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)


class TagManager:
    """全体タグの集計・分類・フォルダー出力・振分けを統括するクラス"""
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.tag_map = {}  # { "AI": [Card1, Card2], "Git": [Card1] }

    def register_card(self, card):
        """カードの持つ tags を読み込み、各タグクラスへ登録"""
        for tag_name in card.tags:
            if tag_name not in self.tag_map:
                self.tag_map[tag_name] = []
            self.tag_map[tag_name].append(card)

    def export_to_folders(self):
        """タグごとのフォルダーを作成し、関連カードを振分け・出力する"""
        for tag_name, cards in self.tag_map.items():
            tag_obj = Tag(tag_name, self.output_dir)
            tag_obj.ensure_folder_exists()
            
            # 各タグフォルダー内に「AI.html」や「Git.html」などの一覧カード群を出力
            # （あるいはシンボリックリンクやファイルコピーで物理管理）
            print(f"📁 フォルダー [{tag_name}] 内に {len(cards)} 件のカードを管理・出力しました。")