from typing import Any


class Node:
    value: Any
    next: "Node | None"

    def __init__(self, value: Any) -> None:
        self.value = value
        self.next = None


class LinkedList:
    head: Node | None
    tail: Node | None
    length: int

    def __init__(self, value: Any | None = None) -> None:
        if value is not None:
            new_node = Node(value)
            self.head = new_node
            self.tail = new_node
            self.length = 1
        else:
            self.head = None
            self.tail = None
            self.length = 0

    def print_list(self) -> None:
        temp = self.head
        while temp is not None:
            print(temp.value)
            temp = temp.next

    def append(self, value: Any) -> bool:
        new_node = Node(value)
        if self.length == 0:
            self.head = new_node
            self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            self.tail = new_node

        self.length += 1
        return True

    def pop(self) -> Node | None:
        if self.length == 0:
            return None

        temp = self.head
        prev = self.head

        assert temp is not None
        while temp.next is not None:
            prev = temp
            temp = temp.next

        self.tail = prev
        assert self.tail is not None
        self.tail.next = None
        self.length -= 1

        if self.length == 0:
            self.head = None
            self.tail = None

        return temp

    def prepend(self, value: Any) -> bool:
        new_node = Node(value)
        if self.length == 0:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node

        self.length += 1
        return True

    def pop_first(self) -> Node | None:
        if self.length == 0:
            return None

        assert self.head is not None
        temp = self.head
        self.head = self.head.next
        temp.next = None
        self.length -= 1

        if self.length == 0:
            self.tail = None

        return temp

    def get(self, index: int) -> Node | None:
        if index < 0 or index >= self.length:
            return None

        temp = self.head
        for _ in range(index):
            assert temp is not None
            temp = temp.next

        return temp

    def set_value(self, index: int, value: Any) -> bool:
        temp = self.get(index)
        if temp is not None:
            temp.value = value
            return True
        return False

    def insert(self, index: int, value: Any) -> bool | None:
        if index < 0 or index >= self.length:
            return None

        if index == (index - 1):
            self.append(value)
            return True

        if index == 0:
            self.prepend(value)
            return True

        new_node = Node(value)
        prev = self.get(index - 1)
        assert prev is not None

        new_node.next = prev.next
        prev.next = new_node
        self.length += 1

        return True

    def remove(self, index: int) -> Node | None:
        if index < 0 or index >= self.length:
            return None

        if index == (index - 1):
            return self.pop()

        if index == 0:
            return self.pop_first()

        prev = self.get(index - 1)
        assert prev is not None
        assert prev.next is not None

        temp = prev.next
        prev.next = temp.next
        temp.next = None
        self.length -= 1
        return temp

    def reverse(self) -> None:
        temp = self.head
        self.head = self.tail
        self.tail = temp

        if temp is None:
            return

        before = None

        for _ in range(self.length):
            after = temp.next
            temp.next = before
            before = temp
            temp = after

    def to_list(self) -> list:

        list_values = []
        temp = self.head
        while temp:
            list_values.append(temp.value)
            temp = temp.next

        return list_values
