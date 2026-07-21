---
categories:
- 会用电脑
date: 2025-11-04
draft: false
slug: 20251104-01
tags: []
title: 在excel中用行号、列的序号来获取单元格的值
---

**用行号与列序号获取单元格值的常用方法**​

- ​**INDEX**​ 函数按“区域内的第几行、第几列”取值，语法：`=INDEX(array, row_num, [column_num])`。其中 ​**row\_num、column\_num**​ 是相对于 array 的位置（从 ​**1**​ 开始）。例如：`=INDEX(A1:D10, 3, 2)`取 A1:D10 区域中第 ​**3**​ 行、第 ​**2**​ 列的值。若区域只有一行或一列，可省略相应参数；将列参数设为 ​**0**​ 可返回整行，行参数设为 ​**0**​ 返回整列（旧版需用 Ctrl+Shift+Enter 作为数组公式，Microsoft 365 直接回车即可）。

- ​**INDIRECT + ADDRESS**​ 组合用“绝对地址文本”取值，语法思路：先用 `ADDRESS(row_num, col_num)`生成如 ​**​_B_5**​ 的地址文本，再用 `INDIRECT`解析为引用。例如：`=INDIRECT(ADDRESS(5, 2))`取第 ​**5**​ 行第 ​**2**​ 列（即 B5）的值；若行号、列号存放在单元格中（如 ​**F4、F5**），可写：`=INDIRECT(ADDRESS(F4, F5))`。注意 ADDRESS 可返回 A1 或 R1C1 样式，且可包含工作表名；INDIRECT 为易挥发函数，大数据量时可能影响性能。

- ​**OFFSET**​ 从基点按偏移量取值，语法：`=OFFSET(reference, rows, cols, [height], [width])`。例如从 ​**A1**​ 开始，向下偏移 ​**2**​ 行、向右偏移 ​**1**​ 列：`=OFFSET(A1, 2, 1)`得到 ​**B3**；要返回一整行可用：`=OFFSET(A1, 2, 0, 1, 4)`（第 3 行、1 行高、4 列宽）。适合动态偏移场景，但引用会随偏移变化，需注意稳定性。

​**实用示例**​

- 已知行号在 ​**F2**、列号在 ​**F3**​（数值为 ​**5**​ 和 ​**2**）：
    - 取值（INDEX）：`=INDEX(A1:D10, F2, F3)`，等价于取 A1:D10 的第 5 行第 2 列。
    
    - 取值（INDIRECT+ADDRESS）：`=INDIRECT(ADDRESS(F2, F3))`，等价于取第 5 行第 2 列。
    
    - 取整行（INDEX）：`=INDEX(A1:D10, F2, 0)`（返回第 5 行的整行数据）。
    
    - 取整列（INDEX）：`=INDEX(A1:D10, 0, F3)`（返回第 2 列的整列数据）。

​**注意事项与小技巧**​

- ​**行号与列号从 1 开始**​：在 INDEX 的 array 范围内计数；超出范围会返回 ​**​#REF**。如需行列序号来自单元格，直接引用即可（如 `=INDEX(A1:D10, F2, F3)`）。

- ​**INDEX 返回整行/整列**​：将列（或行）参数设为 ​**0**；Microsoft 365 直接回车返回溢出数组，旧版可能需要 Ctrl+Shift+Enter。

- ​**动态列字母场景**​：如果“列序号”是字母（如“C”），可先转列号：`=COLUMN(INDIRECT(F3&1))`，再代入：`=INDEX(A1:D10, F2, COLUMN(INDIRECT(F3&1)))`。

- ​**性能建议**​：避免在大表中大量使用 ​**INDIRECT**​（易挥发）；能用 ​**INDEX**​ 尽量用 INDEX，或用 ​**INDEX+MATCH**​ 做动态查找更稳更高效。

​**进阶 VBA 自定义函数**​

- 在 VBA 中可封装一个按“行号、列号”取值的函数：
    1. 按 ​**Alt+F11**​ 打开 VBA 编辑器 → 插入模块；
    
    3. 粘贴代码：复制`Function GetValueByRowCol(row As Long, col As Long, Optional ws As Worksheet) As Variant If ws Is Nothing Then Set ws = ActiveSheet GetValueByRowCol = ws.Cells(row, col).Value End Function`
    
    5. 工作表中直接用：`=GetValueByRowCol(6, 3)`（取第 ​**6**​ 行第 ​**3**​ 列）；也可指定表：`=GetValueByRowCol(6,3,Sheet2)`。