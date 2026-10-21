import json,sys,math
from pathlib import Path
D=json.loads(Path(sys.argv[1]).read_text())
assert D['scope']=='SYNTHETIC_C3D20R_FIXED_COUNT_LOCATION_COMPARATOR_NOT_DESIGN'
assert D['engineering_acceptance']=='NOT_ADMITTED'
assert len(D['cases'])==8
assert set(D['sha256'])=={'four','five','moved'}
seen=set()
lines=['# C3D20R 合成連接配置比較｜固定站點數','', '**工程驗收：NOT_ADMITTED；僅限合成雙向 Z 彈簧研究。**','', '| 網格 | 配置 | k (N/mm/點) | 原 U3 (mm) | 外移 U3 (mm) | 變化 (%) |','|---|---|---:|---:|---:|---:|']
for c in sorted(D['cases'],key=lambda c:(c['mesh'],c['layout'],c['k_per_station_n_per_mm'])):
 key=(c['mesh'],c['layout'],c['k_per_station_n_per_mm']);assert key not in seen;seen.add(key)
 assert c['mesh'] in (8,16) and c['layout'] in ('four_inner_out','five_inner_out') and c['k_per_station_n_per_mm'] in (50,500)
 a,b=c['baseline'],c['moved']
 for x in (a,b):
  assert x['center_u3_mm']>0 and math.isfinite(x['center_u3_mm'])
  assert abs(x['rib_reaction_residual_n'])<.002 and abs(x['nominal_global_z_residual_n'])<.002
  assert len(x['station_forces_n'])==c['station_count']
 assert abs((b['center_u3_mm']/a['center_u3_mm']-1)*100-c['center_u3_relative_change_percent'])<1e-5
 lines.append(f"| n{c['mesh']} | {c['layout']} | {c['k_per_station_n_per_mm']:.0f} | {a['center_u3_mm']:.8f} | {b['center_u3_mm']:.8f} | {c['center_u3_relative_change_percent']:+.2f} |")
lines += ['', '## 原始證據 SHA-256','']+[f'- {k}: `{v}`' for k,v in sorted(D['sha256'].items())]+['','此報表未驗證鋁植釘、焊接、剪力、接觸、實際支承或工程容量。','']
sys.stdout.write('\n'.join(lines))
