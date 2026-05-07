"""
数据库连接诊断脚本
测试各种可能的 MySQL 连接方式
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from urllib.parse import quote_plus

# 尝试不同的连接方式
test_cases = [
    {
        "name": "localhost:3306 (default)",
        "url": "mysql+pymysql://root:Cainiao%40123@localhost:3306",
    },
    {
        "name": "127.0.0.1:3306",
        "url": "mysql+pymysql://root:Cainiao%40123@127.0.0.1:3306",
    },
    {
        "name": "host.docker.internal:3306 (Docker/Podman)",
        "url": "mysql+pymysql://root:Cainiao%40123@host.docker.internal:3306",
    },
    {
        "name": "localhost:3307",
        "url": "mysql+pymysql://root:Cainiao%40123@localhost:3307",
    },
    {
        "name": "127.0.0.1:3307",
        "url": "mysql+pymysql://root:Cainiao%40123@127.0.0.1:3307",
    },
]

try:
    import pymysql
except ImportError:
    print("pymysql not installed. Run: pip install pymysql")
    sys.exit(1)

print("=" * 60)
print("  MySQL Connection Diagnostic")
print("=" * 60)
print()

for case in test_cases:
    try:
        conn = pymysql.connect(
            host=case["url"].split("@")[1].split(":")[0] if "@" in case["url"] else "localhost",
            port=3306,
            user="root",
            password="Cainiao@123",
            connect_timeout=3,
        )
        print(f"  [OK] {case['name']} - Connected!")
        conn.close()
    except pymysql.err.OperationalError as e:
        code = e.args[0] if e.args else "?"
        print(f"  [FAIL] {case['name']} - Error {code}: {e.args[1] if len(e.args) > 1 else e}")
    except Exception as e:
        print(f"  [FAIL] {case['name']} - {type(e).__name__}: {e}")

print()
print("*" * 60)
print("  TROUBLESHOOTING TIPS:")
print("  1. Is Podman/Docker running?")
print("     > podman ps")
print("     > docker ps")
print("  2. MySQL container port mapping?")
print("     Look for '0.0.0.0:XXXX->3306/tcp'")
print("  3. Windows firewall blocking port?")
print("  4. Try connecting from inside the container:")
print("     > podman exec -it <container_name> mysql -u root -p")
print("*" * 60)
