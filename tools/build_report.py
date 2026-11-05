from pathlib import Path
import subprocess,zipfile,json,hashlib
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from pypdf import PdfReader

r=Path(__file__).resolve().parents[1]
git=lambda *a:subprocess.check_output(['git',*a],cwd=r)
draft=git('rev-parse','lab1-ai-draft').decode().strip()
final=git('rev-parse','lab1-final').decode().strip()
assert draft=='325d606d2e2bc7ff82a2f67329f19c0ad4b1316d'
for name in ('requirements.md','chat.txt'):assert (r/name).read_bytes()==git('show','lab1-final:'+name)
pdfmetrics.registerFont(TTFont('Song',r'C:\Windows\Fonts\simsun.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('Hei',r'C:\Windows\Fonts\simhei.ttf'))
body=ParagraphStyle('body',fontName='Song',fontSize=10.5,leading=17,spaceAfter=7,wordWrap='CJK')
small=ParagraphStyle('small',parent=body,fontSize=9,leading=14,spaceAfter=3)
title=ParagraphStyle('title',fontName='Hei',fontSize=20,leading=28,spaceAfter=12)
head=ParagraphStyle('head',fontName='Hei',fontSize=13,leading=20,spaceBefore=10,spaceAfter=7)
sub=ParagraphStyle('sub',parent=head,fontSize=11,leading=16)
story=[]
def p(t,style=body):story.append(Paragraph(escape(t),style))
def h(t):p(t,head)
def table(headers,rows,widths):
 data=[[Paragraph(escape(x),small) for x in headers]]+[[Paragraph(escape(x),small) for x in row] for row in rows]
 t=Table(data,colWidths=[x*mm for x in widths],repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf1f5')),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#bac4cc')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
 story.append(t);story.append(Spacer(1,7))
def new():story.append(PageBreak())

p('实验一：需求分析报告',title)
p('项目2：校内二手交易系统',head)
p('姓名：张瑞珉　　学号：241220002　　日期：2026年11月5日')
h('一、项目概况')
p('校内二手交易经常依赖群消息，商品信息容易被刷走，商品是否售出、是否有人预约也不够清楚。本项目希望集中展示商品，并管理预约、线下交易结果与信用记录，减少重复沟通和交易冲突。')
p('本实验只做需求分析，不编写完整系统。第一版面向本校学生，账号可以同时买卖。采用本地账号密码登录，填写姓名、学号并上传校园卡照片，由管理员核验；通过后才可发布、预约及参与公众投票。一个学号只关联一个已认证账号，重新申请不能清空信用或处罚。')
h('系统范围与明确不实现的内容')
p('范围包括商品草稿与审核、发布和修改、多条件查询、预约与唯一锁定、取消和双向完成确认、信用处罚与答题恢复、举报申诉、严重案件匿名投票、统计和操作日志。')
p('不做在线支付、物流、实时聊天、图片内容自动识别和公开案件评论，也不接入学校统一身份认证接口。预约留言用于协商，交易在线下完成；成交总额仅统计锁定标价，不表示平台收款。')
table(['用户类型','主要权限'],[
('买家（普通账号的购买角色）','浏览搜索、预约、接受邀请、取消、确认完成、举报与申诉。'),
('卖家（普通账号的出售角色）','管理本人商品、选择预约者、提出截止时间、取消及确认完成。'),
('管理员','认证人工核验、审核复核、违规与争议处理、账号限制、发起匿名评议及查询日志。')],[49,123])
p('未认证用户仅可浏览公开商品，不能发布、预约和投票。受限账号不能开展新交易，但仍可处理已有交易、提交证据和申诉。',small)

new();h('二、整体业务流程')
p('1. 注册及认证：用户注册本地账号并提交姓名、学号和校园卡照片；管理员核对，通过后绑定学号和信用身份。认证照片不公开，仅本人和管理员可见。')
p('2. 发布商品：卖家保存草稿后提交。系统检查字段完整性、价格、文字禁售词及图片实际格式，通过后发布；失败给出原因，检查服务异常时保持待审核。存在异议可申请人工复核。')
p('3. 预约和锁定：多人可对同一商品表达购买意向。卖家选择一人并提出截止时间，买家在截止前接受后才锁定，同时结束其他预约并保存标价。卖家改选后旧邀请失效。')
p('4. 交易结束：双方线下交易并分别确认，双方都确认才完成。无人确认时到期自动解锁且不直接扣分；若已有一方确认，则继续锁定，有争议由管理员裁决。')
p('5. 违规处理：当事人可提交照片和说明。普通违规由管理员核实；严重案件可以先公开脱敏摘要并投票72小时，投票仅供参考，管理员最终作出有理由的决定。')
h('主要数据及关联')
table(['数据','关联与约束'],[
('账号与认证申请','账号关联认证申请、姓名、学号及私密照片；同一学号最多一个认证通过账号。'),
('商品与浏览事件','商品关联卖家、分类、图片、价格及状态；最近7天登录浏览按账号去重，卖家自己和匿名浏览不计。'),
('预约、邀请与交易','预约关联买家和商品；同人同商品最多一条有效预约。交易保存买卖双方、商品、截止时间和锁定标价；同商品最多一条有效锁定交易。'),
('信用事件与答题','关联账号和交易，保存取消、爽约、合并处罚、更正及恢复事件；同人同日最多提交一次答题。'),
('举报、投票与日志','举报关联对象、双方及私密证据；每案每人一票。日志关联操作者、时间、对象、动作和结果。')],[41,131])
p('商品、预约和交易不能分别任意修改。接受邀请、取消、超时、完成等操作必须一起更新相关状态；信用变更必须有对应事件，不得只改最终分数。',small)

new();h('三、业务状态与转换')
table(['业务对象','允许的主要转换','禁止或限制'],[
('商品','草稿→待审核；待审核→可预约或驳回；驳回→待审核；可预约→锁定或下架；锁定→已售出或恢复可预约。','未审核不得公开；锁定时禁止直接修改或下架；已售出不得恢复出售，须新建商品。'),
('商品修改与违规','已发布商品修改→待审核；主动下架→重新提交审核；违规下架须管理员解除处置后才能重提。','审核中暂停公开展示与预约；管理员下架锁定商品时必须联动处理交易。'),
('预约与交易','有效意向→选中邀请→接受后锁定；锁定→取消、超时结束、单方确认；单方确认→双向完成或争议裁决。','旧邀请、过期邀请不可接受；其他预约在锁定时结束且解锁后不自动恢复。'),
('完成与争议','无人确认时到期释放；单方确认后保持锁定；管理员裁决为完成或解除锁定。','单方确认后禁止直接取消或自动到期释放；不能用公众投票直接完成交易或处罚。'),
('学生认证','未提交→待审核；待审核→已通过或已驳回；驳回→修改后重提。','用户不能自行标为通过；待审核和驳回不能取得交易权限。')],[29,75,68])
h('并发与异常处理')
p('同时接受邀请时，系统检查当前邀请、商品及截止时间，同一商品最多一人锁定成功。旧页面发起修改、预约或确认时重新校验，不能依赖页面上显示的旧状态。重复预约返回已有结果，重复取消、完成和扣分只产生一次效果。')
p('卖家主动取消与买家主动取消按操作者分别记次。下架含有效预约的商品时使预约和邀请失效；违规下架锁定商品，无人确认时结束交易且不自动扣分，已有单方确认时转入争议处理。')
p('保存中断不得留下部分更新。后续实现至少进行100批、每批20请求的并发与冲突测试，覆盖接受、改选、取消、到期、确认和下架，并检查重启后已成功数据仍存在。')

new();h('四、信用规则与质量要求')
table(['事项','确定的口径'],[
('主动取消','滚动最近7天内，锁定后主动取消第1、2次免扣，第3次起扣2、4、8、16、32分，之后每次最多32分；锁定前说明原因正常取消不计入。'),
('投诉核实爽约','按认定时间统计滚动最近30天次数，首次免扣，第2次起扣2、4、8、16、32分，此后每次最多32分；单纯超时不等于爽约。'),
('处罚合并与更正','同笔同用户最多一次取消及一次爽约认定，取较高处罚，后来只补差额。撤销误判后按时间及事件ID重放受影响历史，保留答题事件与更正记录；自然移出窗口不返分。'),
('等级和恢复','100优秀，95～99良好，80～94一般，60～79较差，0～59差。每日随机5题、最多提交一次，全对加1分，最高100分；低分不自动禁止交易，恢复不解除处罚。')],[35,137])
table(['质量维度','条件及通过标准'],[
('性能','1万件商品、100并发用户，参考4核8GiB环境；查询:预约=8:2，预热1分钟后持续10分钟。两类成功业务响应各自P95≤2秒，非预期错误为0；图片上传不计。'),
('安全','逐项检查角色权限和直接接口调用；全部越权用例拒绝。私密证据及校园卡图片不能经公开地址绕过权限，密码与凭据不得明文保存。'),
('可靠性','并发与重复提交不产生多锁定、重复处罚或部分更新；服务重启保留已成功数据。每日备份，保留最近7份，隔离恢复最近有效备份并在30分钟内核验完成。'),
('可追踪性','保存关键操作及更正日志，支持用户、时间、操作类型组合查询，普通用户不可修改删除；最低保存至2027-02-28，这是约定期限而非课程公布日期。')],[29,143])
p('以上均为后续实现阶段的验收计划。本次完成了需求文本结构、来源、版本及提交包一致性检查，没有实现系统，也没有实际运行上述性能、安全或并发测试。',small)

new();h('五、实验总结')
p('本次讨论先从商品列表、搜索和预约开始，再追问信用处罚、审核及交易冲突。比较困难的是把锁定、短期反复爽约等说法变成可以判断的规则。例如，预约只是意向，只有卖家选定、买家接受后才锁定；不同阶段的取消需要区分处理。')
p('信用规则也经历了补充。取消和经核实的线下爽约采用不同时间窗口，同一交易不能重复处罚；更正误判时还需要保留之后的答题恢复，因此最终用可重放的事件记录说明计算顺序。')
p('人工核对重点包括三个方面：一是发现统一认证接入太重，改为姓名、学号及校园卡人工核验，同时纠正关联需求；二是补齐信用更正的计算顺序；三是明确发布数和成交统计的口径。本人提出变更并确认核对项，AI据实际反馈整理REV记录，没有把AI建议直接写成本人已完成的审查。')
p('AI适合把分散对话转成编号需求，提醒状态、权限和异常的遗漏，但仍可能写错关联编号，或者留下统计口径不清的问题。完整保留首次结果和后续修改，才能看出最终要求是如何确定的。本次交流由AI参与，记录保留真实来源，不将其署名为实际队友。课程要求的互访形式仍应由本人核实。')
h('保留的待确认事项')
p('校园卡照片具体留存期限、身份更正和找回所需证明、密码复杂度及找回流程尚无明确决定，需求中继续标明待确认。这些内容不得在后续实现时自行宣称已得到甲方确认。校园卡人工核验也不能保证完全杜绝冒用身份。')
h('六、版本信息')
p('公开仓库：https://github.com/paulzrm/software-engineering-2026-lab1',small)
p('lab1-ai-draft（首次完整AI初稿）：',small);p(draft,small)
p('lab1-final（需求文本与记录定稿）：',small);p(final,small)
p('最终列表共38个固定编号，其中36条状态为已确认（功能需求31条、非功能需求4条、约束1条），另有已变更1条、已拒绝1条。REQ-001保留已变更以追踪认证替换，REQ-035保留已拒绝，不计入已确认数量。',small)
p('两个标签已固定，报告在其后生成。压缩包中的requirements.md和chat.txt直接从lab1-final导出并逐字节比对；报告及工具的后续提交不改变标签。',small)

def footer(c,d):
 c.setStrokeColor(colors.HexColor('#bac4cc'));c.line(19*mm,17*mm,191*mm,17*mm)
 c.setFont('Song',8);c.drawString(19*mm,12*mm,'软件工程2026秋 / 实验一 / 张瑞珉 241220002');c.drawRightString(191*mm,12*mm,f'{d.page}')
pdf=r/'report.pdf'
doc=SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=19*mm,leftMargin=19*mm,topMargin=17*mm,bottomMargin=22*mm,title='实验一需求分析：校内二手交易系统',author='张瑞珉')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
reader=PdfReader(pdf);assert len(reader.pages)==5,len(reader.pages)
text='\n'.join(p.extract_text() or '' for p in reader.pages)
assert draft in text and final in text and '241220002' in text
folder=r/'output'/'实验1_241220002_张瑞珉';folder.mkdir(parents=True,exist_ok=True)
for name in ('requirements.md','chat.txt'):(folder/name).write_bytes(git('show','lab1-final:'+name))
(folder/'report.pdf').write_bytes(pdf.read_bytes())
zpath=r/'output'/'实验1_241220002_张瑞珉.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
 for name in ('report.pdf','requirements.md','chat.txt'):z.write(folder/name,folder.name+'/'+name)
with zipfile.ZipFile(zpath) as z:
 assert len(z.namelist())==3
 for name in ('requirements.md','chat.txt'):assert z.read(folder.name+'/'+name)==git('show','lab1-final:'+name)
print(json.dumps({'pdf_pages':len(reader.pages),'pdf_bytes':pdf.stat().st_size,'zip':str(zpath),'zip_bytes':zpath.stat().st_size,'final_commit':final,'checks':'5 pages, identity and full commit hashes present; exact tagged text in 3-file ZIP'},ensure_ascii=False,indent=2))
