from pathlib import Path
import subprocess, sys

def test_generator_writes_csv():
    root = Path(__file__).resolve().parents[1]
    csv_path = root / "data" / "processed" / "alpha_max_vs_x_mass_dependent.csv"
    if csv_path.exists():
        csv_path.unlink()
    r = subprocess.run([sys.executable, str(root/"scripts"/"generate_data.py")], cwd=root, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    head = csv_path.read_text(encoding="utf-8").splitlines()[0]
    cols = [c.strip().lower() for c in head.split(",")]
    assert "x" in cols and "alpha_max" in cols
