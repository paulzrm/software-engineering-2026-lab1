from pathlib import Path
import json, glob, re, datetime
root=Path(__file__).resolve().parents[1]
events=[]
for p in glob.glob(r'C:\Users\Administrator\.codex\sessions\2026\11\05\*01a1ab85*.jsonl'):
    for line in open(p,encoding='utf-8'):
        o=json.loads(line);q=o.get('payload',{})
        if o['type']!='response_item' or q.get('type')!='message' or q.get('role') not in ('user','assistant'):continue
        if q.get('role')=='assistant' and q.get('channel') not in (None,'final','commentary'):continue
        s=''.join(x.get('text','') for x in q.get('content',[]) if x.get('type') in ('input_text','output_text'))
        if not s.strip() or s.startswith(('<environment_context>','<external_codex_apps_open_page>')):continue
        events.append((o['timestamp'],q['role'],s))
events=sorted(set(events))
event=next(x for x in reversed(events) if x[1]=='user' and '关于本校统一认证接口' in x[2])
when=datetime.datetime.fromisoformat(event[0].replace('Z','+00:00')).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
p=root/'requirements.md';s=p.read_text(encoding='utf-8')
assert '## REQ-037' not in s,'变更已执行，禁止重复追加'
s=s.replace('（AI首次完整初稿）','（审查与变更工作版本）',1)
s=s.replace('本版尚未经本人逐条人工审查。','首次完整初稿已保存在 lab1-ai-draft；本版已按补充沟通修改，尚未经本人逐条人工审查。',1)
s=s.replace('完整原文和时间见 chat.txt。','INT-03 为初稿固定后的需求变更；完整原文和时间见 chat.txt。',1)
def replace_req(n,name,typ,status,desc,pre,normal,edge,test,rel):
    global s
    block=f'## REQ-{n:03d} {name}\n\n- 类型：{typ}\n- 来源：INT-03-L001；COURSE-02；COURSE-G\n- 优先级：高\n- 状态：{status}\n- 需求描述：{desc}\n- 前置条件：{pre}\n- 正常结果：{normal}\n- 异常或边界情况：{edge}\n- 验收方法：{test}\n- 关联需求：{rel}\n\n'
    s=re.sub(rf'^## REQ-{n:03d} .*?(?=^## REQ-|\Z)',lambda _:block,s,flags=re.M|re.S)
replace_req(1,'姓名学号与校园卡认证','功能需求','已变更','不再对接学校统一身份认证。用户填写本校姓名、学号并上传校园卡照片申请学生身份认证；认证通过后以本校学号绑定账号及信用，买卖为同一账号的两种业务角色。','用户已有本地账号；具体注册登录方式见待确认的REQ-038。','形成与账号关联的认证申请，认证通过后获得发布、预约等已认证用户权限。','仅填写姓名学号不算认证成功；照片上传不代表已核实本人。审核方式及认证状态细则为REQ-037中的待确认建议，不伪称已确认。','检查认证申请包含姓名、学号、校园卡照片及账号关联；认证前后权限须符合REQ-002，审核细则确认后补齐验收。','REQ-002、REQ-003、REQ-037、REQ-038')
replace_req(35,'学校统一身份认证接口接入（不再采用）','约束','已拒绝','原学校统一身份认证接口方案因接入成本被用户撤回，改用姓名、学号及校园卡照片认证。保留本编号追踪变更，不再要求学校接口授权、联调或认证故障降级测试。','已确认INT-03-L001的方案变更。','学校接口不再是本项目外部依赖，不作为验收前置条件。','历史对话及lab1-ai-draft中仍保留原方案，不回写、不删除原记录。','检查当前范围及认证需求不再将学校接口作为依赖；历史标签内容不变。','REQ-001、REQ-037、REQ-038')
s=s.replace('信用及处罚关联稳定学校身份。','信用及处罚关联本校学号对应的已认证身份。')
s=s.replace('学校身份变更的核实材料及注销保留期限待后续确认。','姓名或学号更正、账号找回的核实材料及注销保留期限待确认；不得用重复照片或新账号绕过同学号唯一约束。')
s=s.replace('普通用户可浏览、买卖、举报、申诉和按条件参与投票；','未认证用户可浏览公开商品，不能发布、预约和参与投票；认证通过的普通用户可买卖、举报、申诉和按条件参与投票；')
s=s.replace('不得明文保存密码或认证凭据，本系统不收集学校密码；','不得明文保存密码或认证凭据，本系统不收集学校密码；校园卡照片及认证表单按私密材料隔离，学校认证已改为校园卡申请；')
s=s.replace('外部学校认证接入条件待确认；未知业务细节明确列出，不冒充已确认。','不接入学校统一身份认证；校园卡人工核验、本地注册登录及未定业务细节明确标为待确认，不冒充已确认。')
for n in (2,3,31,36):
    s=re.sub(rf'(^## REQ-{n:03d} .*?^- 来源：)([^\n]+)',lambda m:m[1]+m[2]+'；INT-03-L001',s,flags=re.M|re.S,count=1)
