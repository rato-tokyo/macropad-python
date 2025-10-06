# 引き継ぎドキュメント - MacroPad Python CLI

## プロジェクト概要

中国製マクロキーパッド（3ボタン 1ノブタイプ）をPython CLIで設定するツール。
元のC#プロジェクト https://github.com/rOzzy1987/MacroPad のPython移植版。

**リポジトリ:** https://github.com/rato-tokyo/macropad-python

## 対象デバイス

- **型番:** 3 buttons 1 knob macro keypad
- **VID:PID:** 0x1189:0x8890 (4489:34960)
- **プロトコル:** Legacy Protocol (version 0)
- **特徴:**
  - 3個のボタン + 1個のロータリーエンコーダー（押し込み可能）
  - 合計6つのアクション（button_1, button_2, button_3, knob_1_cw, knob_1_ccw, knob_1_press）
  - 1レイヤーのみ
  - 最大5キーシーケンス（ただし修飾キーは最初のキーのみ）

## 開発環境と実行環境

- **開発環境:** Linux Mint (開発者: tomo)
- **実行環境:** Windows 11 (ユーザー: tomos)
- **Python:** 3.7+
- **依存ライブラリ:** hidapi

## 現在の実装状況

### ✅ 完成した機能

1. **HID通信層** (`macropad/hid_interface.py`)
   - デバイス検出・接続
   - クロスプラットフォーム対応（Windows/Linux）
   - パスフラグメント検索（大文字小文字の違いに対応）

2. **プロトコル実装** (`macropad/protocol.py`)
   - Legacy Protocol (version 0) の実装
   - キーシーケンス、メディアキー、マウスボタン、LED制御のレポート生成

3. **デバイスAPI** (`macropad/device.py`)
   - 高レベルAPI（set_key_sequence, set_media_key, set_mouse_button, set_led_mode）

4. **CLI** (`cli.py`)
   - list: デバイス一覧表示
   - set-key: キーボードショートカット設定
   - set-media: メディアキー設定
   - set-mouse: マウスボタン設定
   - set-led: LEDモード設定

5. **デバッグツール**
   - `debug_devices.py`: 全HIDデバイスを列挙
   - `test_write.py`: 書き込み動作テスト

### ❌ 未解決の問題

#### **重要: デバイスへの設定書き込みが機能していない**

**症状:**
- `python cli.py set-mouse button_1 left` を実行しても、ボタン1を押しても左クリックされない
- デバイスの設定が変更前のまま（変更が反映されていない）

**調査結果（Windows環境）:**

1. **デバイス検出:** ✅ 成功
   - VID:PID 1189:8890 を正しく検出
   - MI_01 インターフェースを選択

2. **HID書き込み:** ✅ 成功（見かけ上）
   - `device.write()` は例外を投げずに完了
   - 戻り値は `-1`（Windowsの特性）
   - `test_write.py` の実行結果:
     ```
     ✓ Write successful: -1 bytes written
     ```

3. **設定反映:** ❌ 失敗
   - 実際にボタンを押しても動作が変わらない
   - デバイスのフラッシュメモリに書き込まれていない可能性

**推測される原因:**

1. **レポートフォーマットの問題**
   - Legacy Protocolの実装が正しくない可能性
   - バイト順、データ構造が元のC#実装と異なる？

2. **インターフェース選択の問題**
   - MI_01が正しいインターフェースではない可能性
   - 元のC#コードでは `config.txt` で `mi_01` を指定しているが、実際にはどのインターフェースを使うべきか不明

3. **レポートID の問題**
   - Protocol 0 では report_id = 0 を使用
   - Windowsでは異なる扱いが必要？

4. **書き込みシーケンスの問題**
   - 複数レポートの送信順序や間隔（delay）が必要？
   - 元のC#コードを詳しく確認する必要がある

## 元のC#実装の重要なファイル

### `/home/tomo/git/MacroPad` (フォーク済み)

1. **設定ファイル:**
   - `src/RSoft.MacroPad/config.txt`: デバイス定義
     ```
     4489:34960,mi_01,0
     ```

