from pathlib import Path
import re, subprocess, hashlib, json
root=Path(__file__).resolve().parents[1]
req=(root/'requirements.md').read_bytes()
chat=(root/'chat.txt').read_bytes()
s=req.decode(); c=chat.decode()
ids=re.findall(r'^## (REQ-\d{3}) ',s,re.M)
assert ids==[f'REQ-{i:03d}' for i in range(1,len(ids)+1)]
fields=['类型','来源','优先级','状态','需求描述','前置条件','正常结果','异常或边界情况','验收方法','关联需求']
for block in re.split(r'^## REQ-\d{3} ',s,flags=re.M)[1:]:
    assert re.findall(r'^- ([^：\n]+)：',block,re.M)==fields
    for x in re.findall(r'REQ-\d{3}',block): assert x in ids, x
    for x in re.findall(r'INT-\d{2}-L\d{3}',block): assert re.search(r'^'+x+r' ',c,re.M),x
initial=subprocess.check_output(['git','show','lab1-ai-draft:requirements.md'],cwd=root).decode()
initial_chat=subprocess.check_output(['git','show','lab1-ai-draft:chat.txt'],cwd=root).decode()
assert '```markdown\n'+initial+'```' in c
assert '```markdown\n'+initial+'```' in initial_chat
assert subprocess.check_output(['git','rev-parse','lab1-ai-draft'],cwd=root,text=True).strip()=='325d606d2e2bc7ff82a2f67329f19c0ad4b1316d'
print(json.dumps({'requirements':len(ids),'functional':s.count('- 类型：功能需求'),'nonfunctional':s.count('- 类型：非功能需求'),'confirmed':s.count('- 状态：已确认'),'changed':s.count('- 状态：已变更'),'rejected':s.count('- 状态：已拒绝'),'pending':s.count('- 状态：待确认'),'draft_sha':subprocess.check_output(['git','rev-parse','lab1-ai-draft'],cwd=root,text=True).strip(),'checks':'IDs, fields, source references, preserved first output and immutable initial tag all pass'},ensure_ascii=False,indent=2))
