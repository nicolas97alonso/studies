from src.linked_list.exercises import find_middle_node
from src.linked_list.ll import LinkedList

import pytest


def test_middle_node():
    nodes = [1, 2, 3, 4, 5]
    ll = LinkedList()
    for i in nodes:
        ll.append(i)
    assert find_middle_node(ll).value == 3


def test_middle_node_empty():
    ll = LinkedList()
    assert find_middle_node(ll) == None


def test_middle_node_next():
    nodes = [2, 3, 4, 5]
    ll = LinkedList()
    for i in nodes:
        ll.append(i)
    assert find_middle_node(ll).value == 4


def test_middle_node_one():
    ll = LinkedList(1)
    assert find_middle_node(ll).value == 1