2. **プロトコル実装:**
   - `src/RSoft.MacroPad.BLL/Infrasturture/Protocol/Legacy/KeyFunctionReport.cs`
   - `src/RSoft.MacroPad.BLL/Infrasturture/Protocol/Legacy/MouseFunctionReport.cs`
   - `src/RSoft.MacroPad.BLL/Infrasturture/Protocol/Legacy/WriteFlashReport.cs`

3. **HID通信:**
   - `src/RSoft.MacroPad.BLL/HID/Hid.cs`
   - `src/RSoft.MacroPad.BLL/Infrasturture/UsbDevice/HidUsb.cs`

## 次にやるべきこと（優先順）

### 1. プロトコル実装の検証

**タスク:** C#のレポート生成コードとPython実装を詳細に比較

- [ ] `KeyFunctionReport.cs` の `Create()` メソッドを精読
- [ ] `MouseFunctionReport.cs` の `Create()` メソッドを精読
- [ ] `WriteFlashReport.cs` の `Create()` メソッドを精読
- [ ] Python実装 (`macropad/protocol.py`) と比較し、バイト配列が完全一致するか確認

**重要ファイル:**
- `/home/tomo/git/MacroPad/src/RSoft.MacroPad.BLL/Infrasturture/Protocol/Legacy/KeyFunctionReport.cs`
- `/home/tomo/git/macropad-python/macropad/protocol.py`

### 2. HID書き込みの詳細確認

**タスク:** 実際に送信されているバイト列をログ出力して確認

- [ ] `hid_interface.py` の `write_report()` に詳細ログを追加
- [ ] 送信バッファの全バイトをHEXダンプ
- [ ] C#版と同じデータが送られているか確認

### 3. インターフェース選択の検証

**タスク:** 正しいHIDインターフェースを使用しているか確認

現在検出されているインターフェース（Windows）:
```
Interface 0: MI_00 (KBD)
Interface 1: MI_01       ← 現在使用中
Interface 2: MI_02 (2つ)
Interface 3: MI_03
```

- [ ] MI_01 以外のインターフェースでも試す
- [ ] 元のC#コードがどのように選択しているか確認
- [ ] `config.txt` の `mi_01` が本当に Interface 1 を指すか検証

### 4. レポートシーケンスの確認

**タスク:** 送信するレポートの順序・タイミングを検証

Legacy Protocolでは複数レポートを送信:
1. (Layer selection - report_id != 0の場合のみ)
2. Key/Mouse/Media function report(s)
3. Write flash report

- [ ] 各レポート間にdelayが必要か確認
- [ ] WriteFlashReportの実装が正しいか確認（`protocol.py:41-45`）

### 5. Windowsでの動作確認ツール作成

**タスク:** より詳細なデバッグ情報を出力するスクリプト

- [ ] 送信前後のデバイス状態を確認
- [ ] 各レポート送信後にデバイスからの応答を読み取る（可能なら）
- [ ] C#版のログ出力機能を参考にする

## ファイル構成

```
macropad-python/
├── macropad/
│   ├── __init__.py
│   ├── models.py           # Enum定義（KeyCode, Modifier等）
│   ├── hid_interface.py    # HID通信層
│   ├── protocol.py         # Legacy Protocol実装 ⚠️ 要確認
│   └── device.py           # 高レベルAPI
├── cli.py                  # CLIエントリーポイント
├── debug_devices.py        # デバイス列挙ツール
├── test_write.py           # 書き込みテストツール
├── requirements.txt        # hidapi
├── README.md
├── HANDOFF.md             # このファイル
└── .gitignore
```

## 重要な実装箇所

### `macropad/protocol.py`

#### `LegacyProtocol.create_mouse_reports()` (行 120-154)

現在の実装:
```python
def create_mouse_reports(
    self,
    action: InputAction,
    layer: int,
    button: MouseButton,
    modifiers: Modifier
) -> List[Report]:
    reports = []

    if self.report_id != 0:
        reports.append(self.create_layer_selection_report(layer))

    report = Report(self.report_id)
    report.data[0] = action.value
    report.data[1] = KeyType.MULTIMEDIA
    if self.report_id != 0:
        report.data[1] |= (layer << 4) & 0xFF

    # Mouse button encoding
    if button in (MouseButton.LEFT, MouseButton.RIGHT, MouseButton.MIDDLE):
        report.data[2] = button.value
        report.data[3] = 0
    else:  # Scroll
        report.data[2] = 0
        report.data[3] = button.value

    report.data[4] = int(modifiers)

    reports.append(report)
    reports.append(self.create_write_flash_report())

    return reports
```

