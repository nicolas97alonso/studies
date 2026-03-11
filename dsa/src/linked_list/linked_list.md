# Linked Lists

A **linked list** is a linear data structure where elements (nodes) are connected using pointers rather than stored next to each other in memory.

---

## How Linked Lists Differ From Normal (Python) Lists

### 1. No Indexes
Linked lists **do not have indexes**.  
To access the 5th element, you must start at the head and follow `.next` pointers until you reach it.

### 2. Not Stored Contiguously in Memory
In a linked list, nodes are **scattered in memory**, not placed next to each other.

### What does “not contiguous” mean?
- In a normal list (like Python’s `list` or an array in lower-level languages), elements are stored **back‑to‑back** in memory.
- In a linked list, each node can be **anywhere** in memory.  
  Each node stores:
  - a **value**
  - a **pointer** to the next node

### Why does this matter?
| Feature | Contiguous (Array/List) | Non‑Contiguous (Linked List) |
|--------|--------------------------|-------------------------------|
| Random access | **O(1)** (jump to index) | **O(n)** (must traverse) |
| Insert/delete at middle | Slow (must shift elements) | Fast (just change pointers) |
| Memory usage | Must allocate a big block | Can grow one node at a time |

Python lists are dynamic arrays → they **do** use contiguous memory internally.

Linked lists do **not**.

* In normal words, a linked list is compossed of nodes, each node have a value and the adress of the next.(pointer)
In a normal list, if we want to insert an element or delete, we will have to search the position, then shift all the indexes, in a linked list, we just need to change the adresses, is is less steps and shifting all the indexes.
Linked list are bad for searching, because you will have to itereate over the nodes until you find the match 

---

## Structure of a Linked List

A linked list typically keeps track of:
- **head** → first node
- **tail** → last node
- each node → points to the **next** node
- last node → points to **None**

Example visualization:

[Value | Next] → [Value | Next] → [Value | None]
↑
head
↑
tail


---

# Big O of Linked List Operations

## Append New Tail — **O(1)**
If we already track the `tail`:
- Create a new node
- Set `tail.next` to the new node
- Update `tail`

No traversal needed → constant time.

---

## Remove Tail Node — **O(n)**

### Why is this O(n)?
Even though we know where the tail is, we **do not know the node before the tail**.

To remove the last node, we must:
1. Start at the head
2. Traverse until we reach the node whose `.next` is the tail
3. Set that node as the new tail
4. Set its `.next` to `None`

This requires walking through the entire list → **O(n)**.

---

## Add New Head — **O(1)**
- Create a new node
- Set its `.next` to the current head
- Update `head`

No traversal needed.

---

## Remove Head — **O(1)**
- Move `head` to `head.next`
- Old head becomes unreferenced (garbage collected)

Instant operation.

---

## Insert in the Middle — **O(n)**
To insert at position `k`:
- Traverse from head to the `(k-1)`th node → O(n)
- Change pointers

Traversal dominates the cost.

---

## Remove an Item — **O(n)**
To remove a node by value:
- Traverse until you find the node
- Update pointers

Again, traversal → O(n).

---

## Lookup (by value or index) — **O(n)**
Linked lists cannot jump to an index.  
You must walk node by node until you find the target.

---

# What Is a Node?

A **node** is the basic building block of a linked list.

A node contains:
- a **value**
- a **pointer** to the next node

Conceptually, you can imagine a node like a dictionary:

```python
{
  "value": 4,
  "next": None
}

# 🧩 What is a *reference* in Python?
A **reference** is a variable that refers to an object stored somewhere in memory.  
You never see the memory address, but the variable still “points” to that object behind the scenes.  
It behaves like a pointer, just without exposing low‑level details.

---

# 🐍 Why Python uses references instead of raw addresses
Python is a high‑level language designed to be safe and easy to use.  
Instead of giving you numeric memory addresses (like C pointers), Python gives you **references**.  
They let you link objects together exactly like pointers do, but Python manages the memory for you.

---

# 🔗 What are `head` and `tail` in a linked list?
`head` and `tail` are **just variables that store references to Node objects**.

- **head** → reference to the *first* node in the list  
- **tail** → reference to the *last* node in the list  

They are not special objects or special types.  
They simply help you quickly access the beginning and end of the list.

---

# 🧠 Putting it all together
- Each Node stores a value and a **reference** to the next Node.  
- Python hides the memory address, but the behavior is the same as a pointer.  
- `head` and `tail` are variables that **refer to the first and last Node objects**, making traversal and appending efficient.

