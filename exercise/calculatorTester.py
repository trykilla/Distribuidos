#!/usr/bin/env python3

import sys
import Ice
Ice.loadSlice("Calculator.ice")
import SSDD

class Cliente(Ice.Application):
    def run(self, argv):
        comm = self.communicator()
       
        
        if not calc:
            print("Error en el proxy")
            return -1
        
         
        return 0

    

if __name__ == "__main__":
    cliente = Cliente()
    sys.exit(cliente.main(sys.argv))