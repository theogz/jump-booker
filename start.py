from booker import app, socket

if __name__ == '__main__':
    socket.run(app, host='localhost', port='4999')
