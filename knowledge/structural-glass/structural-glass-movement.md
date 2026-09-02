---
title: "結構玻璃位移相容性"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 結構玻璃位移相容性

## Scope

結構玻璃系統除風壓強度外，還必須處理樓層側移、垂直層間位移、thermal movement、support rotation 與 construction tolerance。

## Recommended workflow

1. 定義 imposed movement：horizontal drift / vertical differential movement / thermal movement。
2. 建立支承自由度：fixed、sliding、rotational、bearing、slotted connection 等。
3. 檢查玻璃與玻璃、玻璃與金屬、孔洞與 fitting 之 clearances。
4. 以 global model 檢查 movement-induced stress / reaction。
5. 必要時另外做 local hole / bearing / sealant deformation check。
6. 極限或 seismic condition 下再確認 glass fallout、contact、support disengagement 與 residual stability。

## Clearance vs stress

只做「joint gap 大於 imposed movement」的幾何檢查不一定足夠；也只做 FEA stress check 而不檢查 physical clearance 也不完整。

應同時確認：

- joint closure / opening
- glass edge contact
- fitting / bolt contact
- sealant strain
- support rotation
- connection slot travel
- secondary stress

## Support restraint guard

減少拘束有時可降低 movement-induced secondary stress，但不得因此省略 stability / redundancy。增加固定點也可能提高 unintended restraint。

因此 support philosophy 應同時滿足：

`load transfer + stability + movement accommodation + constructability`

## Inter-story standards routing

一般 curtain-wall movement 可參考 AAMA/FGIA 501.4、501.6、501.7 等相應方法；結構玻璃若有特殊 geometry / point supports，仍需 project-specific analysis，不能只因整體 mock-up movement PASS 就自動推定每個 local glass connection PASS。

## Do not assume

- joint clearance check = full seismic design
- flexible silicone = unlimited movement capacity
- slot length = usable movement without considering bolt position / washer / edge distance
- one imposed-displacement model covers all thermal and seismic combinations

> 本頁提供 movement-design routing，不指定任何 project-specific drift ratio、gap 或 acceptance value。