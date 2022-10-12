#!/usr/bin/env python3


import sys
import Ice

Ice.loadSlice("Calculator.ice")
#pylint: disable=C0413
import SSDD


class CalculadoraServant(SSDD.Calculator):

    def sum(self, a , b, current=None) -> float:  # Suma dos números
        return(a+b)

    def sub(self,a , b , current=None) -> float:  # Resta dos números
        return (a-b)  # Resta dos números

    def mult(self,a , b , current=None) -> float:
        return a*b  # Multiplica dos números

    def div(self,a , b ,current=None) -> float:  # Divide dos números
        try:
            return a/b
        except ZeroDivisionError:
            raise SSDD.ZeroDivisionError()
        

class Server(Ice.Application):
    def run(self, argv):
        comm = self.communicator()
        servant = CalculadoraServant()
        
        adapter = comm.createObjectAdapterWithEndpoints(
            "CalcAdapter", "tcp")
        proxyGenerico = adapter.add(servant, comm.stringToIdentity("calculator"))
        proxyTester = comm.stringToProxy(argv[1])
        
        tester = SSDD.CalculatorTesterPrx.checkedCast(proxyTester)
        calc = SSDD.CalculatorPrx.checkedCast(proxyGenerico)
        
        tester.test(calc)
        
        adapter.activate()
        self.shutdownOnInterrupt()
        comm.waitForShutdown()

        return 0


if __name__ == '__main__':
    server = Server()
    sys.exit(server.main(sys.argv))
