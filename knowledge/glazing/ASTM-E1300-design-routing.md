---
title: "ASTM E1300 建築玻璃耐荷重設計 routing"
standard: "ASTM E1300-24"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# ASTM E1300 建築玻璃耐荷重設計 routing

## 適用範圍

ASTM E1300-24 是建築玻璃 load resistance 的核心 practice。它用於依玻璃種類、厚度、尺寸、支承與載重條件判定玻璃抗載能力；不能由產品標準 C1036 / C1048 / C1172 直接取代。

## 輸入檢核表

使用 E1300 前至少確認：

1. glass construction：monolithic / laminated / insulating glass unit
2. treatment：annealed / heat-strengthened / fully tempered
3. nominal / actual thickness category
4. plate dimensions
5. support condition
6. load type / duration
7. laminated interlayer / IGU configuration as applicable
8. holes / notches / edge condition 是否超出標準一般假設
9. project specification 是否要求更嚴格 criteria

## 工程防呆

- 玻璃厚度不可只看公稱值而忽略標準採用的 thickness category。
- laminated glass 不可把兩片厚度簡單相加後當 monolithic plate。
- IGU 各 lite 的 load sharing 需依 E1300 方法處理，不能自行假設 50/50。
- fully tempered / heat-strengthened 的 treatment effect 應依標準方法，不使用坊間固定倍率。

## 服務性／邊緣淨空

E1300 的 load resistance 判定不等於 curtain wall system 的所有 serviceability 問題均已解決。仍應檢查：

- glass deflection vs bite / gasket engagement
- edge clearance
- setting block / support condition
- contact with frame / pressure plate
- sealant joint deformation
- thermal movement

## 破壞機率／專案判定基準

正式設計時應依 E1300 與 project specification 的採用條件判斷，不得由 AI 自行設定 probability-of-breakage 或安全係數。

## 不可推論事項

- `tempered = 4× strength` 不是可直接代替 E1300 的設計規則。
- `laminated 6+6 = monolithic 12 mm` 不成立。
- `IGU = each lite carries half pressure` 不成立。
- `E1300 PASS = framing / sealant / gasket system PASS` 不成立。

## 主要來源

- ASTM E1300-24, Standard Practice for Determining Load Resistance of Glass in Buildings: https://store.astm.org/e1300-24.html

> 本頁提供 design routing，不取代正式 E1300 計算、玻璃廠技術確認或專案規範。