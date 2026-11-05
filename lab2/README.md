# 实验二：软件设计与建模

项目2，校内二手交易系统。张瑞珉，241220002。

当前为可审查初稿：

- `实验报告.pdf`：31页，含主要功能、面向对象架构、数据约束、六种UML图、16个界面、AI使用与优化过程。
- `UML/`：7份PlantUML源文件及7份PNG。
- `UI界面/`：16份从Figma原生可编辑设计导出的PNG。
- `设计说明.md`：模块、存储、事务、接口与待确认边界。
- `本人审查清单.md`：集中核对三项设计判断。
- `AI记录/`：完整用户输入及可见交流、初始UI源码、实际UML改动差异和使用分析。

Figma源文件：https://www.figma.com/design/MzYfVETDV1TPYxcXBlAaxM

基线是`lab1-final`，不修改实验一两个固定标签。当前Git保留初始AI UML生成阶段（3b0a1a6）与AI自查/UI阶段（aa23530），后续本人的实际反馈另行记录，不能把AI修改写成本人修改。

初稿压缩包在仓库根目录的 `output/实验2_241220002_张瑞珉.zip`，仅含课程规定的报告、UML、UI界面。不要提交整个仓库源码压缩包。收到本人审查意见后再生成最终提交版。

参考资料仅作组织参考，未复制往届作业图和界面。执行要求以本次提供的2026题面为准，附件2.md为旧版说明。

PlantUML渲染：Java21 + PlantUML1.2026.9 + Graphviz16.1；`tools/write_uml.py`保留生成过程。PDF打包脚本`tools/build_report.py`依赖ReportLab、Pillow、pypdf及中文字体。Figma构建源码在`tools/figma_ui.js`，其中批次起止占位符由调用时替换，不是独立可执行的浏览器脚本。
