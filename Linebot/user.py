class User:
    """
    __id: 使用者的id\n
    mode:\n 
        0: 輸入競賽名稱\n
    competition: 使用者要參加的競賽
    """
    def __init__(self, user_id : str, mode : int = 0):
        self.__id = user_id
        self.mode = mode
        self.competition = ""

    