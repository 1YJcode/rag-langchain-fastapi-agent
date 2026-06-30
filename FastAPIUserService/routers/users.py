from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from FastAPIUserService.models.users import User
from FastAPIUserService.schemas.users import UserAutResponse, UserChangePasswordResponse, UserInfoResponse, UserRequest, UserUpdateRequest
from FastAPIUserService.config.db_config import get_db
from FastAPIUserService.crud.users import change_password, get_user_by_username, create_user, create_token, update_info
from FastAPIUserService.utils.security import verify_password
from starlette import status
from FastAPIUserService.utils.auth import get_current_user
from FastAPIUserService.utils.success_response import success_response
from FastAPIUserService.utils.upload_avatar import upload_avatar_orm



router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def register_user(user_data: UserRequest, db=Depends(get_db)):

    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")

    user = await create_user(db, user_data)

    token = await create_token(db, user.id)

    # return {
    #     "code": 200,
    #     "message": "User registered successfully",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "user_id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }
    response_data = UserAutResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login_user(user_data: UserRequest, db=Depends(get_db)):
    user = await get_user_by_username(db, user_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="密码错误")

    token = await create_token(db, user.id)
    # return {
    #     "code": 200,
    #     "message": "登录成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "user_id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }
    response_data = UserAutResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="用户信息获取成功", data=UserInfoResponse.model_validate(user))


# 修改用户信息：验证Token → 更新（用户输入数据 put提交数据 → 请求体参数 → 定义Pydantic模型类) → 响应结果
# 参数：用户输入的 + 验证Token的 + db (调用更新的方法)
@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    updated_user = await update_info(db, user_data, user.username)
    return success_response(message="更新用户成功", data=UserInfoResponse.model_validate(updated_user))



# 更新用户密码
@router.put("/password")
async def update_user_password(
    password_data: UserChangePasswordResponse,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await change_password(db, user, password_data)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
    
    return success_response(message="修改密码成功")




@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_data = await upload_avatar_orm(file)
    updated_user = await update_info(db, user_data, user.username)

    return success_response(message="头像上传成功", data=UserInfoResponse.model_validate(updated_user))
