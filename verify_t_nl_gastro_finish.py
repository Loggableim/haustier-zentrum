"""Script to verify the status of t_nl_gastro_finish in both tirol-cicd databases."""
import sqlite3

databases = [
    r"C:\HermesPortable\home\spaces\tirol-tourismus\kanban\boards\tirol-cicd\kanban.db",
    r"C:\HermesPortable\home\kanban\boards\tirol-cicd\kanban.db",
]

print("=== Current status of t_nl_gastro_finish ===")
for p in databases:
    conn = sqlite3.connect(p)
    row = conn.execute("SELECT id, status FROM tasks WHERE id=?", ("t_nl_gastro_finish",)).fetchone()
    print(f"  {p}:")
    if row:
        print(f"    id={row[0]!r}, status={row[1]!r}")
    else:
        print(f"    Task not found!")
    conn.close()
print("=== Done ===")
