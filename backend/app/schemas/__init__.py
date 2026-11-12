from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    confirm_password: str

    @field_validator("name")
    @classmethod
    def strip_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Name is required")
        return v

    @model_validator(mode="after")
    def match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ConvOut(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    last_message_at: str


class MsgOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: str
    sources: list[dict] = []


class ConvDetail(BaseModel):
    conversation: ConvOut
    messages: list[MsgOut]


class RenameIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)

    @field_validator("title")
    @classmethod
    def strip_title(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v


class MessageIn(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    retry_message_id: str | None = None


class ChatOut(BaseModel):
    user_message: MsgOut
    assistant_message: MsgOut
