"""Script to mark t_nl_gastro_finish as 'done' in both tirol-cicd databases."""
import sqlite3
import datetime

now = datetime.datetime.now().timestamp()
databases = [
    r"C:\HermesPortable\home\spaces\tirol-tourismus\kanban\boards\tirol-cicd\kanban.db",
    r"C:\HermesPortable\home\kanban\boards\tirol-cicd\kanban.db",
]

for p in databases:
    conn = sqlite3.connect(p)
    # Update the task
    conn.execute("UPDATE tasks SET status=? WHERE id=?", ("done", "t_nl_gastro_finish"))
    # Verify
    row = conn.execute("SELECT id, status FROM tasks WHERE id=?", ("t_nl_gastro_finish",)).fetchone()
    print(f"{p}: {row}")
    conn.commit()
    conn.close()
