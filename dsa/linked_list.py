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

    def pop_first(self) -> Optional[Node]:
        if self.lenght == 0:
            return None
        temp = self.head
        self.head = self.head.next
        temp.next = None
        self.lenght -= 1
        if self.lenght == 0:
            self.tail = None
        return temp

    def get(self, index: int) -> Opitional[Node]:
        if index < 0 or index >= self.lenght:
            return None
        temp = self.head
        for _ in range(index):
            temp = temp.next
        return temp

    def set_value(self, index: int, value: Any) -> bool:
        temp = self.get(index)
        if temp:
            temp.value = value
            return True
        return False

    def insert(self, index: int, value: Any) -> bool:
        if index < 0 or index > self.lenght:
            return False
        if index == 0:
            return self.preappend(value)
        if index == self.lenght:
            return self.append(value)
        new_node = Node(value)
        pre = self.get(index - 1)
        new_node.next = pre.next
        pre.next = new_node
        self.lenght += 1
        return True

    def remove(self, index: int) -> Node:
        if index < 0 or index >= self.lenght:
            return None
        if index == 0:
            return self.pop_first()
        if index == (self.lenght - 1):
            return self.pop()
        pre = self.get(index - 1)
        temp = pre.next
        pre.next = temp.next
        temp.next = None
        self.lenght -= 1
        return temp

    def reverse(self) -> None:
        temp = self.head
        self.head = self.tail
        self.tail = temp
        after = temp.next
        before = None
        for _ in range(self.lenght):
            after = temp.next
            temp.next = before
            before = temp
            temp = after
