/** Fixed public synthetic Stage 59 observation only, NOT parameterized FEA. */
export const FIXED_SYNTHETIC = Object.freeze({
  title:'Stage 59／PR #96：共節點中心直肋（非 U 型肋）',
  geometry:'100 × 100 × 2 mm；四邊理想固定；n=16 S8R',
  material:'合成 E=69000 MPa、ν=0.33',
  pressure:'合成均布面壓 0.0001 N/mm²',
  sourceRepo:'masini1491/building-envelope-engineering-kb',
  sourceRevision:'b52d29e5d725b54611a08479e1d58d8488cf37cb',
  sourcePath:'TASKS.md',
  ribHeightsMm:Object.freeze([0,4,8]),
  centerDeflectionMm:Object.freeze([0.0002382199,0.0001840568,0.0001079533]),
  engineeringAcceptance:'NOT_ADMITTED'
});
