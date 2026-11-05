from pathlib import Path
import glob,json,datetime,re,subprocess
R=Path(__file__).resolve().parents[1]
assert subprocess.run(['git','rev-parse','--verify','refs/tags/lab2-final'],cwd=R,capture_output=True).returncode!=0,'最终标签已存在，请勿重写'
events=[]
for path in glob.glob(r'C:\Users\Administrator\.codex\sessions\2026\11\05\*01a1ab85*.jsonl'):
 for line in open(path,encoding='utf-8'):
  o=json.loads(line);q=o.get('payload',{})
  if o['type']!='response_item' or q.get('type')!='message' or q.get('role') not in ('user','assistant'):continue
  if q.get('role')=='assistant' and q.get('channel') not in (None,'final','commentary'):continue
  t=''.join(x.get('text','') for x in q.get('content',[]) if x.get('type') in ('input_text','output_text'))
  if t.strip() and not t.startswith(('<environment_context>','<external_codex_apps_open_page>')):events.append((o['timestamp'],q['role'],t))
events=sorted(set(events));feedback=next(x for x in reversed(events) if x[1]=='user' and x[2].strip()=='全部保留')
def dt(t):return datetime.datetime.fromisoformat(t.replace('Z','+00:00')).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
review=f'''# 本人审查反馈及处理记录

- 反馈时间：{dt(feedback[0])}（北京时间，取自实际消息）
- 原始反馈：全部保留
- 对应初稿：lab2-ai-draft，d1f890b35664e0d3ed650203b9db1221e717e375。
- 核对对象：集中审查清单、31页报告和Figma设计。
- 处理：保留现有架构、领域模型及界面，更新报告为审查后版本，单独保存反馈驱动的文档提交。

## REVIEW-01 架构与并发

- 本人决定：保留模块化单体、PostgreSQL及行锁方案。
- 对应内容：报告第2、4、8、11页及设计说明。
- 实际修改：不改架构，更新报告决策状态与来源。

## REVIEW-02 领域模型与交易状态

- 本人决定：保留商品、购买意向、邀请与交易分离，保留旧邀请失效及单方确认后的限制。
- 对应内容：报告第6、10、19、20页，类图、状态图及预约/交易界面。
- 实际修改：图和业务流程不改；保留来源及审查结果。

## REVIEW-03 界面与权限

- 本人决定：保留全部现有界面，不新增界面调整。
- 对应内容：16个画板、报告第13至28页。
- 实际修改：不改图层或导出图；更新报告说明与最终包。

## 记录边界

以上分项是AI根据“全部保留”对清单三项的统一反馈整理，不冒充用户逐字给出的三段意见。用户未提供额外理由或具体改图指令，因此不编造个人论证或人工改图。此前布局、语义和权限显示修正仍归为AI自查，不能改记为人工修改。本人审查后保留与人工实质改图是不同事实，报告如实区分。
'''
(R/'AI记录/本人审查.md').write_bytes(review.encode())
raw=R/'AI记录/对话原文.md';s=raw.read_text(encoding='utf-8')
question=next(x for x in reversed(events) if x[0]<feedback[0] and x[1]=='assistant' and '实验二初稿已做好' in x[2])
for ts,role,t in (question,feedback):
 s+=f'\n## {dt(ts)} / {"用户" if role=="user" else "AI"}\n\n{t}\n'
