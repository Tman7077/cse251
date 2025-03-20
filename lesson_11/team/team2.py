"""
Course: CSE 251
Lesson Week: 11
File: team2.py
Author: Brother Comeau

Purpose: Team Activity 2: Queue, Stack

Instructions:

Part 1:
- Create classes for Queue_t and Stack_t that are thread safe.
- You can use the List() data structure in your classes.
- Once written, test them using multiple threads.

Part 2
- Create classes for Queue_p and Stack_p that are process safe.
- You can use the List() data structure in your classes.
- Once written, test them using multiple processes.

Queue methods:
    - constructor(<no arguments>)
    - size()
    - get()
    - put(item)

Stack methods:
    - constructor(<no arguments>)
    - push(item)
    - pop()

Steps:
1) write the Queue_t and test it with threads.
2) write the Queue_p and test it with processes.
3) Implement Stack_t and test it 
4) Implement Stack_p and test it 

Note: Testing means having lots of concurrency/parallelism happening.  Also
some methods for lists are thread safe - some are not.
"""

import time
import threading
import multiprocessing as mp

# -------------------------------------------------------------------
class Queue_t:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def size(self):
        with self.lock:
            return len(self.queue)

    def get(self):
        with self.lock:
            if self.queue:
                return self.queue.pop(0)
            return None

    def put(self, item):
        with self.lock:
            self.queue.append(item)


# -------------------------------------------------------------------
class Stack_t:
    def __init__(self):
        self.stack = []
        self.lock = threading.Lock()

    def push(self, item):
        with self.lock:
            self.stack.append(item)

    def pop(self):
        with self.lock:
            if self.stack:
                return self.stack.pop()
            return None


# -------------------------------------------------------------------
class Queue_p:
    def __init__(self):
        self.queue = mp.Manager().list()

    def size(self):
        return len(self.queue)

    def get(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def put(self, item):
        self.queue.append(item)


# -------------------------------------------------------------------
class Stack_p:
    def __init__(self):
        self.stack = mp.Manager().list()

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None


def test_queue_t():
    queue = Queue_t()

    def producer():
        for i in range(10):
            queue.put(i)
            time.sleep(0.01)

    def consumer():
        for _ in range(10):
            item = queue.get()
            print(f"Queue_t Consumer got: {item}")
            time.sleep(0.02)

    threads = []
    for _ in range(2):
        t = threading.Thread(target=producer)
        threads.append(t)
        t.start()

    for _ in range(2):
        t = threading.Thread(target=consumer)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


def test_stack_t():
    stack = Stack_t()

    def producer():
        for i in range(10):
            stack.push(i)
            time.sleep(0.01)

    def consumer():
        for _ in range(10):
            item = stack.pop()
            print(f"Stack_t Consumer got: {item}")
            time.sleep(0.02)

    threads = []
    for _ in range(2):
        t = threading.Thread(target=producer)
        threads.append(t)
        t.start()

    for _ in range(2):
        t = threading.Thread(target=consumer)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


def test_queue_p():
    queue = Queue_p()

    def producer():
        for i in range(10):
            queue.put(i)
            time.sleep(0.01)

    def consumer():
        for _ in range(10):
            item = queue.get()
            print(f"Queue_p Consumer got: {item}")
            time.sleep(0.02)

    processes = []
    for _ in range(2):
        p = mp.Process(target=producer)
        processes.append(p)
        p.start()

    for _ in range(2):
        p = mp.Process(target=consumer)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()


def test_stack_p():
    stack = Stack_p()

    def producer():
        for i in range(10):
            stack.push(i)
            time.sleep(0.01)

    def consumer():
        for _ in range(10):
            item = stack.pop()
            print(f"Stack_p Consumer got: {item}")
            time.sleep(0.02)

    processes = []
    for _ in range(2):
        p = mp.Process(target=producer)
        processes.append(p)
        p.start()

    for _ in range(2):
        p = mp.Process(target=consumer)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()


def main():
    print("Testing Queue_t with threads")
    test_queue_t()
    print("\nTesting Stack_t with threads")
    test_stack_t()
    print("\nTesting Queue_p with processes")
    test_queue_p()
    print("\nTesting Stack_p with processes")
    test_stack_p()


if __name__ == '__main__':
    main()
