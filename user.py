class User:
    accessToken: str
    expiresIn: int
    refreshToken: str
    userId: str

    def __init__(
        self,
        accessToken: str,
        expiresIn: int,
        refreshToken: str,
        userId: str,
    ):
        self.accessToken = accessToken
        self.expiresIn = expiresIn
        self.refreshToken = refreshToken
        self.userId = userId