**⚠️ 要確認:** この実装が元のC#と一致するか詳細検証が必要

### `macropad/hid_interface.py`

#### `write_report()` (行 111-143)

現在の実装:
```python
def write_report(self, report_id: int, data: bytes) -> bool:
    if not self.device:
        logger.error("Device not opened")
        return False

    buffer = bytearray(self.output_report_length)
    buffer[0] = report_id

    data_len = min(len(data), 64)
    buffer[1:data_len+1] = data[:data_len]

    try:
        bytes_written = self.device.write(bytes(buffer))
        logger.debug(f"Wrote {bytes_written} bytes to device")
        return True  # ⚠️ -1でもTrueを返すが、実際には設定が反映されていない
    except Exception as e:
        logger.error(f"Failed to write to device: {e}")
        return False
```

## 検証用コマンド

### デバイス検出確認
```bash
python cli.py list
python debug_devices.py
```

### 書き込みテスト
```bash
python test_write.py
```

### 設定コマンド（現在動作せず）
```bash
python cli.py set-mouse button_1 left
python cli.py set-key button_1 "F1"
python cli.py -v set-media button_1 play_pause
```

## 参考情報

### C#プロジェクトのキーファイル

1. **MouseFunctionReport.cs** (要精読)
   - パス: `/home/tomo/git/MacroPad/src/RSoft.MacroPad.BLL/Infrasturture/Protocol/Legacy/MouseFunctionReport.cs`

2. **KeyFunctionReport.cs** (要精読)
   - パス: `/home/tomo/git/MacroPad/src/RSoft.MacroPad.BLL/Infrasturture/Protocol/Legacy/KeyFunctionReport.cs`

3. **WriteFlashReport.cs** (要精読)
   - パス: `/home/tomo/git/MacroPad/src/RSoft.MacroPad.BLL/Infrasturture/Protocol/Legacy/WriteFlashReport.cs`

4. **HidUsb.cs** (HID書き込み実装)
   - パス: `/home/tomo/git/MacroPad/src/RSoft.MacroPad.BLL/Infrasturture/UsbDevice/HidUsb.cs`

### 既知の制限（デバイス仕様）

- 1レイヤーのみサポート
- 最大5キーシーケンス
- 修飾キーは最初のキーのみに適用される
- LEDモード: OFF, ON, BREATHE（色なし）
- マウス修飾キー: 左側のみサポート

## 連絡事項

- Linux Mint環境（開発環境）には実機デバイスがないため、実際の動作確認はWindows環境でのみ可能
- Windows環境（実行環境）で直接デバッグ・修正を進める方が効率的
- 元のC#プロジェクトは `/home/tomo/git/MacroPad` にクローン済み（要分析）

## Windows環境での作業開始方法

```powershell
# リポジトリクローン（既に済んでいる場合はスキップ）
git clone https://github.com/rato-tokyo/macropad-python.git
cd macropad-python

# 依存関係インストール
pip install -r requirements.txt

# 現状確認
python debug_devices.py
python test_write.py
python cli.py list
```

## 推奨アプローチ

1. **C#コードの詳細分析**
   - 特に `MouseFunctionReport.Create()` と `KeyFunctionReport.Create()` の実装を逐一確認
   - 生成されるバイト配列を手動で計算し、Python実装と比較

2. **バイトレベルでのログ比較**
   - Python版で送信する全バイトをHEXダンプ
   - C#版（元のソフトウェア）のログと比較

3. **インターフェース別テスト**
   - MI_00, MI_01, MI_02, MI_03 のそれぞれで書き込みテスト

---

**最終更新:** 2025-10-07
**作成者:** Claude Code (Linux環境)
**次の担当:** Claude Code (Windows環境)
