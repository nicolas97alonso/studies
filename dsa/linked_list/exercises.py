from ll import LinkedList, Node


# 1. Find middle node
def find_middle_node(ll: LinkedList) -> Node:
    slow = ll.head
    fast = ll.head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    return slow


# 2. Has loop


def has_loop(ll: LinkedList) -> bool:
    slow = ll.head
    fast = ll.head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True

    return False


# 3. Find kth node from end


def find_k_end_node(ll: LinkedList, i: int) -> Node:
    slow = ll.head
    fast = ll.head

    for _ in range(i):
        fast = fast.next
        if not fast:
            return None

    while fast:
        slow = slow.next
        fast = fast.next

    return slow


# 4. Remove duplicates


if __name__ == "__main__":

    ll = LinkedList()
    ll.append(3)
    ll.append(4)
    ll.append(6)
    ll.append(2)
    ll.append(1)

    ll.print_list()
    print("--------")
    print("Check middle node")
    print(find_middle_node(ll).value)
    print("--------")
    print("Check has loop false")
    print(has_loop(ll))
    print("--------")
    ll2 = LinkedList()
    ll2.append(3)
    ll2.append(4)
    ll2.append(6)
    ll2.append(2)
    ll2.append(1)
    ll2.tail.next = ll2.head
    print("Check k end node i = 1, 1")
    print(find_k_end_node(ll, 1).value)
    print("--------")
    print("Check k end node i = 2, 2")
    print(find_k_end_node(ll, 2).value)
    print("--------")
    print("Check k end node i = 3, 6")
    print(find_k_end_node(ll, 3).value)
    print("--------")
