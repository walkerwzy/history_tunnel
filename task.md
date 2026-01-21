# 欧洲大事年表项目任务清单

## 项目概述
- 目标：生成欧洲大事年表，使用LangChain进行数据处理，d3.js进行可视化展示
- 数据范围：公元前1000年到2026年
- 技术栈：Jupyter Notebook + LangChain + PostgreSQL + d3.js

## 任务列表

### 阶段一：项目初始化和数据库设计
- [x] 创建task.md任务清单
- [x] 创建Jupyter Notebook文件 `european_timeline.ipynb`
- [x] 在Notebook中说明项目依赖（langchain, psycopg2, requests, beautifulsoup4, pandas等）
- [x] 分析数据库需求，确定PostgreSQL表结构设计
  - 事件表：事件名称、起止时间、关键人物、事件概述、事件影响、事件分类、地域
  - 时期表：时期名称、起止时间、时期类型（连续/独立）、地域
- [x] 在Notebook中编写数据库连接和建表代码
- [x] 配置LangChain tools，说明如何配置

 ### 阶段二：数据抓取和处理
- [x] 搜索并分析权威欧洲历史网站（维基百科、欧洲历史博物馆等）
- [x] 编写数据抓取代码cell（Europeana API、Wikipedia API函数），翻译为中文
- [x] 使用LangChain进行数据处理和结构化
  - 事件描述和总结生成
  - 事件影响评估
  - 事件分类（政治变革、科技突破、军事和运动、经济、文化艺术等）
- [x] 数据验证和质量检查
- [x] 将处理后的数据存储到PostgreSQL，应用LangChain使用大模型对数据库进行插入而不是手动编写insert代码

 ### 阶段三：代码抽象和封装
- [x] 将Notebook中的抓取数据并处理，优化和入库的方法进行抽象和重构，封装为可复用的Python程序/模块
- [x] 支持通过参数传入不同地域（如中国）生成大事年表
- [x] 编写使用文档和示例
- [x] 最后用封装好的方法爬取一次中国的大事年表，并存储到数据库中

 ### 阶段四：数据库查询功能
- [x] 实现按时间轴滚动查询功能（enhanced_database_manager.py - get_events_paginated）
- [x] 实现按事件关键字查询功能（enhanced_database_manager.py - search_events_advanced）
- [x] 实现交叉查询同时期其它地区或文明的事件功能(当前有中国和欧洲)（enhanced_database_manager.py - get_cross_regional_comparison）
- [x] 根据事件影响筛选重要事件（解决时间段过长返回数据过多的问题）（enhanced_database_manager.py - get_events_by_importance）
- [x] 基于SQLDatabase对象创建Toolkit(langchain.agents.agent_toolkits)，实现LangChain与数据库的自然语言交互（nl_query_engine.py）

### 阶段五：前端可视化（d3.js/three.js等技术的静态页面）
- [ ] 确定视觉方案：类似掉入黑洞穿越一样的空间隧道变形动效，随着鼠标滚轮的滚动，实现一个主观视角也在往前/后穿行看到的空间隧道的动画效果，左右两边分别显示当前时间点处于的当前区域的时期，左边显示欧洲，右边显示中国，然后这个时间点附近的事件实时查询（可缓存和预取），根据事件重要级显示成直径不一的圆点附在空间隧道上，注意颜色区分。
- [ ] 根据以上视觉方案设计技术方案
- [ ] 设计前端页面架构
- [ ] 创建独立的HTML文件，引入相关库
- [ ] 实现虫洞穿越效果（时间旅行）
- [ ] 事件展示为虫洞界面上的圆点，当前时期按地区展示在屏幕左和右，圆点也按地区左右分布，半径与事件影响力有关
- [ ] 点击圆点展示事件详情（概述、影响、分类等）卡片
- [ ] 样式和交互优化

   ## 当前状态
  - 阶段一：已完成
  - 阶段二：已完成
  - 阶段三：已完成
  - 阶段四：已完成
  - 阶段五：待开始

   ## 最后更新
  - 2026-01-16: 创建任务清单，准备开始阶段一
  - 2026-01-16: 完成阶段一，创建Notebook并建立数据库表结构
  - 2026-01-16: 完成阶段二，添加数据抓取、LangChain处理和数据库存储代码
  - 2026-01-16: 完成阶段三，封装可复用模块（wikipedia_scraper.py, langchain_processor.py, database_manager.py, timeline_generator.py），支持多地区生成，编写完整使用文档
  - 2026-01-19: 完成阶段四，实现增强型数据库查询功能（分页、高级搜索、跨地区对比、重要性筛选）和自然语言查询引擎