for n,name,desc,pre,normal,edge,test,rel in [
    (37,'校园卡认证人工审核（建议待确认）','建议由管理员核对姓名、学号与卡面信息。认证申请设未提交、待审核、已通过、已驳回四种状态；驳回须给出理由，用户更正后可重提。照片只允许申请者和管理员查看，不进入公开资料或公众投票。','用户提交认证材料。','只有审核通过才赋予已认证权限；同学号最多一个通过认证的账号。','同一学号并发通过时最多一份成功；重复提交不重复审批；资料不清或不一致时驳回。校园卡持有证明、照片留存期限及文件限制尚待确认；该方案不能保证杜绝冒用。','分别提交匹配、不匹配、模糊、重复学号材料，验证通过、驳回、重提、并发及证据越权保护；这些为确认后的计划，非已实施测试。','REQ-001、REQ-002、REQ-003、REQ-031'),
    (38,'本地账号注册登录（建议待确认）','建议采用本地账号和密码注册登录，登录后提交校园卡认证；仅姓名与学号不能作为登录凭据。密码只保存带盐的安全哈希，不保存明文。','用户选择本地注册或登录。','注册产生未认证账号；登录后可查看认证进度，审核通过后开放交易权限。','账号名唯一；未通过认证不能交易。密码规则、找回方式和认证材料更正流程待确认，不默认为已获用户授权的业务决定。','核对注册、正确和错误密码登录、重复账号、认证前后权限及密码持久化；待用户确认方式及细则后完善。','REQ-001、REQ-002、REQ-031')]:
    s+=f'## REQ-{n:03d} {name}\n\n- 类型：功能需求\n- 来源：INT-03-L001（变更依据）；AI建议，具体细则待确认\n- 优先级：高\n- 状态：待确认\n- 需求描述：{desc}\n- 前置条件：{pre}\n- 正常结果：{normal}\n- 异常或边界情况：{edge}\n- 验收方法：{test}\n- 关联需求：{rel}\n\n'
p.write_bytes(s.encode())
chat=root/'chat.txt';c=chat.read_text(encoding='utf-8')
c=c.replace('\n## AI 交互记录\n',f'\n### 初稿固定后的认证方案变更\n\nINT-03-L001 [{when}] [用户] {event[2]}\n\n## AI 交互记录\n',1)
cut=next(x[0] for x in events if x[1]=='user' and '行，那你完整的去做' in x[2])
append='\n### 首次初稿后的后续交互（原文）\n\n'
for ts,role,t in events:
    if ts<=cut:continue
    time=datetime.datetime.fromisoformat(ts.replace('Z','+00:00')).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
    append+=f'#### {time} / {"用户" if role=="user" else "AI"}\n\n{t}\n\n'
append+='### 本次AI修改说明\n\n依据INT-03-L001修改REQ-001、002、003、031、035、036，追加待确认建议REQ-037、038；撤销学校接口依赖，保留初稿原文及标签。人工审核与本地密码登录尚未得到用户确认，未填写为人工审查结果。本次完整修改可通过Git提交差异复核。\n\n'
c=c.replace('\n## 人工审查记录\n',append+'\n## 人工审查记录\n',1)
chat.write_bytes(c.encode())
guide=root/'请你核对.md';g=guide.read_text(encoding='utf-8')
g=g.replace('# 你需要完成的核对','# 你需要完成的核对\n\n更新：用户已撤回学校统一认证，改为姓名、学号和校园卡照片认证。REQ-001已变更，REQ-035保留为已拒绝；人工核验及本地登录建议见REQ-037、038，待本人确认。原学校接口条目不再适用。',1)
g=g.replace('改为 REQ-002、REQ-035，正确关联学校认证依赖','已随方案变更调整为REQ-002、REQ-003、REQ-037、REQ-038；请核对关联与新方案一致')
g=g.replace('学校身份变更时仅接受学校认证服务可验证的身份对应材料，经管理员核实换绑；无有效证明不换绑。','姓名、学号更正或账号找回须管理员重新核对身份材料，具体证明方式尚待确认。')
g=re.sub(r'\| 11 \| REQ-035 \|.*?\|','| 11 | REQ-035、037、038 | 学校接口方案已撤回。待确认：管理员人工审核校园卡；本地账号密码登录；校园卡照片仅本人和管理员可见。照片文件限制、留存期限及账号找回方式仍待确认。 |',g)
guide.write_bytes(g.encode())
print('Updated identity requirements and appended original conversation; draft tag untouched.')
