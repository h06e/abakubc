import time

def pylog(message):
    date=time.strftime("%d-%m %H:%M:%S")
    car=date+'@'+__name__+': '+message
    print(car)
    return

def fc():
    pylog('Message from module')
    return