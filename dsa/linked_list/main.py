class Node:
    def __init__(self, value) -> None:
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self, value=None) -> None:
        self.head = None
        self.tail = None
        self.lenght = 0
        if value is not None:
            new_node = Node(value)
            self.head = new_node
            self.tail = new_node
            self.lenght = 1

    def print_list(self):
        temp = self.head
        while temp is not None:
            print(temp.value)
            temp = temp.next

    def append(self, value) -> None:
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.lenght += 1
        return True

    def pop(self) -> None:
        if self.head is None:
            return None
        elif self.head == self.tail:
            temp = self.head
            self.head = None
            self.tail = None
            self.lenght = 0
            return temp
        else:
            temp = self.head
            pre = self.head

            while temp.next is not None:
                pre = temp
                temp = temp.next

            self.tail = pre
            self.tail.next = None
            self.lenght -= 1
            return temp


test = LinkedList(3)
test.append(4)
test.print_list()
test.pop()
test.print_list()
