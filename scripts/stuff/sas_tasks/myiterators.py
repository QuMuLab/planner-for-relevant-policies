# -*- coding: utf-8 -*-

class EolStripIterator(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return self

    def next(self):
        return self.iterator.next().rstrip("\n")


class LookaheadIterator(object):
    def __init__(self, iterator):
        self.iterator = iterator
        self.rewind_buffer = [] 

    def __iter__(self):
        return self

    def next(self):
        if self.rewind_buffer:
            return self.rewind_buffer.pop()
        else:
            return self.iterator.next()

    def putback(self, item):
        self.rewind_buffer.append(item)

    def peek(self):
        try:
            result = self.next()
        except StopIteration:
            return None
        self.putback(result)
        return result
