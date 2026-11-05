from pathlib import Path
from xml.sax.saxutils import escape
import json,subprocess,zipfile,hashlib
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
from pypdf import PdfReader

R=Path(__file__).resolve().parents[1]
pdfmetrics.registerFont(TTFont('Song',r'C:\Windows\Fonts\simsun.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('Hei',r'C:\Windows\Fonts\simhei.ttf'))
body=ParagraphStyle('body',fontName='Song',fontSize=10.5,leading=17,spaceAfter=8,wordWrap='CJK')
small=ParagraphStyle('small',parent=body,fontSize=9,leading=13.5,spaceAfter=4)
heading=ParagraphStyle('heading',fontName='Hei',fontSize=18,leading=25,spaceAfter=11)
subheading=ParagraphStyle('subheading',fontName='Hei',fontSize=12,leading=18,spaceBefore=6,spaceAfter=7)
title=ParagraphStyle('title',fontName='Hei',fontSize=29,leading=42,spaceAfter=12)
story=[];toc=[]
def p(s,st=body):story.append(Paragraph(escape(s),st))
def h(s):p(s,subheading)
def new(s):
 if story:story.append(PageBreak())
 p(s,heading);toc.append(s)
def table(headers,rows,widths,style=small):
 data=[[Paragraph(escape(x),style) for x in headers]]+[[Paragraph(escape(x),style) for x in row] for row in rows]
 t=Table(data,colWidths=[w*mm for w in widths],repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8F0E9')),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#B6C8BE')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(t);story.append(Spacer(1,8))
def img(path,maxw=260*mm,maxh=145*mm):
 with PILImage.open(path) as im:w,h=im.size
 k=min(maxw/w,maxh/h);story.append(Image(str(path),w*k,h*k,hAlign='CENTER'));story.append(Spacer(1,5))

new('一、项目与主要功能')
p('拾集：校内二手交易系统',title)
p('软件工程2026秋 · 实验二：软件设计与建模',subheading)
p('姓名：张瑞珉　学号：241220002　日期：2026年11月5日')
p('设计依据：实验一lab1-final需求，项目2。本版为AI辅助设计初稿，图、界面和报告已完成自动检查及AI自查，新增架构选择与人工审查记录仍待本人阅读确认。')
p('目标是把校内闲置商品发布、多人购买意向、卖家选择、唯一锁定和线下交易结果统一起来。买卖双方使用同一账号，通过姓名、学号及校园卡照片人工认证；信用、举报和操作记录为交易提供可追溯依据。')
table(['功能模块','主要功能','对应需求'],[
('账号与学生认证','本地账号密码、校园卡人工核验、学号唯一、权限控制','REQ-001—003、037、038'),
('商品与审核','草稿、自动审核、复核、发布修改、下架、组合查询与排序','REQ-004—010'),
('预约与交易','多人意向、当前邀请、接受后锁定、取消、到期、双方完成与争议','REQ-011—019'),
('信用与答题','取消与爽约计罚、合并与更正、等级展示、每日答题恢复','REQ-020—024'),
('举报与评议','举证、匿名投票、管理员裁决、账号限制与申诉','REQ-025—028'),
('日志与统计','关键操作查询、发布数、完成数和锁定标价汇总','REQ-029、030')],[39,160,61])
p('范围不包含在线支付、物流、实时聊天、图片内容自动识别和学校统一身份认证。当前是设计，不是已经运行的业务软件。',small)

new('二、架构选择与面向对象设计')
p('建议采用模块化单体，按界面入口、应用服务、领域对象和持久化适配器分层。六个业务模块保持边界，在同一进程和数据库内协作。后续实验规模较小，优先保证跨商品、预约、交易和信用的事务一致性，比拆成多个独立服务更容易实现和验证。该技术选择是本次AI提出的建议，待本人审查。')
table(['层或对象','职责与设计理由'],[
('HTTP入口 / 会话与权限','读取当前用户，校验角色、所有权和认证状态，解析幂等键；UI禁用按钮仅是提示，不能代替后端校验。'),
('应用服务','TradeService编排接受、取消和确认；CreditService组织策略和事件重放；一个用例中的关联写入在同一事务完成。'),
('领域实体','Product约束商品生命周期；Reservation代表意向；Invitation代表当前选择及截止时间；Trade保存锁定价格、双方确认和交易状态。'),
('策略与接口','PenaltyPolicy区分7天取消和30天爽约策略；Repository隔离SQL和存储，实现不应散落在UI或每个实体中。'),
('买家与卖家','是同一User的业务角色，不作为互斥子类。用户可以同时买卖，管理员通过授权角色管理系统。'),
('信用与治理','CreditEvent是可追溯事实，CreditAccount是当前投影；投票仅形成参考信息，不能直接调用封禁或扣分。')],[47,213])
h('模块交互')
p('交易模块调用账号模块检查认证及限制，主动取消时调用信用模块。治理模块裁决争议并通知交易和信用模块；商品违规下架也要联动交易状态。查询模块只读受权限过滤的数据，定时任务调用同样的到期服务，不绕过业务规则直接改商品字段。')
h('沿用的本人业务判断与新设计建议')
p('实验一中本人提出了搜索与热度、信用翻倍扣分、答题恢复、举报评议，并把统一身份认证改为校园卡人工核验。本实验在这些已确认判断上展开；模块化单体、PostgreSQL、行锁和接口路径是新增设计建议，不冒充本人已经决定。')

new('三、数据存储、关联与约束')
p('结构化信息建议存PostgreSQL，图片存对象存储并以media_asset_id关联。金额用定点数，业务时间保存UTC；展示和每日答题按北京时间计算。以下是设计层面的表划分，不要求本实验建库。')
table(['表或数据组','关联与保存内容','不能重复或同步要求'],[
('用户、角色、认证','账号、密码哈希、状态、学号、校园卡引用及审核结果','账号名唯一；同学号最多一个认证通过账号；换号不清空信用。'),
('商品、分类、图片','卖家、类别、描述、价格、首次发布时间、状态和版本','草稿不公开；修改重审；图片有所有者、真实格式及访问范围。'),
('预约、邀请、留言','买家和商品，邀请截止时间，双方文字协商','同人同商品一条有效意向；每商品一个当前邀请，改选使旧邀请失效。'),
('交易','商品、双方、邀请、锁定标价、截止时间、双方确认','同商品最多一条有效锁定交易；允许保留多笔历史交易。'),
('信用、事件、答题','用户、交易、事件来源、认定/取消时间、恢复和更正','同源事件不重复；每人北京时间每日最多一次答题提交。'),
('举报、证据、申诉、票','关联商品/交易/账号、双方、私密材料、脱敏摘要及决定','同人同事项不重复举报；每案每人一票；申诉次数及截止在事务中校验。'),
('浏览、日志、幂等请求','浏览人和时间；动作、对象、结果；请求键、摘要及响应','窗口内按人去重；幂等键按用户/动作/键唯一，同键不同参数拒绝。')],[47,106,107])
p('校园卡和原始证据只能由提交者及管理员读取；另一方仅看必要脱敏摘要。公开商品图和私密证据分开控制，不能把长期公开图片地址交给投票页。',small)
p('图片先暂存再随业务提交绑定引用，业务失败产生的孤立暂存文件由任务清理。备份要一起核验数据库和媒体引用，不能只恢复表而丢失所需文件。',small)

new('四、核心事务与异常设计')
table(['操作','事务与结果','异常处理'],[
('接受邀请','先检查同用户同动作幂等结果；新请求锁定商品行，重查邀请/权限/截止；创建交易、保存标价、锁定商品、结束其他预约并记日志。','同键同参数返回原结果；同键不同参数拒绝；旧邀请、超时和已锁定状态拒绝，不能返回伪成功。'),
('取消及到期','无人确认时主动取消或到期解除锁定；主动取消关联信用事件，超时本身不归责。','单方确认后不允许直接取消或自动释放；旧预约不因释放而复活。'),
('确认完成','分别保存双方确认；第二方确认才完成，并把商品置已售出。','重复确认不重复计数；与到期、取消串行检查，失败不留下部分写入。'),
('违规与争议','管理员核实证据、给理由，必要时结束未确认交易；单方确认交易转争议。','投票不自动处罚；受限账号仍可处理旧交易及申诉；原始证据不公开。'),
('信用更正','按事件时间和ID重放；同笔取较高罚分，后认定仅补差额，误判撤销后重算受影响历史。','保留答题恢复与更正版本，每事件后限制0～100；自然移出窗口不返分。'),
('日志与统计','业务成功日志与状态同事务；拒绝和失败记录独立安全审计；统计从有效完成交易查询。','不记录明文密码与私密材料；不在前端累加次数或金额。')],[30,126,104])
h('质量要求如何落到设计')
p('数据唯一约束、固定锁顺序和幂等请求记录共同保证一致性；会话与对象权限服务保护证据；定时任务复用业务服务并执行每日备份。实验一的1万商品、100并发、P95不超过2秒等条件仍是未来验收目标，本次未实现或运行这些业务测试。')
p('校园卡照片留存期限、身份更正与找回证明、密码复杂度和找回方式仍为待确认事项。设计保留可配置策略与人工入口，不擅自写成已经确认的业务规则。',small)

new('五、UML图种的理解与选择')
table(['分类','图种','用途与本项目选择'],[
('结构性','类图（必画）','类的字段、方法、关联、多重性及接口。本项目分交易和信用两张，便于阅读。'),
('结构性','对象图','展示某一时刻的具体实例与链接；本项目用界面示例和状态守卫说明实例，不单独绘制。'),
('结构性','组件图','描述模块及依赖，本项目用于说明六个模块、入口、适配器和存储。'),
('结构性','复合结构图','展示单个分类器内部部件、端口和连接；当前规模不需要进一步展开。'),
('结构性','部署图','描述运行节点和制品分布；本次以单体加数据库/对象存储说明，不另画部署拓扑。'),
('结构性','包图','表达包分组与依赖；已在分层与组件图中说明代码组织，不重复作主图。'),
('结构性','剖面图','用构造型、标记值和约束扩展UML；本项目无需自定义完整剖面。'),
('行为性','用例图','展示角色及系统边界，选用以区分买家、卖家和管理员的目标。'),
('行为性','状态图','描述对象生命周期和守卫条件，选用交易状态防止单方确认后错误超时。'),
('行为性','活动图','描述决策与工作流，选用商品自动审核及人工复核过程。'),
('交互性','时序图 / 序列图','按时间展示参与者消息，选用接受邀请的事务与并发路径；两名称不算两种图。'),
('交互性','通信图','突出对象协作网络和编号消息；本项目已有时序图，不重复展示相同调用。'),
('交互性','交互概览图','以活动结构组合多个交互；当前主流程用活动图及单个关键时序已能表达。')],[24,49,187])
p('本报告实际绘制7张、6种UML图，满足三类覆盖；后续每张明确标注图种，源代码均为PlantUML。',small)

diagrams=json.loads((R/'uml_manifest.json').read_text(encoding='utf-8'))
diagram_desc=[
 'User可同时买卖；商品、意向、邀请和交易分开建模。Product到Trade是多笔历史关系，数据库只限制当前有效交易唯一。金额字段用{field}明确为字段，避免Decimal括号被误判为方法。',
 '信用策略通过接口分别实现取消与爽约计罚；事件账保留更正和恢复，当前信用只是投影。案件关联证据和投票，公众意见不能直接改分或限制账号。',
 'HTTP入口执行会话与权限校验，六个业务模块调用持久化适配器。跨模块业务使用同一数据库事务，定时任务复用交易服务，图片先暂存后绑定。',
 '买家与卖家都是已认证用户的业务角色，共享信用、举报和统计能力；管理员承担认证、裁决、审核和日志。包含关系仅用于发布/修改提交后的审核子流程，不表示保存草稿也强制审核。',
 '交易在接受有效邀请后进入锁定。无人确认可取消或超时；单方确认后只能等待另一方或进入争议，不再自动超时。管理员按证据完成或解除交易。',
 '鉴权后先检查当前用户范围内的幂等结果，避免已成功请求重试时被商品锁定状态误拒绝。新请求锁商品行再验证当前邀请，成功结果与所有状态同事务保存。',
 '先校验操作者及商品状态，再进入自动审核。审核服务异常保留待审；规则失败说明原因，可申请人工复核；修改后重新审核，首次发布时间不刷新。'
]
for i,(d,desc) in enumerate(zip(diagrams,diagram_desc),1):
 new('五-'+str(i)+'、'+d['title'])
 img(R/'UML'/(d['file']+'.png'),maxh=143*mm)
 p(desc,small)

screens=json.loads((R/'figma_manifest.json').read_text(encoding='utf-8'))['screens']
ui_desc=[
 '注册区包含账号、密码和再次确认；登录区包含账号与密码。注册产生未认证账号，未登录标签与页面状态一致，认证是后续独立步骤。密码复杂度和找回流程不擅自定死。',
 '展示姓名、学号、校园卡上传及驳回后重提。上传材料仅本人和管理员可见；同学号唯一，材料模糊时说明原因。留存期限仍待确认。',
 '支持关键词、分类、价格及商品状态联合筛选，提供最新和最热门。商品卡展示标价和状态，锁定商品仍能被查询但不能新预约。商品图为可编辑示意图，非真实照片。',
 '展示商品信息、卖家信用、购买意向按钮及双方留言。意向不独占商品；锁定、下架或售出时禁用预约并由接口再次检查，避免旧页面成功假象。',
 '商品表单区分保存草稿和提交审核，说明价格及图片限制。显示非法价格示例和自动审核边界；已有锁定商品不能用该页面直接编辑。',
 '列表覆盖发布、锁定、待审、驳回和草稿；按状态提供操作。自动检查不可用时保持待审，误拦截可填理由申请复核；下架不恢复旧预约。',
 '卖家可比较多个预约者信用，选人并提出截止时间；买家从对应邀请接受后才锁定。改选使旧邀请失效，重复接受返回已有结果。',
 '示例为买家已确认、卖家未确认。禁用直接取消，仍允许卖家确认或任一方提交争议；无人确认才可到期自动释放。锁定标价保持不变。',
 '展示当前分数、等级、取消与爽约不同口径及信用事件明细。恢复分数不解除账号处罚；同笔取较高处罚，错误认定可由管理员更正。',
 '给出5道规则题及每日一次提交入口，全对恢复1分。题目展示内容为样例，不等于固定每日题目；提交后必须由后端按北京时间占用当日额度。',
 '关联交易或商品填写事实、上传证据，并查看处理进度或发起一次申诉。原始照片与另一方摘要分开；超时或重复申诉拒绝。',
 '公众只看脱敏摘要，选择支持处理、证据不足或无法判断。一人一票不可修改，72小时截止；涉事及受限用户不能参与，票数仅供管理员参考。',
 '管理员核对校园卡材料，处理商品审核及复核，并维护禁售词。图中学号、姓名均为虚构，不含真实证件。更新规则不直接给历史用户扣分。',
 '管理员核实双方材料、查看参考票数、填写决定和理由，可限制交易、发起评议或撤销误判。公众评议和最终裁决是不同动作，私密证据不进入投票页。',
 '按用户、时间和动作组合查关键日志，包括旧邀请拒绝和信用事件。此页展示管理员视图；普通用户通过本人记录入口查看自己的日志，不能改删。',
 '发布数按至少发布过一次的商品ID去重，状态分布包含后来下架或违规。完成数与总额只来自本人参与的完成交易，金额是锁定标价，非平台实际收款。'
]
for i,(s,desc) in enumerate(zip(screens,ui_desc),1):
 new(f'六-{i}、UI界面：'+s['name'][3:])
 img(R/'UI界面'/(s['name']+'.png'),maxh=143*mm)
 p('功能与交互：'+desc,small)
 p('关联需求：'+s['req']+'；Figma可编辑画板：'+s['id'],small)

new('七、AI辅助工具使用记录（1/2）')
p('使用工具：Codex桌面应用、Figma MCP、PlantUML 1.2026.9、Graphviz和PDF排版工具。完整原始用户输入、可见交流、初始UI源码、UML修改差异均保存在仓库lab2/AI记录；以下按实际辅助场景逐项记录。')
table(['使用场景','生成结果','优点与实际局限','修改优化后的结果'],[
('AI-01 需求到设计','依据实验一需求生成六模块、领域对象、数据表及接口草案。','能集中整理复杂状态；但技术选择只是建议，不能把未定留存和找回规则擅自确认。','分清User角色、意向/邀请/交易，使用有效子集唯一性保留历史；架构仍待本人判断。'),
('AI-02 UML生成','七份puml及对应PNG；初始源码由Git提交3b0a1a6保留。','可追踪文本差异；但初次出现换行转义错误、金额字段被当方法、幂等判断顺序不当。','修正原始字符串与{field}；幂等成功回放前置，同键不同参数拒绝；重新渲染通过。')],[36,70,78,76])
h('实际思考的边界')
p('实验一中本人明确决定的业务范围已经作为基线，本实验的新增技术方案先由AI提出。当前发现与修正均属于AI自查，不能把渲染修复或自动检查写成本人已经作出的人工修改。需要本人对并发方案、模型分离和界面权限做实质判断后，再保存对应反馈和Git提交。')
h('资料使用')
p('两份往届压缩包只参考目录和部分报告组织，不复制其中的UML、UI或文字。附件2.md为旧版要求；报告按本次用户给出的2026说明编写，截止时间为2026年11月6日23:59，允许AI辅助报告但要求本人检查。')

new('七、AI辅助工具使用记录（2/2）')
table(['使用场景','生成结果','优点与实际局限','修改优化后的结果'],[
('AI-03 Figma UI','16个原生可编辑画板，复用按钮与输入框，统一中文字体和语义色。','可批量维护；初次结构检查未发现中间容器高度裁切，身份标签和管理入口也需对照业务核对。','视觉检查后改为按内容确定高度；校正身份、隐藏普通管理入口、补齐注册表单，重导出16张PNG。'),
('AI-04 报告与打包','汇总设计、图和界面，生成PDF及符合目录要求的压缩包。','减少命名及漏放文件问题；不能代替本人思考，也不能凭报告声称系统性能测试已通过。','逐页检查PDF、对照需求与图文件，保留人工审查待完成状态及待确认事项。')],[36,70,78,76])
h('能否让人只负责检查校对？')
p('建议工作流是：本人明确目标与边界 → AI生成设计及备选方案 → 自动检查语法、文件对应和覆盖 → AI用反例检查状态及接口 → 本人决定保留或修改 → 保存真实反馈及修改提交 → 重新渲染与打包。')
p('如果检查校对包括判断权限、异常、事务和业务代价，人可以主要承担审查与决策，少做机械绘图；如果只检查排版和错别字，就不足以保证设计正确。自动化工具能验证图能生成、文件齐全，却不能独立决定争议规则是否合理，也无法代替真实用户确认未定需求。')
p('本稿未伪造人工审查完成记录。下一步需要本人阅读后决定是否保留模块化单体和行锁、是否认可意向/邀请/交易分离，以及是否接受图中的私密材料访问边界。',small)

new('八、版本、待审查项与参考资料')
p('公开仓库：https://github.com/paulzrm/software-engineering-2026-lab1',small)
p('本实验文件位于lab2目录；沿用仓库保存连续演进，不移动实验一两个固定标签。',small)
table(['阶段','完整提交编号或定位','说明'],[
('实验一需求基线','f231f182f1007cdb42d7265251c8c29a3612285a','lab1-final，只读基线。'),
('实验二AI初始UML','3b0a1a6（完整号可由Git解析）','先保留生成结果，含真实渲染问题。'),
('实验二AI自查与UI','aa235301454bcbea2ab9848945dd384a1ad58ebf','补充Figma输出、语义修正、AI记录。'),
('本人审查与人工修改','待本人反馈后提交','当前没有虚构该阶段；课程要求仍需完成。')],[49,116,95])
p('Figma源文件：https://www.figma.com/design/MzYfVETDV1TPYxcXBlAaxM',small)
h('本人集中核对清单')
p('1. 是否保留模块化单体、PostgreSQL及行锁？若同意，请说明你认为这比微服务适合本项目的原因。\n2. 商品、意向、邀请与锁定交易是否需要分开？请核对旧邀请和单方确认的反例。\n3. 普通用户不看管理入口，校园卡及原始证据不公开投票，是否符合你的预期？可提出一个实际界面修改。')
h('参考资料（访问日期2026-11-05）')
for name,url in [('PlantUML类图','https://plantuml.com/zh/class-diagram'),('PlantUML组件图','https://plantuml.com/zh/component-diagram'),('PlantUML时序图','https://plantuml.com/zh/sequence-diagram'),('PlantUML状态图','https://plantuml.com/zh/state-diagram')]:p(name+'：'+url,small)
p('提交目录：实验2_241220002_张瑞珉 / 实验报告.pdf、UML（7份PNG与7份puml）、UI界面（16份PNG）。本版为可审查初稿，收到本人反馈后再生成最终提交版。',small)

def footer(c,doc):
 w,h=landscape(A4);c.setStrokeColor(colors.HexColor('#B6C8BE'));c.line(16*mm,12*mm,w-16*mm,12*mm);c.setFont('Song',8);c.drawString(16*mm,8*mm,'软件工程2026秋 · 实验二 · 张瑞珉 241220002 · AI辅助设计初稿');c.drawRightString(w-16*mm,8*mm,str(doc.page))
out=R/'实验报告.pdf'
doc=SimpleDocTemplate(str(out),pagesize=landscape(A4),leftMargin=17*mm,rightMargin=17*mm,topMargin=13*mm,bottomMargin=18*mm,title='实验二：软件设计与建模 - 校内二手交易系统',author='张瑞珉')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
reader=PdfReader(out);text='\n'.join(page.extract_text() or '' for page in reader.pages)
assert '241220002' in text and '校园卡' in text and 'AI辅助工具使用记录' in text
assert len(reader.pages)==31,(len(reader.pages),len(toc))
dest=R.parent/'output'/'实验2_241220002_张瑞珉.zip'
prefix='实验2_241220002_张瑞珉/'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 z.write(out,prefix+out.name)
 for folder in ('UML','UI界面'):
  for f in sorted((R/folder).iterdir()):
   if f.is_file() and f.suffix.lower() in ('.png','.puml'):z.write(f,prefix+folder+'/'+f.name)
with zipfile.ZipFile(dest) as z:
 assert len(z.namelist())==31,len(z.namelist())
 assert z.testzip() is None
 for f in (R/'UML').glob('*.puml'):
  assert z.read(prefix+'UML/'+f.name)==f.read_bytes()
print(json.dumps({'pdf_pages':len(reader.pages),'uml_sources':7,'uml_png':7,'ui_png':16,'zip_files':31,'zip_bytes':dest.stat().st_size,'zip_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
