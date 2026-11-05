from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[1];U=R/'UML';U.mkdir(parents=True,exist_ok=True)
(R/'baseline').mkdir(exist_ok=True)
(R/'baseline'/'requirements.md').write_bytes(subprocess.check_output(['git','show','lab1-final:requirements.md'],cwd=R))
common='''@startuml
skinparam defaultFontName Microsoft YaHei
skinparam defaultFontSize 16
skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam ArrowColor #32665C
skinparam classBackgroundColor #F3F8F5
skinparam classBorderColor #71978A
skinparam packageBackgroundColor #FFFFFF
skinparam roundcorner 8
skinparam dpi 160
'''
diagrams={
'01_类图_交易领域':('结构性图：交易领域类图', r'''
hide circle
top to bottom direction
class User {
 - id: UUID
 - username: String
 - passwordHash: String
 - status: AccountStatus
 + canStartTrade(): boolean
}
class Verification {
 - id: UUID
 - schoolStudentKey: String
 - realName: String
 - state: VerificationState
 - cardAssetId: UUID
 + approve(reviewerId)
 + reject(reason)
}
class Product {
 - id: UUID
 - sellerId: UUID
 - title: String
 {field} - price: Decimal(10,2)
 - state: ProductState
 - version: long
 + submit()
 + lockFor(tradeId)
 + markSold()
}
class Reservation {
 - id: UUID
 - buyerId: UUID
 - state: ReservationState
 + cancel(reason)
 + close(reason)
}
class Invitation {
 - id: UUID
 - deadline: Instant
 - state: InvitationState
 + expire()
 + invalidate()
}
class Trade {
 - id: UUID
 - buyerId: UUID
 - sellerId: UUID
 {field} - lockedPrice: Decimal(10,2)
 - deadline: Instant
 - state: TradeState
 - buyerConfirmed: boolean
 - sellerConfirmed: boolean
 + confirm(actorId)
 + cancel(actorId,reason)
 + expire(now)
}
class Message {
 - id: UUID
 - authorId: UUID
 - content: String
 - createdAt: Instant
}
class MediaAsset {
 - id: UUID
 - ownerId: UUID
 - objectKey: String
 - accessScope: AssetScope
 + authorizeRead(actorId)
}
class TradeService <<application>> {
 + acceptInvitation(actorId, invitationId, key)
 + confirmCompletion(actorId, tradeId, key)
 + cancelTrade(actorId, tradeId, key)
}
interface TradeRepository {
 + lockProduct(productId)
 + saveAtomically(trade, product)
}
User "1" -- "0..*" Product : 发布 >
User "1" -- "0..*" Verification : 提交 >
Product "1" -- "0..*" Reservation
User "1" -- "0..*" Reservation : 买家 >
Reservation "1" -- "0..*" Invitation : 历史邀请 >
Product "1" -- "0..*" Trade : 历史交易 >
Trade "0..1" -- "1" Invitation : 接受后创建 >
Reservation "1" *-- "0..*" Message
User "1" -- "0..*" MediaAsset
Verification --> MediaAsset : 私密校园卡
Product --> MediaAsset : 商品图片
TradeService ..> Trade
TradeService ..> Product
TradeService ..> TradeRepository
note bottom of Product
同商品最多一笔有效锁定交易；不是只允许一笔历史交易。
已预约是有效意向提示，不是独占锁定状态。
end note
note bottom of Verification
同学号最多一个审核通过账号。
买家和卖家是User的业务角色，不分成互斥子类。
end note
'''),
'02_类图_信用治理':('结构性图：信用与治理类图',r'''
hide circle
class CreditAccount {
 - userId: UUID
 - score: int
 - version: long
 + replay(events)
 + grade(): CreditGrade
}
class CreditEvent {
 - id: long
 - userId: UUID
 - tradeId: UUID?
 - kind: EventKind
 - occurredAt: Instant
 - amount: int
 - revoked: boolean
}
interface PenaltyPolicy {
 + penalty(count): int
 + windowDays(): int
}
class CancellationPolicy {
 + penalty(count): int
 + windowDays(): int = 7
}
class NoShowPolicy {
 + penalty(count): int
 + windowDays(): int = 30
}
class CreditService {
 + recordCancellation(tradeId, actorId)
 + recognizeNoShow(caseId, actorId)
 + revokeRecognition(eventId)
 + mergeAndReplay(userId)
}
class QuizAttempt {
 - userId: UUID
 - localDate: Date
 - answers: JSON
 - correctCount: int
 + submit()
}
class ModerationCase {
 - id: UUID
 - targetType: TargetType
 - targetId: UUID
 - reporterId: UUID
 - state: CaseState
 - publicSummary: String
 + startVote(deadline)
 + decide(action,reason)
 + appeal(actorId,reason)
}
class CaseEvidence {
 - submitterId: UUID
 - mediaAssetId: UUID
 - explanation: String
 + authorizeRead(actorId)
}
class Vote {
 - caseId: UUID
 - voterId: UUID
 - choice: VoteChoice
 - createdAt: Instant
}
class AuditEntry {
 - actorId: UUID
 - action: String
 - targetType: String
 - targetId: UUID
 - result: String
 - occurredAt: Instant
}
PenaltyPolicy <|.. CancellationPolicy
PenaltyPolicy <|.. NoShowPolicy
CreditService ..> PenaltyPolicy
CreditService ..> CreditAccount
CreditService ..> ModerationCase
CreditAccount "1" *-- "0..*" CreditEvent
QuizAttempt --> CreditEvent : 全对恢复事件
ModerationCase "1" *-- "0..*" CaseEvidence
ModerationCase "1" *-- "0..*" Vote
ModerationCase --> CreditService : 核实后才计罚
CreditService ..> AuditEntry
ModerationCase ..> AuditEntry
note bottom of CreditAccount
按(occurredAt,id)顺序重放；每事件后限制0..100。
同笔同人取较高罚分，误判撤销保留更正历史。
end note
note bottom of Vote
唯一(caseId,voterId)；涉事双方及受限用户不可投票。
投票不触发自动处罚，最终由管理员裁决。
end note
'''),
'03_组件图_模块架构':('结构性图：模块化单体组件图',r'''
left to right direction
component "用户端 / 管理端\nWeb UI" as UI
component "HTTP入口\n会话·RBAC·幂等" as API
package "应用服务（同一进程）" {
 component "账号与校园卡认证" as Auth
 component "商品与自动审核" as Product
 component "预约与交易" as Trade
 component "信用与答题" as Credit
 component "举报·投票·申诉" as Case
 component "查询·统计·日志" as Query
}
component "定时任务\n到期释放·备份" as Job
component "持久化适配器\nRepository / UnitOfWork" as Repo
database "PostgreSQL\n关系·状态·约束·日志" as DB
storage "对象存储\n商品图 / 私密证据" as Files
UI --> API : HTTPS
API --> Auth
API --> Product
API --> Trade
API --> Credit
API --> Case
API --> Query
Trade --> Auth : 交易权限
Trade --> Credit : 取消计罚
Case --> Trade : 争议裁决
Case --> Credit : 爽约认定/撤销
Product --> Trade : 违规下架联动
Job --> Trade : expire(now)
Auth --> Repo
Product --> Repo
Trade --> Repo
Credit --> Repo
Case --> Repo
Query --> Repo
Repo --> DB
Repo --> Files : 私密访问鉴权
Job --> DB : 每日备份
note bottom of Repo
跨业务状态在同一数据库事务内更新。
上传图片先暂存，通过业务提交后绑定；
孤立暂存文件由清理任务回收。
end note
'''),
'04_用例图_角色权限':('行为性图：用户角色用例图',r'''
left to right direction
actor "浏览者" as Guest
actor "已认证用户" as User
actor "买家" as Buyer
actor "卖家" as Seller
actor "管理员" as Admin
User --|> Guest
Buyer --|> User
Seller --|> User
rectangle "校内二手交易系统" {
 usecase "组合查询与排序" as Search
 usecase "注册登录/提交认证" as Register
 usecase "商品草稿/发布/修改/下架" as Publish
 usecase "自动审核/人工复核" as Audit
 usecase "预约/接受当前邀请" as Reserve
 usecase "选择预约者与截止时间" as Select
 usecase "取消/双方确认完成" as Complete
 usecase "信用查询/每日答题" as Credit
 usecase "举报/举证/申诉" as Report
 usecase "匿名公众投票" as Vote
 usecase "个人统计与本人日志" as Stats
 usecase "认证核验/违规与争议裁决" as Review
 usecase "日志查询/账号限制" as Logs
}
Guest --> Search
Guest --> Register
Seller --> Publish
Publish ..> Audit : <<include>>\n提交或修改后
Buyer --> Reserve
Seller --> Select
Buyer --> Complete
Seller --> Complete
User --> Credit
User --> Report
User --> Vote
User --> Stats
Admin --> Audit
Admin --> Review
Admin --> Logs
note bottom of Vote
只向非涉事且未受限用户开放；一人一票。
校园卡及原始举报证据不向公众展示。
end note
'''),
'05_状态图_交易生命周期':('行为性图：锁定交易状态图',r'''
state "已锁定/无人确认" as Locked
state "买家已确认" as BuyerOK
state "卖家已确认" as SellerOK
state "争议处理中" as Disputed
state "双方确认完成" as Completed
state "主动取消" as Cancelled
state "超时释放" as Expired
state "管理员解除" as Released
[*] --> Locked : 当前受邀买家接受\n[截止前且商品可预约]
Locked --> BuyerOK : 买家确认
Locked --> SellerOK : 卖家确认
BuyerOK --> Completed : 卖家确认
SellerOK --> Completed : 买家确认
Locked --> Cancelled : 买家或卖家主动取消
Locked --> Expired : 到期且无人确认
BuyerOK --> Disputed : 任一方提交争议\n或管理员违规下架
SellerOK --> Disputed : 任一方提交争议\n或管理员违规下架
Disputed --> Completed : 管理员裁决完成
Disputed --> Released : 管理员裁决解除
Locked --> Released : 管理员违规下架\n无单方确认，不自动扣分
Cancelled --> [*]
Expired --> [*]
Released --> [*]
Completed --> [*]
note right of BuyerOK
单方确认不再自动超时释放，
不允许直接取消，保留锁定。
end note
note bottom of Completed
完成后商品为已售出，不可恢复。
取消/到期释放商品可预约，但原其他预约不复活。
end note
'''),
'06_时序图_接受邀请并发控制':('交互性图：接受邀请与唯一锁定时序图',r'''
autonumber
actor "当前受邀买家" as Buyer
boundary "预约界面" as UI
control "TradeService" as S
database "PostgreSQL" as DB
Buyer -> UI : 接受邀请
UI -> S : accept(invitationId, idempotencyKey)
S -> DB : BEGIN; 按用户/动作/键读取幂等记录和参数摘要
alt 同键、同参数已有成功结果
 S -> DB : 读取原结果; COMMIT
 S --> UI : 返回原tradeId，不重新校验可预约状态
else 同键不同参数
 S -> DB : ROLLBACK
 S --> UI : 409 幂等键冲突
else 新请求
 S -> DB : 占用幂等键，锁定商品行
 S -> DB : 重查当前邀请、认证权限、截止时间与商品状态
 alt 旧邀请/过期/非当前买家/商品不可预约
  S -> DB : ROLLBACK（业务变更）
  S --> UI : 409状态冲突或403无权限
  UI --> Buyer : 提示刷新，不显示锁定成功
 else 当前状态有效
  S -> DB : 创建Trade(锁定标价、截止时间)
  S -> DB : 商品置LOCKED，当前预约置LOCKED
  S -> DB : 结束其他预约及邀请
  S -> DB : 写操作日志和幂等响应
  S -> DB : COMMIT
  S --> UI : tradeId + 当前状态 + lockedPrice
  UI --> Buyer : 显示锁定与交易截止时间
 end
end
note over S,DB
不同买家的并发请求按商品行锁串行校验。
事务失败不得留下商品已锁定但交易不存在的状态。
日志安全拒绝记录独立写入，不回滚成功操作记录。
end note
'''),
'07_活动图_发布审核':('行为性图：商品发布审核活动图',r'''
start
:卖家创建或修改商品;
:保存草稿;
if (选择提交?) then (是)
 :重新校验所有权、权限及当前状态;
 if (已锁定或已售出?) then (是)
  :拒绝修改，保留原商品;
  stop
 else (否)
  :置待审核，暂停展示与预约;
 endif
 :检查字段、价格、图片实际格式、禁售词;
 if (检查服务可用?) then (否)
  :保留待审核，记录失败，等待重试;
  stop
 else (是)
  if (规则通过?) then (是)
   :发布为可预约，保留首次发布时间;
   :记录审核日志，通知卖家;
  else (否)
   :驳回并说明原因;
   if (申请人工复核?) then (是)
    :管理员检查材料;
    if (复核通过?) then (是)
     :发布并记录复核理由;
    else (否)
     :保持驳回，允许修改重提;
    endif
   else (否)
    :保留草稿或驳回信息;
   endif
  endif
 endif
else (否)
 :保持草稿，不公开;
endif
stop
''')}
meta=[]
for name,(title,code) in diagrams.items():
 text=common+'title '+title+'\n'+code+'\n@enduml\n'
 (U/(name+'.puml')).write_bytes(text.encode())
 meta.append({'file':name,'title':title})
(R/'uml_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print('Wrote',len(meta),'PlantUML sources; lab1-final baseline preserved.')
