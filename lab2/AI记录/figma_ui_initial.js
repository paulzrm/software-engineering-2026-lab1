// Editable Figma Design construction, used in four retry-safe batches.
const createdNodeIds=[];
const keep=n=>{createdNodeIds.push(n.id);return n};
await Promise.all(['Regular','Medium','Bold'].map(style=>figma.loadFontAsync({family:'Noto Sans SC',style})));
await Promise.all(['Regular','Medium','Semi Bold','Bold'].map(style=>figma.loadFontAsync({family:'Inter',style})));
const [buttonSet,inputSet,bodyStyle]=await Promise.all([
 figma.importComponentSetByKeyAsync('cc8b558dc7d9684011b6b99ce8e6509399bc836b'),
 figma.importComponentSetByKeyAsync('c28150b04d333d34ed9d2b77abd9f2f54e1a878a'),
 figma.importStyleByKeyAsync('cebee1b62ea594fa8f97b0b247fd163730736f2a')]);
const page=figma.currentPage;page.name='拾集 · 全模块界面';
const palette={brand:'#23665A',ink:'#203B35',muted:'#70847C',canvas:'#F5F6F0',paper:'#FFFFFF',soft:'#E8F0E9',line:'#DCE5DD',amber:'#A36B25',danger:'#AA4C43'};
function rgb(hex){const s=hex.replace('#','');return {r:parseInt(s.slice(0,2),16)/255,g:parseInt(s.slice(2,4),16)/255,b:parseInt(s.slice(4,6),16)/255}}
let col=(await figma.variables.getLocalVariableCollectionsAsync()).find(c=>c.name==='拾集·界面语义');
if(!col)col=figma.variables.createVariableCollection('拾集·界面语义');
const local=await figma.variables.getLocalVariablesAsync();const vars={};
for(const [name,hex] of Object.entries(palette)){
 let v=local.find(x=>x.name==='color/'+name&&x.variableCollectionId===col.id);
 if(!v){v=figma.variables.createVariable('color/'+name,col,'COLOR');v.scopes=['FRAME_FILL','SHAPE_FILL','TEXT_FILL'];v.setValueForMode(col.modes[0].modeId,rgb(hex));}
 vars[name]=v;
}
function paint(n,k){n.fills=[figma.variables.setBoundVariableForPaint({type:'SOLID',color:rgb(palette[k])},'color',vars[k])];}
function box(parent,name,dir='VERTICAL',w=400,pad=0,bg=null,gap=14){
 const n=keep(figma.createAutoLayout(dir));n.name=name;n.resize(w,10);n.primaryAxisSizingMode='AUTO';n.counterAxisSizingMode='FIXED';
 n.itemSpacing=gap;n.paddingLeft=n.paddingRight=n.paddingTop=n.paddingBottom=pad;n.fills=[];
 if(bg)paint(n,bg);if(parent)parent.appendChild(n);return n;
}
function txt(parent,str,size=18,color='ink',bold=false,w=null){
 const n=keep(figma.createText());n.name=str.slice(0,40);n.fontName={family:'Noto Sans SC',style:bold?'Bold':'Regular'};
 if(bodyStyle)n.textStyleId=bodyStyle.id;
 n.fontName={family:'Noto Sans SC',style:bold?'Bold':'Regular'};n.fontSize=size;n.lineHeight={unit:'PERCENT',value:145};n.characters=str;paint(n,color);
 parent.appendChild(n);if(w){n.textAutoResize='HEIGHT';n.resize(w,n.height);}return n;
}
function row(p,name,w,gap=14){return box(p,name,'HORIZONTAL',w,0,null,gap)}
function panel(p,title,w){const n=box(p,title,'VERTICAL',w,20,'paper',14);n.cornerRadius=14;if(title)txt(n,title,20,'ink',true,w-40);return n;}
function btn(p,label,variant='Primary',disabled=false){
 const main=buttonSet.children.find(c=>c.type==='COMPONENT'&&c.name===`Variant=${variant}, State=${disabled?'Disabled':'Default'}, Size=Medium`)||buttonSet.defaultVariant;
 const n=keep(main.createInstance());n.name='操作/'+label;p.appendChild(n);n.setProperties({'Label#2:0':label,'Has Icon Start#4:128':false,'Has Icon End#4:64':false});
 for(const t of n.findAllWithCriteria({types:['TEXT']})){t.fontName={family:'Noto Sans SC',style:'Medium'};t.fontSize=16;}
 if(variant==='Primary'&&!disabled)paint(n,'brand');return n;
}
function input(p,label,value,w){
 const n=keep(inputSet.children.find(c=>c.type==='COMPONENT'&&c.name==='State=Default, Value Type=Default').createInstance());n.name='输入/'+label;p.appendChild(n);
 n.setProperties({'Label#280:41':label,'Value#630:14':value,'Has Description#611:20':false,'Has Error#72:6':false});
 n.resize(w,n.height);for(const t of n.findAllWithCriteria({types:['TEXT']})){t.fontName={family:'Noto Sans SC',style:'Regular'};t.fontSize=16;}return n;
}
function badge(p,s,c='brand'){const n=box(p,'状态/'+s,'HORIZONTAL',Math.max(84,s.length*15+24),7,'soft',0);n.cornerRadius=7;txt(n,s,14,c,true);return n;}
function notice(p,s,c='soft'){const n=box(p,'提示','VERTICAL',980,14,c,4);n.cornerRadius=10;txt(n,s,16,c==='soft'?'brand':'paper',false,950);return n;}
function table(p,headers,rows,widths){
 const w=widths.reduce((a,b)=>a+b,0);const t=box(p,'数据表','VERTICAL',w,0,'paper',0);t.cornerRadius=12;
 function tr(vals,isHeader){const rr=box(t,isHeader?'表头':'数据行','HORIZONTAL',w,12,isHeader?'soft':null,0);rr.counterAxisAlignItems='CENTER';vals.forEach((v,i)=>txt(rr,v,isHeader?14:16,isHeader?'muted':'ink',isHeader,widths[i]-(i===0?16:10)));}
 tr(headers,true);rows.forEach(r=>tr(r,false));return t;
}
function bar(p,label,value,max,w=280){txt(p,label,16,'muted');const b=box(p,'统计条','HORIZONTAL',w,0,'soft',0);b.resize(w,10);b.primaryAxisSizingMode='FIXED';b.cornerRadius=5;const f=keep(figma.createRectangle());b.appendChild(f);f.resize(Math.max(4,w*value/max),10);f.cornerRadius=5;paint(f,'brand');}
function productArt(p,type,w=270,h=110){
 const a=box(p,'商品示意图/'+type,'HORIZONTAL',w,0,'soft',0);a.resize(w,h);a.primaryAxisSizingMode='FIXED';a.counterAxisAlignItems='CENTER';a.primaryAxisAlignItems='CENTER';a.cornerRadius=10;
 const shape=box(a,'可编辑商品图','VERTICAL',type==='教材'?65:100,8,'paper',6);shape.cornerRadius=8;
 txt(shape,type==='教材'?'SE':type==='数码'?'⌨':type==='生活'?'日用':'文具',24,'brand',true);
 return a;
}
const configs=[
 ['01','账号登录与注册','账号与认证','REQ-001 / 038','本地账号登录，校园卡认证后开启交易'],
 ['02','学生身份认证','账号与认证','REQ-003 / 037','人工核验 · 学号唯一绑定 · 材料不公开'],
 ['03','发现校园好物','商品与搜索','REQ-009 / 010','让闲置重新被需要'],
 ['04','商品详情与购买意向','商品与搜索','REQ-011 / 014 / 023','发出意向不等于锁定，等待卖家选择'],
 ['05','发布与编辑商品','发布与审核','REQ-004—008','先保存草稿，再审核发布'],
 ['06','我的商品与审核结果','发布与审核','REQ-005—008','草稿、审核、发布与下架状态一处管理'],
 ['07','预约与邀请管理','预约与交易','REQ-011—013','由卖家选择买家，买家接受后才锁定'],
 ['08','线下交易进度','预约与交易','REQ-015—019','双方分别确认，保留完整处理记录'],
 ['09','信用与记录','信用与答题','REQ-020—024','有依据的扣分，可追踪的恢复'],
 ['10','每日交易规则答题','信用与答题','REQ-024','每天一次机会，5题全对恢复1分'],
 ['11','举报、争议与申诉','举报与评议','REQ-018 / 019 / 025 / 028','提交事实和证据，跟踪处理进度'],
 ['12','匿名公众评议','举报与评议','REQ-026 / 027','投票仅供参考，最终由管理员依据证据决定'],
 ['13','认证与商品审核','管理工作台','REQ-005 / 006 / 037','原始材料仅授权管理员可见'],
 ['14','案件处理与账号限制','管理工作台','REQ-025—028','证据核实、脱敏公开与最终裁决分开处理'],
 ['15','关键操作日志','日志与统计','REQ-029 / 031','按用户、时间和操作类型追溯'],
 ['16','个人交易统计','日志与统计','REQ-030','统计已完成的线下标价，不代表平台收款']
];
const output=[];
for(const c of configs.slice(BATCH_START,BATCH_END)){
 const [id,title,active,req,subtitle]=c;
 const existing=page.children.find(n=>n.name===id+'_'+title);if(existing)throw new Error('Screen exists; inspect before retry: '+existing.id);
 const root=box(page,id+'_'+title,'HORIZONTAL',1280,0,'canvas',0);root.resize(1280,900);root.primaryAxisSizingMode='FIXED';root.counterAxisSizingMode='FIXED';root.clipsContent=true;
 root.x=200+((Number(id)-1)%4)*1440;root.y=200+Math.floor((Number(id)-1)/4)*1060;
 const nav=box(root,'侧边导航','VERTICAL',208,24,'brand',20);nav.resize(208,900);nav.primaryAxisSizingMode='FIXED';
 txt(nav,'拾 集',32,'paper',true);txt(nav,'CAMPUS EXCHANGE',11,'soft');
 for(const label of ['商品与搜索','发布与审核','预约与交易','信用与答题','举报与评议','日志与统计','账号与认证','管理工作台']){
  const b=box(nav,label,'VERTICAL',160,10,label===active?'soft':null,0);b.cornerRadius=8;txt(b,label,16,label===active?'brand':'paper',label===active);
 }
 txt(nav,'本校认证 · 线下交易',12,'soft');
 const main=box(root,'主内容','VERTICAL',1072,32,null,20);
 const top=row(main,'页头',1008,14);const ht=box(top,'标题','VERTICAL',790,0,null,3);txt(ht,title,28,'ink',true);txt(ht,subtitle,14,'muted');badge(top,Number(id)>=13?'管理员':'已认证用户');
 const content=box(main,'功能内容','VERTICAL',1008,0,null,16);
 if(id==='01'){
  const r=row(content,'双栏',1008,24);const a=panel(r,'欢迎回到拾集',484);txt(a,'让校园里的好物，多一段故事。',25,'brand',true,440);txt(a,'浏览公开商品无需认证；发布与预约前请先完成校园卡认证。',18,'muted',false,440);productArt(a,'教材',444,195);badge(a,'账号与学号长期关联');
  const b=panel(r,'账号登录',484);input(b,'账号','campus_demo',444);input(b,'密码','••••••••••',444);const actions=row(b,'登录注册',444);btn(actions,'登录');btn(actions,'创建账号','Neutral');txt(b,'注册后为未认证账号，可在认证页提交校园卡。',15,'muted',false,440);txt(b,'注册：设置唯一账号、密码并再次确认密码。',15,'muted',false,440);notice(content,'登录失败仅提示账号或密码不正确，不显示学校身份信息。');
 }else if(id==='02'){
  const r=row(content,'认证双栏',1008,24);const a=panel(r,'填写认证资料',484);input(a,'姓名','演示同学',444);input(a,'学号','DEMO-2026-001',444);const up=box(a,'校园卡上传','VERTICAL',444,24,'soft',8);txt(up,'上传校园卡照片',20,'brand',true);txt(up,'JPEG / PNG / WebP · 每张 ≤ 5MiB',14,'muted');btn(a,'提交人工审核');
  const b=panel(r,'审核状态',484);badge(b,'已驳回','danger');txt(b,'原因：学号区域不清晰，请重新拍摄后提交。',18,'ink',false,440);txt(b,'未提交 → 待审核 → 已通过 / 已驳回',17,'muted',false,440);btn(b,'重新上传并提交','Neutral');txt(b,'校园卡仅本人和管理员可见。照片留存期限与身份找回证明仍为待确认事项。',16,'muted',false,440);notice(content,'同一学号仅能绑定一个已认证账号，重新注册不会清空信用。');
 }else if(id==='03'){
  const search=row(content,'搜索筛选',1008,12);input(search,'关键词','教材 / 数码 / 生活用品',400);input(search,'分类','全部分类',170);input(search,'价格区间','¥0.01—99999.99',220);btn(search,'搜索');
  const tabs=row(content,'状态与排序',1008);badge(tabs,'最新上架');badge(tabs,'最热门');badge(tabs,'可预约');badge(tabs,'已锁定');badge(tabs,'已售出');
  for(let j=0;j<2;j++){const r=row(content,'商品网格',1008,16);for(let i=0;i<3;i++){const k=j*3+i;const card=panel(r,'',320);productArt(card,['教材','数码','生活'][i],280,90);txt(card,['软件工程教材','机械键盘','宿舍收纳盒','英语词汇书','无线鼠标','护眼台灯'][k],18,'ink',true);const rr=row(card,'价格状态',280);txt(rr,['¥35.00','¥120.00','¥18.00','¥20.00','¥45.00','¥38.00'][k],22,'brand',true);badge(rr,k===4?'已锁定':'可预约');}}
 }else if(id==='04'){
  const r=row(content,'详情双栏',1008,24);const a=panel(r,'软件工程教材 · 九成新',600);productArt(a,'教材',560,210);txt(a,'¥35.00',32,'brand',true);txt(a,'无缺页，少量铅笔批注。可在教学楼附近协商当面交易。',18,'ink',false,550);badge(a,'可预约 · 已有3人表达意向');
  const b=panel(r,'卖家与预约',384);txt(b,'同学A　信用 98 · 良好',18,'ink',true,340);txt(b,'买卖双方可以看到对方信用，学号和校园卡不公开。',16,'muted',false,340);btn(b,'发起购买意向');btn(b,'举报商品','Subtle');input(b,'给卖家留言','请问今晚可以面交吗？',344);btn(b,'发送留言','Neutral');notice(content,'商品若已锁定/下架/售出，按钮禁用；旧页面提交时重新校验并提示刷新。');
 }else if(id==='05'){
  const r=row(content,'编辑双栏',1008,24);const a=panel(r,'商品信息',600);input(a,'标题','软件工程教材',560);const rr=row(a,'分类价格',560,16);input(rr,'分类','教材',272);input(rr,'价格（元）','35.00',272);input(a,'描述','九成新，无缺页，可协商线下交易。',560);productArt(a,'教材',560,120);
  const b=panel(r,'提交前检查',384);txt(b,'图片1～9张，每张≤5MiB。价格0.01～99,999.99元，最多两位小数。',17,'muted',false,340);badge(b,'自动审核规则');txt(b,'字段完整性 / 文字禁售词 / 图片格式；不识别图片内容。',17,'ink',false,340);btn(b,'保存草稿','Neutral');btn(b,'提交审核');txt(b,'示例错误：价格不能为0。已发布商品修改后重新审核，期间暂停展示。',16,'danger',false,340);
 }else if(id==='06'){
  table(content,['商品','状态','价格','最近结果 / 可用操作'],[
   ['软件工程教材','已发布','¥35.00','修改 / 下架 / 查看预约'],['机械键盘','已锁定','¥120.00','查看交易（禁止直接修改）'],['收纳盒','待审核','¥18.00','检查服务暂不可用，等待重试'],['台灯','已驳回','¥38.00','含禁售词：修改 / 申请复核'],['旧教材','草稿','未填写','继续编辑 / 提交审核']], [240,150,120,474]);
  const a=panel(content,'人工复核与下架',1008);input(a,'复核说明','商品未涉及禁售内容，请人工复核。',960);const rr=row(a,'操作',960);btn(rr,'提交复核');btn(rr,'编辑选中商品','Neutral');txt(a,'下架结束未锁定预约；商品解锁不恢复原预约。已售出商品再次出售须新建。',16,'muted',false,950);
 }else if(id==='07'){
  const tabs=row(content,'角色页签',1008);badge(tabs,'我是卖家');badge(tabs,'我是买家');
  table(content,['商品 / 买家','信用','意向状态','可用操作'],[['软件工程教材 / 同学B','100 优秀','已选择，待接受','改选 / 留言'],['软件工程教材 / 同学C','97 良好','有效意向','选择此买家'],['软件工程教材 / 同学D','89 一般','有效意向','选择此买家']],[330,150,210,294]);
  const rr=row(content,'邀请双栏',1008,24);const a=panel(rr,'卖家提出截止时间',484);input(a,'交易截止时间（北京时间）','2026-11-06 18:00',444);btn(a,'向所选买家发送邀请');const b=panel(rr,'买家收到邀请',484);txt(b,'商品 ¥35.00 · 截止 11月6日18:00',17,'ink',true,440);btn(b,'接受邀请并锁定');txt(b,'改选后旧邀请立即失效；重复点击返回已有结果。',15,'muted',false,440);
 }else if(id==='08'){
  notice(content,'买家已确认完成，等待卖家确认。此时禁止直接取消，截止时间到达也不自动解锁。');
  const rr=row(content,'交易双栏',1008,24);const a=panel(rr,'交易 #T-DEMO-017',600);txt(a,'软件工程教材　锁定价格 ¥35.00',23,'ink',true,550);txt(a,'买家：同学B 100优秀　卖家：同学A 98良好',16,'muted',false,550);table(a,['阶段','结果'],[['买家接受邀请','已完成，结束其他预约'],['线下交易','由双方实际完成'],['买家确认','已确认'],['卖家确认','等待确认']],[220,336]);
  const b=panel(rr,'卖家操作',384);btn(b,'确认已完成交易');btn(b,'取消交易','Neutral',true);btn(b,'提交交易争议','Neutral');txt(b,'如双方都未确认，可主动取消并填写原因，或到期自动释放。系统释放本身不认定爽约。',17,'muted',false,340);btn(b,'提交到场爽约证据','Subtle');
 }else if(id==='09'){
  const rr=row(content,'信用概览',1008,24);const a=panel(rr,'我的信用',320);txt(a,'98',54,'brand',true);badge(a,'良好');txt(a,'答题恢复不解除账号处罚',15,'muted',false,280);btn(a,'开始每日答题');const b=panel(rr,'扣分和等级规则',664);txt(b,'取消：最近7天第3次起扣2、4、8、16、32分。',17,'ink',false,620);txt(b,'核实爽约：最近30天第2次起扣2、4、8、16、32分。',17,'ink',false,620);txt(b,'同笔处罚取较高值；等级：100优秀 / 95—99良好 / 80—94一般 / 60—79较差 / 0—59差。',16,'muted',false,620);
  table(content,['时间','事件','变动','结果'],[['11-05 09:20','第3次主动取消锁定交易','-2','98'],['11-04 20:00','正常取消未锁定意向','0','100'],['11-03 12:00','5题全对（已满分）','0','100']],[220,450,130,184]);
 }else if(id==='10'){
  notice(content,'今日尚未提交 · 5题全对恢复1分 · 每天最多提交一次，答错不扣分。');
  const a=panel(content,'今日题目（演示内容）',1008);for(const [i,q] of ['买家发起预约后，商品是否立即独占？','单方确认后，是否仍会到期自动解锁？','公众投票能否直接决定封禁？','重复点击接受邀请能否创建两笔交易？','答题恢复分数是否自动解除处罚？'].entries()){
   const rr=row(a,'题目'+(i+1),960,12);txt(rr,(i+1)+'. '+q,17,'ink',false,680);badge(rr,'○ 是');badge(rr,'● 否');}
  const rr=row(a,'提交',960);btn(rr,'提交本次答案');txt(rr,'提交后锁定本日额度，不允许重复提交。',15,'muted');
 }else if(id==='11'){
  const rr=row(content,'举报双栏',1008,24);const a=panel(rr,'提交举报或交易争议',600);input(a,'关联对象','交易 T-DEMO-017',560);input(a,'类型','到场后对方未出现',560);input(a,'事实说明','已到达约定地点，尝试联系后未能见面。',560);const up=box(a,'证据区','VERTICAL',560,18,'soft',8);txt(up,'上传照片与补充说明',18,'brand',true);txt(up,'原始材料仅提交者和管理员可见',15,'muted');btn(a,'提交材料');
  const b=panel(rr,'处理进度与申诉',384);badge(b,'管理员核实中');txt(b,'提交 → 初审 → 必要时公众评议 → 管理员决定 → 申诉复核',18,'ink',false,340);txt(b,'每案公布结果后7×24小时内可申诉一次；填写不服理由和补充材料。',16,'muted',false,340);btn(b,'对已有结果提出申诉','Neutral');txt(b,'同人同事项不能重复举报；截止后或重复申诉将被拒绝。',15,'muted',false,340);
 }else if(id==='12'){
  notice(content,'匿名评议 #C-DEMO-003 · 剩余 32小时18分 · 本人未涉事且未受限，可投票一次。');
  const rr=row(content,'评议双栏',1008,24);const a=panel(rr,'案件脱敏摘要',600);txt(a,'某商品在约定交易后产生争议。管理员已收集双方陈述，现就已脱敏事实征求意见。',22,'ink',true,550);txt(a,'不展示姓名、学号、联系方式、地址、付款信息或原始证据照片；这里只展示必要事实摘要。',18,'muted',false,550);badge(a,'投票不等于认定违规');
  const b=panel(rr,'你的意见',384);btn(b,'支持处理');btn(b,'证据不足','Neutral');btn(b,'无法判断','Neutral');txt(b,'每案一票，提交不可修改。涉事双方、受限用户及截止后的请求均不能投票。',17,'muted',false,340);txt(b,'管理员依据证据决定，票数不足也不自动结束案件。',16,'muted',false,340);
 }else if(id==='13'){
  table(content,['校园卡认证申请','学号（管理视图）','状态','处理'],[['演示同学 / V-DEMO-01','DEMO-2026-001','待审核','核对材料 / 通过 / 驳回'],['演示同学 / V-DEMO-02','DEMO-2026-001','学号已绑定','驳回重复认证']],[300,260,150,274]);
  const rr=row(content,'审核双栏',1008,24);const a=panel(rr,'商品审核与复核',600);txt(a,'P-DEMO-21 · 台灯 · 命中文字禁售规则',18,'ink',true,550);input(a,'审核理由','需核对描述，确认是否属于误拦截。',560);const actions=row(a,'审核操作',560);btn(actions,'复核通过');btn(actions,'驳回并说明原因','Neutral');
  const b=panel(rr,'规则管理',384);input(b,'禁售词示例','违规词条（示例）',344);btn(b,'保存词表','Neutral');txt(b,'更新词表不自动给历史用户扣分；自动审核不可用时商品保留待审。',16,'muted',false,340);txt(b,'校园卡是私密材料，本界面仅使用虚构样本，不包含真实卡片。',15,'muted',false,340);
 }else if(id==='14'){
  const rr=row(content,'案件双栏',1008,24);const a=panel(rr,'案件 C-DEMO-003',600);txt(a,'原始证据：仅管理员与各自提交者可见',17,'danger',true,550);txt(a,'已核对双方说明。核实前不自动扣分，不公开举报对象身份。',18,'ink',false,550);table(a,['公众参考','票数'],[['支持处理','28'],['证据不足','12'],['无法判断','7']],[330,226]);input(a,'对外脱敏摘要','仅公开必要事实与最终处理理由。',560);
  const b=panel(rr,'管理员最终决定',384);input(b,'处理动作','认定爽约 / 限制新交易',344);input(b,'理由','依据已核实证据说明事实及处理原因。',344);btn(b,'提交裁决');btn(b,'发起72小时匿名评议','Neutral');btn(b,'撤销误判并重算信用','Neutral');txt(b,'解除限制需管理员处理；受限用户仍能处理旧交易和申诉。',16,'muted',false,340);
 }else if(id==='15'){
  const rr=row(content,'日志筛选',1008,12);input(rr,'用户','同学A / 用户ID',260);input(rr,'时间区间','2026-11-01—2026-11-05',340);input(rr,'操作类型','全部 / 信用变更 / 交易',270);btn(rr,'查询');
  table(content,['时间','操作者','对象 / 操作','结果'],[['11-05 15:30','同学B','T-017 / 买家确认','成功，保持锁定'],['11-05 15:20','同学B','I-021 / 接受邀请','成功，创建T-017'],['11-05 15:20','同学C','I-020 / 接受旧邀请','拒绝：邀请已失效'],['11-05 10:10','管理员','V-001 / 校园卡审核','通过'],['11-05 09:20','系统','用户A / 取消计罚','-2，关联事件E-201']],[180,140,430,234]);
  notice(content,'普通用户只能查询本人记录；管理员支持组合筛选。日志不可由普通用户修改删除，不记录明文密码和原始私密证据。');
 }else if(id==='16'){
  const rr=row(content,'指标卡',1008,20);for(const [label,value] of [['累计发布商品','12'],['完成交易','8'],['成交标价合计','¥436.00']]){const a=panel(rr,label,322);txt(a,value,40,'brand',true);}
  const rr2=row(content,'统计双栏',1008,24);const a=panel(rr2,'商品状态分布',600);bar(a,'可预约　4',4,12,550);bar(a,'已锁定　2',2,12,550);bar(a,'已售出　5',5,12,550);bar(a,'下架 / 违规　1',1,12,550);
  const b=panel(rr2,'口径说明',384);txt(b,'发布数：至少正式发布过一次的商品ID去重计数，含后来下架、违规和已售出。',17,'ink',false,340);txt(b,'完成数：本人参与且有效完成的交易，每笔只计一次。金额使用锁定时标价，排除取消与未完成交易。',17,'muted',false,340);txt(b,'平台不接在线支付，统计不代表实际收款。',16,'brand',true,340);
 }
 root.exportSettings=[{format:'PNG',constraint:{type:'SCALE',value:1}}];
 output.push({id:root.id,name:root.name,req,width:root.width,height:root.height,descendants:root.findAll(()=>true).length});
}
return {createdNodeIds,screens:output,font:'Noto Sans SC',editable:true};


