from pathlib import Path
import json,glob,datetime,re
root=Path(__file__).resolve().parents[1]
events=[]
for p in glob.glob(r'C:\Users\Administrator\.codex\sessions\2026\11\05\*01a1ab85*.jsonl'):
    for l in open(p,encoding='utf-8'):
        o=json.loads(l);q=o.get('payload',{})
        if o['type']!='response_item' or q.get('type')!='message' or q.get('role') not in ('user','assistant'):continue
        if q.get('role')=='assistant' and q.get('channel') not in (None,'final','commentary'):continue
        s=''.join(c.get('text','') for c in q.get('content',[]) if c.get('type') in ('input_text','output_text'))
        if s.strip() and not s.startswith(('<environment_context>','<external_codex_apps_open_page>')):events.append((o['timestamp'],q['role'],s))
events=sorted(set(events))
answer=next(x for x in reversed(events) if x[1]=='user' and x[2].strip()=='全部同意')
question=next(x for x in reversed(events) if x[0]<answer[0] and x[1]=='assistant' and '这三项你是否同意' in x[2])
def when(ts):return datetime.datetime.fromisoformat(ts.replace('Z','+00:00')).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
p=root/'requirements.md';s=p.read_text(encoding='utf-8')
assert '校园卡认证人工审核（建议待确认）' in s,'本次确认已执行或目标版本不符'
s=s.replace('审核方式及认证状态细则为REQ-037中的待确认建议，不伪称已确认。','管理员核对姓名、学号和校园卡照片，驳回说明原因并允许修改重提；认证申请状态细则仍以REQ-037中的待确认说明为准。')
s=s.replace('具体注册登录方式见待确认的REQ-038。','通过本地账号密码注册登录，见REQ-038。')
s=s.replace('校园卡人工核验、本地注册登录及未定业务细节明确标为待确认，不冒充已确认。','采用校园卡人工核验及本地账号密码登录；尚未确定的文件限制、材料留存及找回等细节仍明确标为待确认。')
s=s.replace('校园卡认证人工审核（建议待确认）','校园卡认证人工审核').replace('本地账号注册登录（建议待确认）','本地账号注册登录')
for n in (1,37,38):
    pat=rf'(^## REQ-{n:03d} .*?^- 来源：)([^\n]+)'
    s=re.sub(pat,lambda m:m[1]+m[2]+'；INT-03-L002；INT-03-L003',s,count=1,flags=re.M|re.S)
for n in (37,38):
    pat=rf'(^## REQ-{n:03d} .*?^- 状态：)待确认'
    s=re.sub(pat,lambda m:m[1]+'已确认',s,count=1,flags=re.M|re.S)
s=s.replace('INT-03-L001（变更依据）；AI建议，具体细则待确认','INT-03-L001（变更依据）')
s=s.replace('建议由管理员核对姓名、学号与卡面信息。认证申请设未提交、待审核、已通过、已驳回四种状态；','由管理员核对姓名、学号与卡面信息。认证状态建议设未提交、待审核、已通过、已驳回四种（具体状态划分待确认）；')
s=s.replace('建议采用本地账号和密码注册登录，','采用本地账号和密码注册登录，')
s=s.replace('密码只保存带盐的安全哈希，不保存明文。','密码不得明文保存；采用带盐安全哈希的实现建议待后续设计确认。')
s=s.replace('待用户确认方式及细则后完善。','本地账号密码方式已确认，密码及找回细则确认后补齐对应边界验收。')
p.write_bytes(s.encode())
p=root/'chat.txt';c=p.read_text(encoding='utf-8');assert 'INT-03-L003' not in c
addition='\n### 校园卡认证配套方式确认\n\n'
for ident,(ts,role,t) in zip(('INT-03-L002','INT-03-L003'),(question,answer)):
    addition+=f'{ident} [{when(ts)}] [{"用户" if role=="user" else "AI"}]\n{t}\n\n'
c=c.replace('\n## AI 交互记录\n',addition+'\n## AI 交互记录\n',1)
cut=next(x[0] for x in reversed(events) if x[1]=='user' and '关于本校统一认证接口' in x[2])
addition='\n### 校园卡方案配套确认的后续交互（原文）\n\n'
for ts,role,t in events:
    if cut<ts<=answer[0]:addition+=f'#### {when(ts)} / {"用户" if role=="user" else "AI"}\n\n{t}\n\n'
addition+='### 本次AI修改说明\n\n将REQ-037、038的管理员人工核验、本地账号密码登录、照片权限主要目标更新为已确认；未将此前核对清单中的所有建议自动视为已确认，未代填人工审查。REQ-001保留已变更状态，REQ-035保留已拒绝，首次初稿标签不变。\n\n'
c=c.replace('\n## 人工审查记录\n',addition+'\n## 人工审查记录\n',1);p.write_bytes(c.encode())
p=root/'请你核对.md';g=p.read_text(encoding='utf-8')
g=g.replace('人工核验及本地登录建议见REQ-037、038，待本人确认。','人工核验、本地账号密码登录及照片仅本人和管理员可见已确认，见REQ-037、038。')
g=g.replace('待确认：管理员人工审核校园卡；本地账号密码登录；校园卡照片仅本人和管理员可见。','已确认：管理员人工审核校园卡；本地账号密码登录；校园卡照片仅本人和管理员可见。')
g=g.replace('1. 一个空的公开GitHub仓库地址。不要把密码或访问令牌发到聊天里。连接后由我尝试推送；若需账号登录，你在本机完成。','1. 公开仓库已经创建并推送：https://github.com/paulzrm/software-engineering-2026-lab1 ，此项已完成。')
g=g.replace('与未落实的仓库','')
p.write_bytes(g.encode())
print('Confirmed core card-review and local-login decisions; unrelated review items remain pending.')
