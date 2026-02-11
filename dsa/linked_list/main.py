from linked_list import *

lined_list = LinkedList(3)
lined_list.append(2)
lined_list.print_list()
print("Now i will prepend")
lined_list.preappend(7)
lined_list.print_list()
print("Now i will pop")
lined_list.pop()
lined_list.print_list()

print("Now i will pre pop")
lined_list.pop_first()
lined_list.print_list()
