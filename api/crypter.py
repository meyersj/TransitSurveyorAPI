from keyczar import keyczar

class Crypter(object): 
    crypter = None 
     
    def __init__(self, keys): 
        #TODO verify keys file exist and handle errors with reading keys 
        self.crypter = keyczar.Crypter.Read(keys) 
 
    def Encrypt(self, message): 
        return self.crypter.Encrypt(message) 
 
    def Decrypt(self, cipher): 
        return self.crypter.Decrypt(cipher)

