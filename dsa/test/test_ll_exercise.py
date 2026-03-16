from src.linked_list.exercises import (
    delete_duplicates,
    find_kth_from_end,
    find_middle_node,
    has_loop,
    delete_duplicates,
)
from src.linked_list.ll import LinkedList

import pytest


@pytest.fixture
def ll_base():
    nodes = [2, 3, 4, 5]
    ll = LinkedList()
    for i in nodes:
        ll.append(i)
    return ll

def test_middle_node(ll_base):
    ll_base.append(6)
    assert find_middle_node(ll_base).value == 4


def test_middle_node_empty():
    ll = LinkedList()
    assert find_middle_node(ll) is None


def test_middle_node_next(ll_base):
    assert find_middle_node(ll_base).value == 4


def test_middle_node_one():
    ll = LinkedList(1)
    assert find_middle_node(ll).value == 1


def test_has_loop(ll_base):
    assert has_loop(ll_base) == False
    ll_base.tail.next = ll_base.head
    assert has_loop(ll_base) == True

@pytest.mark.parametrize("k, expected", [
                         (1,5),
                         (3,3),
])
def test_find_kth_end_node(ll_base, k, expected):
    assert find_kth_from_end(ll_base, k).value == expected
    ll_empty = LinkedList()
    assert find_kth_from_end(ll_empty, 3) is None

@pytest.mark.parametrize(
def test_delete_duplcates(ll_base):
    assert 
