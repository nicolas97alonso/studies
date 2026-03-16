from src.linked_list.ll import LinkedList, Node


def find_middle_node(ll: LinkedList) -> Node:
    slow = ll.head
    fast = ll.head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow


def has_loop(ll: LinkedList) -> bool:
    slow = ll.head
    fast = ll.head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if fast == slow:
            return True
    return False


def find_kth_from_end(ll, k) -> Node | None:
    if not ll.head:
        return None
    slow = ll.head
    fast = ll.head

    for _ in range(k):
        fast = fast.next
        if not fast:
            return None

    while fast:
        slow = slow.next
        fast = fast.next

    return slow


def delete_duplicates(ll) -> bool | None:
    if not ll.head:
        return None

    slow = ll.head

    while slow:
        prev = slow
        fast = slow.next

        while fast:
            if fast.value == slow.value:

                to_delete = fast

                prev.next = fast.next
                fast = prev.next

                to_delete.next = None
            else:
                prev = fast
                fast = fast.next

        slow = slow.next

    return True