raw.write_bytes(s.encode())
p=R/'AI记录/使用记录.md';s=p.read_text(encoding='utf-8');s='> 最终状态：本人已对集中清单反馈“全部保留”，见本人审查.md。以下保留初稿阶段的真实过程；其中“待本人审查”等说明属于当时状态。没有把AI自查转写成人工改图。\n\n'+s;p.write_bytes(s.encode())
p=R/'设计说明.md';s=p.read_text(encoding='utf-8').replace('（AI辅助设计初稿）','（审查后保留版）',1)
s=s.replace('本文件是设计建议，不修改实验一已固定标签。','本文件的架构、领域模型及界面已由本人反馈“全部保留”，不修改实验一已固定标签。',1)
s=s.replace('是本次AI提出的设计建议，尚需本人审核，不冒充已获本人确认。','最初由AI提出，本人已反馈全部保留；保留理由由AI整理，不冒充本人逐字论证。')
s=s.replace('## 本人待核对的三项设计判断','## 本人已反馈的三项设计判断（保留原清单）')
s=s.replace('这些问题不影响先交付可审查的图与界面，但在本人给出意见前，不填写“已完成人工修改”。','本人对上述清单统一回复“全部保留”，故不修改图与界面；详见AI记录/本人审查.md，不虚构人工改图。')
p.write_bytes(s.encode())
p=R/'本人审查清单.md';s=p.read_text(encoding='utf-8');s='> 已收到实际反馈：“全部保留”。三项均保留，具体记录见AI记录/本人审查.md。以下保留原清单用于追溯，不再要求重复确认。\n\n'+s;p.write_bytes(s.encode())
p=R/'tools/build_report.py';s=p.read_text(encoding='utf-8')
mapping={
'本版为AI辅助设计初稿，图、界面和报告已完成自动检查及AI自查，新增架构选择与人工审查记录仍待本人阅读确认。':'本版依据本人对集中清单的“全部保留”反馈定稿。架构、领域模型和界面保持不变，图、界面与报告已完成自动检查及AI自查；人工审查结果如实记录为保留，不编造人工改图。',
'该技术选择是本次AI提出的建议，待本人审查。':'该技术选择最初由AI提出，本人已在集中审查中决定保留。以下设计理由由AI整理，不冒充本人逐字给出的论证。',
'模块化单体、PostgreSQL、行锁和接口路径是新增设计建议，不冒充本人已经决定。':'模块化单体、PostgreSQL、行锁和接口路径最初是新增设计建议，本人已统一回复“全部保留”。没有补写本人未提供的额外论证。',
'架构仍待本人判断。':'本人审查后决定保留架构。',
'实验一中本人明确决定的业务范围已经作为基线，本实验的新增技术方案先由AI提出。当前发现与修正均属于AI自查，不能把渲染修复或自动检查写成本人已经作出的人工修改。需要本人对并发方案、模型分离和界面权限做实质判断后，再保存对应反馈和Git提交。':'实验一中本人明确决定的业务范围作为基线，实验二新增技术方案由AI提出。本人对集中清单反馈“全部保留”，因此保留架构、领域模型和界面。本次文档更新由这一真实反馈驱动；先前渲染修复、幂等顺序和权限标签校正仍属于AI自查，不改记为人工修改。',
'逐页检查PDF、对照需求与图文件，保留人工审查待完成状态及待确认事项。':'逐页检查PDF与打包内容；记录本人决定全部保留，并继续标明未定业务细节，不虚构额外修改。',
'本稿未伪造人工审查完成记录。下一步需要本人阅读后决定是否保留模块化单体和行锁、是否认可意向/邀请/交易分离，以及是否接受图中的私密材料访问边界。':'本人已对上述三项核对统一反馈“全部保留”。本版据此不改架构、模型或界面，更新审查和版本记录；用户未给出具体改图意见或额外理由，不代为编造。审查后保留与人工实质改图是不同事实，报告如实区分。',
'八、版本、待审查项与参考资料':'八、版本、本人审查结果与参考资料',
"('本人审查与人工修改','待本人反馈后提交','当前没有虚构该阶段；课程要求仍需完成。')":"('本人审查结果','原始反馈：全部保留；详见仓库AI记录/本人审查.md','保留架构、模型及界面；由反馈驱动更新报告，无人工实质改图。')",
'本人集中核对清单':'本人集中核对与实际反馈',
'本版为可审查初稿，收到本人反馈后再生成最终提交版。':'本版为审查后保留版，已重新核对图、源文件和压缩包内容；原始AI初稿由lab2-ai-draft保留。',
'AI辅助设计初稿':'审查后保留版',
}
for a,b in mapping.items():
 assert a in s,a
 s=s.replace(a,b)
# 历史核对问题仍作为审查对象保留，补充真实结果。
needle="h('本人集中核对与实际反馈')"
s=s.replace(needle,needle+"\np('以下是当时提交本人核对的三项问题。本人实际回复为“全部保留”，未提供另外的理由和界面改动。',small)")
review_source=subprocess.check_output(['git','rev-parse','3b0a1a6'],cwd=R,text=True).strip()
s=s.replace('3b0a1a6（完整号可由Git解析）',review_source)
p.write_bytes(s.encode())
p=R/'README.md';s=p.read_text(encoding='utf-8');s=s.replace('当前为可审查初稿：','当前为本人反馈“全部保留”后的定稿：',1)
s=s.replace('集中核对三项设计判断。','保留原清单及实际反馈；结果为全部保留。')
s=s.replace('后续本人的实际反馈另行记录，不能把AI修改写成本人修改。','本人实际反馈见AI记录/本人审查.md，结果为全部保留；不能把AI修改写成本人修改。')
s=s.replace('初稿压缩包在仓库根目录的','最终压缩包在仓库根目录的').replace('收到本人审查意见后再生成最终提交版。','已收到本人保留意见并重建最终包，原始初稿固定在lab2-ai-draft。')
p.write_bytes(s.encode())
print('Recorded exact keep-all feedback and updated report status without inventing edits.')
