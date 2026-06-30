import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, ValidationInfo

class UserRequest(BaseModel):
    username: str
    password: str


# 返回的Info类
class UserInfoBase(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    phone: Optional[str] = Field(None, max_length=50, description="电话号码")



# 返回的用户信息体
class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    model_config = ConfigDict(
        from_attributes=True
    )



# 用户认证返回的请求体
class UserAutResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


# 更新用户信息的模型类
class UserUpdateRequest(UserInfoBase):
    pass


# 用户新旧密码请求体
class UserChangePasswordResponse(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=32, alias="newPassword", description="新密码")
    confirm_password: Optional[str] = Field(None, min_length=6, max_length=32, alias="confirmPassword", description="确认新密码")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("new_password")
    def password_complexity(cls, v):
        # 简单规则：必须包含大小写字母 + 数字
        if not re.search(r"[A-Z]", v):
            raise ValueError("新密码必须包含大写字母")
        if not re.search(r"[a-z]", v):
            raise ValueError("新密码必须包含小写字母")
        if not re.search(r"\d", v):
            raise ValueError("新密码必须包含数字")
        return v

    @field_validator("new_password")
    def cannot_same_as_old(cls, v, info: ValidationInfo):
        if "old_password" in info.data and v == info.data["old_password"]:
            raise ValueError("新密码与旧密码不能相同")
        return v

    @field_validator("confirm_password")
    def check_confirm(cls, v, info: ValidationInfo):
        if v is not None and "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("两次输入的密码不一致")
        return v


