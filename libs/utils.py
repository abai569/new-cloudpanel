# 分页
def Pagination(page, limit, dataLen=999):
    if page == 1 or page == 0:
        return 0, limit
    a = int(limit) * int(page)
    if dataLen < int(limit):
        return 0, a
    return a - int(limit), a

def DateTimeToStr(_datetime):
    try:
        return _datetime.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(_datetime)


def md5(str):
    import hashlib
    m2 = hashlib.md5()
    m2.update(str.encode("utf-8"))
    return m2.hexdigest()


if __name__ == '__main__':
    pass