# 第三方權利聲明

本 repository 為工程研究與可追溯性目的，會引用標準、出版物、製造商、組織、政府文件與其他外部來源。

## 不重新授權第三方作品

本 repository 的授權（原創文件／知識採 `CC BY 4.0`；原創 schemas／scripts／code 採 `MIT`）只適用於 repository maintainer 有權授權的內容。

這些授權**不會額外授予**重製、再散布、改作、販售或以其他方式利用第三方作品的權利；第三方作品仍依適用法律及原權利人的授權／使用條款處理。

第三方內容可能包括但不限於：

- ASTM standards and publications
- CNS 標準
- ISO standards
- AAMA / FGIA standards and publications
- Aluminum Association publications
- AWS / AISC publications
- 製造商 technical literature、evaluation reports、test reports、product data、trademarks 與 logos
- 受自身再利用條款規範的政府出版物
- 他人擁有的研究論文、圖、表、照片、diagram 或 quotation

## 儲存庫（Repository）自行撰寫的摘要與 metadata

本 repository 自行撰寫的摘要、分類、routing notes、工程評論與 metadata，可依 repository 的文件授權使用；但這不會移轉或重新授權底層第三方來源的權利。

例如 repository 自行整理「ASTM E330 可作為 uniform static air pressure 結構性能試驗的 routing reference」這類工程說明，可屬於 repository 的原創 commentary；但 ASTM 標準原文仍是第三方作品。


## 可選數值 backend dependency

二維熱橋 numerical kernel 透過獨立 optional dependency set 使用下列第三方 Python 套件；repository 不 vendor 其原始碼：

- `NumPy 2.5.3` — BSD 3-Clause-style license；copyright 依 upstream `LICENSE.txt`。
- `SciPy 1.18.1` — BSD 3-Clause-style license；copyright 依 upstream `LICENSE.txt`。
- `scikit-fem 12.0.2` — BSD-3-Clause；copyright 2018–26 scikit-fem developers。

這些套件只作 numerical backend／scientific-computing dependency；其授權不改變本 repository 自有 code/document 的授權，也不代表 NumPy、SciPy 或 scikit-fem 對本 repository 的 endorsement。

## 非線性 FEA 公開範例的權利與隔離

`tests/fea_benchmark/shell90/mesh.fbd` 和 `shell90.inp` 衍生自
`calculix/CalculiX-Examples` 的 `Streifen/sh.fbd` 與 `Streifen/sh.inp`
（commit `316273e9105e44ce7e3ee05059dac1bc3f256a69`）。

Copyright (c) 2017 Martin Kraska

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

另，CI 以 Ubuntu apt 安裝的 CalculiX `ccx`／`cgx` 軟體仍各受其 upstream
授權約束，沒有複製或附帶分發這些求解器二進位檔，也不因此將其 GPL
授權誤當成 MIT。

## 商標

ASTM、ISO、CNS、AAMA、FGIA 及製造商名稱等名稱與標誌，只用於識別與引用。除非相關權利人明確表示，否則不代表 sponsorship、endorsement、affiliation 或 ownership。

## 取得來源

使用者應從適用的 publisher、主管機關、manufacturer 或合法授權來源取得標準及 proprietary technical documents，並遵守其使用條款。

若發現本 repository 出現不應公開的第三方內容或 attribution 錯誤，請提出 issue 供維護者檢查。