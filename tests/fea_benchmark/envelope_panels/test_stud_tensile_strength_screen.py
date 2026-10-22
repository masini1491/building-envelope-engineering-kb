"""Synthetic-only unit and CLI tests for engineer-selected strength formula."""
import json,math,subprocess,sys,tempfile,unittest
from pathlib import Path
from stud_tensile_strength_screen import METHOD,calculate,load_input

def sample():
 return dict(method=METHOD,failure_loads=[90,105,111,120],load_unit="kgf",
  safety_factor=3,failure_modes=["STUD_FRACTURE","WELD_FAILURE","STUD_FRACTURE","STUD_FRACTURE"],
  source_sha256="f"*64)

class Screen(unittest.TestCase):
 def test_sample_statistics_and_units(self):
  out=calculate(sample());sd=math.sqrt(477/3)
  self.assertEqual(out["sample_count"],4)
  self.assertAlmostEqual(out["sample_mean_failure_load"],106.5)
  self.assertAlmostEqual(out["sample_standard_deviation"],sd)
  self.assertAlmostEqual(out["candidate_allowable_load_source_unit"],(106.5-sd)/3)
  self.assertAlmostEqual(out["candidate_allowable_load_n"],(106.5-sd)/3*9.80665)
 def test_newtons(self):
  x=sample();x["load_unit"]="N";o=calculate(x)
  self.assertEqual(o["candidate_allowable_load_n"],o["candidate_allowable_load_source_unit"])
 def test_never_approves_design_or_stiffness(self):
  o=calculate(sample())
  self.assertEqual(o["engineering_acceptance"],"NOT_ADMITTED")
  self.assertEqual(o["connection_stiffness_n_per_mm"],"NOT_ESTABLISHED")
  self.assertEqual(o["characteristic_fractile_or_confidence_bound"],"NOT_ESTABLISHED")
  self.assertEqual(o["failure_mode_counts"]["WELD_FAILURE"],1)
 def test_too_few_samples(self):
  x=sample();x["failure_loads"]=[100];x["failure_modes"]=["OTHER"]
  with self.assertRaisesRegex(ValueError,"SAMPLE_COUNT"):calculate(x)
 def test_bad_load_values(self):
  for v in (0,-1,float("inf"),float("nan"),True):
   x=sample();x["failure_loads"][0]=v
   with self.subTest(v=str(v)),self.assertRaisesRegex(ValueError,"FAILURE_LOAD"):calculate(x)
 def test_bad_safety_factor(self):
  for v in (0,1,-1,True,float("nan")):
   x=sample();x["safety_factor"]=v
   with self.subTest(v=str(v)),self.assertRaisesRegex(ValueError,"SAFETY_FACTOR"):calculate(x)
 def test_method_and_digest(self):
  x=sample();x["method"]="STANDARD_QUALIFIED"
  with self.assertRaisesRegex(ValueError,"METHOD_NOT_EXPLICIT"):calculate(x)
  x=sample();x["source_sha256"]="bogus"
  with self.assertRaisesRegex(ValueError,"SOURCE_HASH"):calculate(x)
 def test_mode_count_and_enum(self):
  x=sample();x["failure_modes"]=["OTHER"]
  with self.assertRaisesRegex(ValueError,"FAILURE_MODES"):calculate(x)
  x=sample();x["failure_modes"][0]="PASS"
  with self.assertRaisesRegex(ValueError,"FAILURE_MODES"):calculate(x)
 def test_schema_extras(self):
  x=sample();x["design_capacity_n"]=888
  with self.assertRaisesRegex(ValueError,"SCHEMA"):calculate(x)
 def test_duplicate_json_and_nonfinite_json(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"a.json";p.write_text('{"method":"x","method":"y"}')
   with self.assertRaisesRegex(ValueError,"DUPLICATE_JSON_KEY"):load_input(p)
   p.write_text('{"data":NaN}')
   with self.assertRaisesRegex(ValueError,"JSON_NONFINITE"):load_input(p)
 def test_real_command_line(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"synthetic.json";p.write_text(json.dumps(sample()))
   script=Path(__file__).with_name("stud_tensile_strength_screen.py")
   res=subprocess.run([sys.executable,"-B",str(script),str(p)],text=True,capture_output=True,timeout=10)
   self.assertEqual(res.returncode,0,res.stderr)
   out=json.loads(res.stdout)
   self.assertEqual(out["engineering_acceptance"],"NOT_ADMITTED")
   self.assertNotIn("f"*64,res.stdout)
   self.assertNotIn("90, 105",res.stdout)
if __name__=="__main__":unittest.main()
