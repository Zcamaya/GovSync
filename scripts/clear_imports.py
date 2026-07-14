import sys
from pathlib import Path

# ensure project root is on sys.path so local packages import correctly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storage.sqlite import connect

"""
Simple script to delete all payroll imports and payroll records.
Run from the project root using the project's venv Python.
"""

if __name__ == "__main__":
    conn = connect()
    cur = conn.cursor()
    print("Deleting payroll_records...")
    cur.execute("DELETE FROM payroll_records")
    print("Deleting payroll_imports...")
    cur.execute("DELETE FROM payroll_imports")
    conn.commit()
    # optional vacuum to reclaim space
    try:
        print("Vacuuming database...")
        cur.execute("VACUUM")
    except Exception:
        pass
    conn.close()
    print("Done. All payroll imports and records removed.")
