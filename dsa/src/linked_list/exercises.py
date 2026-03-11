from .ll import LinkedList, Node


def find_middle_node(ll: LinkedList) -> Node:
    slow = ll.head
    fast = ll.head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow


def has_loop(ll: LinkedList) -> Node:
    slow = ll.head
    fast = ll.head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if fast == slow:
            return True
    return False


# TODO: Investigate unnit test

if __name__ == "__main__":
    ll = LinkedList()
    ll.append(2)
    ll.append(3)
    ll.append(2)
    ll.print_list()
    print("----------")
    print("find_middle_node_test")
    print(find_middle_node(ll).value)
    print("----------")
    ll.append(4)
    ll.print_list()
    print("----------")
    print("find_middle_node_test")
    print(find_middle_node(ll).value)
    print("----------")
    print("has_loop_test")
    ll2 = LinkedList()
    ll2.append(2)
    ll2.append(3)
    ll2.append(4)
    ll2.tail = ll2.head
    print(has_loop(ll2))
