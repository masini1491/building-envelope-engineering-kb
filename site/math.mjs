/** Nominal geometry ONLY. Sharp-corner unfolded U: no bend-radius allowance. */
const finite = value => typeof value === 'number' && Number.isFinite(value);

export function evaluate(input) {
  const { length, width, plateThickness, ribWidth, ribHeight, ribThickness, ribCount } = input;
  const values = [length, width, plateThickness, ribWidth, ribHeight, ribThickness];
  if (!values.every(v => finite(v) && v > 0) ||
      !Number.isInteger(ribCount) || ribCount < 0 || ribCount > 100 ||
      values.some(v => v > 100000) ||
      plateThickness >= Math.min(length,width) ||
      ribThickness * 2 >= ribWidth || ribThickness >= ribHeight) {
    throw new RangeError('尺寸超出名目幾何範圍；請確認厚度、U 肋內淨寬與肋數。');
  }
  const plateVolumeMm3 = length * width * plateThickness;
  // U bottom plate (b*t) plus two webs above the bottom (2*(h-t)*t).
  const ribAreaMm2 = ribCount ? ribThickness * (ribWidth + 2 * (ribHeight - ribThickness)) : 0;
  const ribsVolumeMm3 = length * ribAreaMm2 * ribCount;
  const totalVolumeMm3 = plateVolumeMm3 + ribsVolumeMm3;
  return Object.freeze({
    plateVolumeMm3, ribAreaMm2, ribsVolumeMm3, totalVolumeMm3,
    plateVolumeCm3: plateVolumeMm3/1000,
    ribsVolumeCm3: ribsVolumeMm3/1000,
    totalVolumeCm3: totalVolumeMm3/1000,
    ribFractionPercent: 100*ribsVolumeMm3/totalVolumeMm3,
  });
}
export function compare(a,b) {
  const x=evaluate(a), y=evaluate(b);
  return { a:x, b:y, deltaCm3:y.totalVolumeCm3-x.totalVolumeCm3,
    deltaPercent: 100*(y.totalVolumeMm3/x.totalVolumeMm3-1) };
}
