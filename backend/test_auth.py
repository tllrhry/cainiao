"""
认证模块快速验证脚本
用法：python test_auth.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("  认证模块验证")
print("=" * 50)

# 1. 导入检查
print("\n[1/5] 模块导入...")
try:
    from app.schemas.common import BaseResponse
    from app.schemas.auth import LoginRequest, TokenData, UserInfo
    from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token
    from app.crud.auth import authenticate_user, get_user_by_username, get_user_by_id
    from app.deps.security import get_current_user, require_admin
    from app.api.v1.routers.auth import router
    print("  ✅ 所有模块导入成功")
except Exception as e:
    print(f"  ❌ 导入失败: {e}")
    sys.exit(1)

# 2. 密码哈希/验证
print("\n[2/5] 密码哈希验证...")
hashed = hash_password("test123")
assert verify_password("test123", hashed), "密码验证失败"
assert not verify_password("wrong", hashed), "错误密码不应通过"
print("  ✅ 密码哈希/验证正常")

# 3. JWT 生成/解码
print("\n[3/5] JWT 令牌生成/解码...")
token = create_access_token(data={"sub": 1, "username": "admin"})
print(f"  Token: {token[:50]}...")
payload = decode_access_token(token)
assert payload["sub"] == "1"  # JWT 规范要求 sub 为字符串
assert int(payload["sub"]) == 1
assert payload["username"] == "admin"
print("  ✅ JWT 生成/解码正常")

# 4. Schema 测试
print("\n[4/5] Pydantic Schema 验证...")
req = LoginRequest(username="admin", password="admin123")
assert req.username == "admin"
assert req.password == "admin123"
print(f"  LoginRequest: username={req.username}, password=******")

token_data = TokenData(access_token="fake-token", expires_in=86400)
assert token_data.token_type == "bearer"
print(f"  TokenData: type={token_data.token_type}, expires_in={token_data.expires_in}s")

# BaseResponse 泛型测试
resp = BaseResponse[TokenData](data=token_data, message="success")
print(f"  BaseResponse: code={resp.code}, message={resp.message}")

print("  ✅ Schema 验证正常")

# 5. 数据库连接测试
print("\n[5/5] 数据库连接 & 用户查询...")
try:
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        user = get_user_by_username(db, "admin")
        if user:
            print(f"  ✅ 找到管理员: {user.username}")
            print(f"     ID: {user.id}, 状态: {'启用' if user.is_active else '禁用'}")
            print(f"     角色: {[r.name for r in user.roles]}")

            # 测试认证
            authed = authenticate_user(db, "admin", "admin123")
            assert authed is not None, "管理员认证失败"
            print(f"  ✅ 管理员认证通过")

            # 错误密码测试
            bad = authenticate_user(db, "admin", "wrong_pass")
            assert bad is None, "错误密码应该返回 None"
            print(f"  ✅ 错误密码正确拒绝")

        else:
            print("  ❌ 未找到管理员账号，请先运行 setup_db.py")
    finally:
        db.close()
except Exception as e:
    print(f"  ❌ 数据库连接失败: {e}")
    print("  请确保 MySQL 正在运行")

print("\n" + "=" * 50)
print("  验证完成！启动后端: python -m uvicorn app.main:app --reload")
print("  API 文档:   http://localhost:8000/docs")
print("=" * 50)
