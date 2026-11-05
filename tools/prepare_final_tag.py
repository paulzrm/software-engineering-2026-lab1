from pathlib import Path
import subprocess
r=Path(__file__).resolve().parents[1]
p=r/'requirements.md';s=p.read_text(encoding='utf-8').replace('逐项检查事件账和分数；未定计算顺序单独待确认。','按上述确定的计算顺序逐项检查事件账和分数。').replace('尚未确定的文件限制、材料留存及找回等细节','尚未确定的材料留存及找回等细节')
p.write_bytes(s.encode())
# AI最终输出记录应与本次细节校正保持一致，首次完整初稿保持原样。
p=r/'chat.txt';s=p.read_text(encoding='utf-8');anchor=s.index('### 最终修改说明及完整结果')
s=s[:anchor]+s[anchor:].replace('逐项检查事件账和分数；未定计算顺序单独待确认。','按上述确定的计算顺序逐项检查事件账和分数。').replace('尚未确定的文件限制、材料留存及找回等细节','尚未确定的材料留存及找回等细节')
p.write_bytes(s.encode())
