---
title: "帷幕牆水管理（Water Management）"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
---

# 帷幕牆水管理（Water Management）

本目錄整理 curtain wall / building-envelope 的雨水侵入、pressure equalization、rainscreen、drainage 與 weep design 方法。

核心原則：**水密不是單一 sealant line 的問題，而是「水源 + 路徑 + 驅動力 + 排水／排壓策略」的系統問題。**

## 建議讀取順序

1. [`water-ingress-mechanisms.md`](water-ingress-mechanisms.md) — 先辨識水如何移動。
2. [`pressure-equalization-and-rainscreen.md`](pressure-equalization-and-rainscreen.md) — 再判斷 pressure equalization / rainscreen 是否真的成立。
3. [`drainage-and-weep-design.md`](drainage-and-weep-design.md) — 最後建立可排出的 drainage path。
4. [`../standards/performance-testing/curtain-wall-performance-crosswalk.md`](../standards/performance-testing/curtain-wall-performance-crosswalk.md) — 用 laboratory / field test 驗證系統性能。

## 系統思考

水密 review 建議依下列順序：

`water exposure`
→ `opening / discontinuity / joint`
→ `driving force`
→ `primary rain barrier`
→ `pressure-moderation cavity`
→ `air seal / inner barrier`
→ `collection path`
→ `drainage / weep outlet`
→ `field / laboratory validation`

## 重要防呆

- `有排水孔 = 水密設計完成`：錯誤。
- `有空腔 = pressure equalized`：錯誤。
- `外層填縫越密越好`：不一定；若系統原本依靠 pressure moderation / drainage，錯誤封堵可能改變設計機制。
- `等壓 = 沒有水進入空腔`：錯誤；良好的 rainscreen system 通常仍須處理少量進水並安全排出。
- `mock-up PASS = 所有施工位置自動 PASS`：錯誤；現場 workmanship、joint continuity、weep blockage 與 interface detail 仍可能控制。

## 公開來源 routing

- [`../../references/government/abri-metal-curtain-wall-design-manual-2003.md`](../../references/government/abri-metal-curtain-wall-design-manual-2003.md)
- [`../../references/government/nist-envelope-rain-penetration-and-pressure-equalization.md`](../../references/government/nist-envelope-rain-penetration-and-pressure-equalization.md)
- [`../../references/standards/aama-508-21-pressure-equalized-rainscreen.md`](../../references/standards/aama-508-21-pressure-equalized-rainscreen.md)

> 本目錄提供水管理 methodology，不提供 universal weep size、chamber ratio、opening ratio、test pressure 或 water-head dimension。