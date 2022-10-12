#!/usr/bin/env python3

'''
This server wait for a calculator and then run random
operations checking the responses.
'''

import logging
import operator
import random
import sys
from dataclasses import dataclass, field
from math import isclose
from queue import PriorityQueue
from threading import Thread
from typing import Any

import Ice

try:
    import SSDD
except ImportError:
    Ice.loadSlice("Calculator.ice")
    import SSDD


class Tester(SSDD.CalculatorTester):
    """Implementation of the Tester interface."""

    def __init__(self, queue):
        self.queue = queue

    def test(self, calculator: SSDD.CalculatorPrx, current: Ice.Current = None):
        """Test a new calculator"""
        self.queue.add(calculator)


class WorkQueue(Thread):
    """Job for a calculator"""
    QUIT = "QUIT"
    CANCEL = "CANCEL"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = PriorityQueue()

    def add(self, calculator: SSDD.Calculator):
        """New calculator servant is available"""
        if not calculator:
            logging.warning("Received a None calculator. Ignoring")
            return

        ops = [
            (calculator.sum, operator.add),
            (calculator.sub, operator.sub),
            (calculator.mult, operator.mul),
            (calculator.div, operator.truediv),
        ]

        for remote_op, local_op in ops:
            priority = random.randint(1, 10)
            opA = random.uniform(0.01, 10.0)
            opB = random.uniform(0.01, 10.0)
            expected = local_op(opA, opB)
            job = Job(priority, remote_op, opA, opB, expected)
            self.queue.put(job)

        # Add an specific job for testing the exception
        priority = random.randint(1, 10)
        opA = random.uniform(0.01, 10.0)
        opB = 0.0
        job = Job(priority, calculator.div, opA, opB, SSDD.ZeroDivisionError())
        self.queue.put(job)
        # self.queue.put(WorkQueue.QUIT)

    def run(self):
        for job in iter(self.queue.get, WorkQueue.QUIT):
            success = job.execute()
            if success:
                logging.info("%s worked!!!", job)
            else:
                logging.error("%s misbehaved!!!", job)

        self.queue.task_done()


@dataclass(order=True)
class Job:
    """Run a single operation, checking the results"""
    priority: int
    op: Any = field(compare=False)

    def __init__(self, priority, operation, opA, opB, expected):
        self.priority = priority
        self.op = operation
        self.left = opA
        self.right = opB
        self.expected = expected

    def execute(self):
        if isinstance(self.expected, SSDD.ZeroDivisionError):
            try:
                self.op(self.left, self.right)
                return False

            except SSDD.ZeroDivisionError:
                return True

            except Exception as ex:
                logging.error("It shouldn't happen: %s", ex)
                return False

        else:
            result = self.op(self.left, self.right)
            retval = isclose(result, self.expected, rel_tol=1e-5)
            if not retval:
                logging.debug("Op: %s, Result: %s, Expected: %s",
                              self.op, result, self.expected)
            return retval

    def __str__(self):
        return f"Op {self.op.__name__}({self.left}, {self.right})"


class Server(Ice.Application):
    """Implementation of the server main startup."""

    def run(self, args: list) -> int:
        """Initialize the Ice environment and setup the servants."""
        broker = self.communicator()
        adapter = broker.createObjectAdapterWithEndpoints(
            "TesterAdapter", "tcp")
        adapter.activate()

        working_queue = WorkQueue(daemon=True)
        servant = Tester(working_queue)

        prx = adapter.add(servant, broker.stringToIdentity("tester"))
        print(f'The proxy of the tester is "{prx}"')

        self.shutdownOnInterrupt()
        working_queue.start()
        broker.waitForShutdown()

        return 0


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    server = Server()
    sys.exit(server.main(sys.argv))
