import socket
import _pickle as pickle


class Network:
    """
    class to connect, send and receive information from the server
    hardcode the host attribute to be the server's ip
    """
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = input("[NETWORK] Enter the server ip-address: ")
        self.port = 5555
        self.address = (self.host, self.port)

    def connect(self, name):
        """
        connects to server and returns the id of the client that connected
        :param name: str
        :return: int representing id
        """
        self.client.connect(self.address)
        self.client.send(str.encode(name, 'utf-8'))
        client_id = self.client.recv(8).decode()
        return int(client_id)  # can be int because will be an int id

    def disconnect(self):
        """
        disconnects from the server
        :return: None
        """
        self.client.close()

    def send(self, data, pickle_data=False):
        """
        sends information to the server
        :param data: str
        :param pickle_data: boolean if should pickle or not
        :return: str representing reply of the server
        """
        try:
            if pickle_data:
                self.client.send(pickle.dumps(data))
            else:
                self.client.send(str.encode(data))
            reply = self.client.recv(2048*16)
            try:
                reply = pickle.loads(reply)
            except Exception as error:
                print('[NETWORK]', error)
            return reply
        except socket.error as error:
            print('[NETWORK]', error)
