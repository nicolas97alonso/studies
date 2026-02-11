from typing import Any, Optional


class Node:
    def __init__(self, value: Any):
        self.value: Any = value
        self.next: Optional["Node"] = None


class LinkedList:
    def __init__(self, value: Optional[Any] = None):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self.lenght: int = 0

        if value is not None:
            new_node = Node(value)
            self.head = new_node
            self.tail = new_node
            self.lenght = 1

    def print_list(self) -> None:
        temp: Optional[Node] = self.head
        while temp is not None:
            print(temp.value)
            temp = temp.next

    def append(self, value: Any) -> bool:
        new_node = Node(value)
        if self.lenght == 0:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.lenght += 1
        return True

    def pop(self) -> Optional[Node]:
        if self.lenght == 0:
            return None

        pre = self.head
        temp = self.head

        while temp.next:
            pre = temp
            temp = temp.next

        self.tail = pre
        self.tail.next = None
        self.lenght -= 1

        if self.lenght == 0:
            self.head = None
            self.head = None

        return temp

    def preappend(self, value: Any) -> bool:
        new_node = Node(value)
        if self.lenght == 0:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.lenght += 1
        return True

    def pop_first(self) -> Optional[Any]:
        if self.lenght == 0:
            return None
        temp = self.head
        self.head = self.head.next
        temp.next = None
        self.lenght -= 1
        if self.lenght == 0:
            self.tail = None
        return temp

    def get(self, index):
        if self.lenght < 0 or index >= self.lenght:
            return None
        temp = self.head
        for _ in range(index):
            temp = temp.next
        return temp
