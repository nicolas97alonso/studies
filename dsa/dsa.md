# Data Structures and Algorithms – Chapter 1 Notes

## What Are Data Structures and Algorithms?

### Data Structures
Ways of organizing and storing data so operations can be performed efficiently.  
Examples: arrays, linked lists, stacks, queues, trees, graphs, hash tables.

### Algorithms
Step-by-step procedures to solve problems.  
Examples: searching, sorting, traversing, inserting, deleting.

### Why They Matter
Choosing the right data structure + algorithm affects:
- speed  
- memory usage  
- scalability  
- code clarity  

---

# Big O Notation

Big O describes **how the runtime or memory usage of an algorithm grows** as the input size `n` increases.

It does **not** measure:
- seconds  
- CPU cycles  
- actual runtime  

Instead, it measures **growth rate**.

---

## Why We Use Big O

- Different machines run code at different speeds.  
- Big O ignores hardware and focuses on the *shape* of the growth.  
- It lets us compare algorithms in a universal way.

Example:  
An algorithm that takes `n²` steps will always grow faster than one that takes `n` steps, no matter the computer.

---

## Why We Drop Constants

### Rule
O(2n) → O(n)
O(1000n + 500) → O(n)


### Reason
Big O describes **growth**, not exact operations.

If you double the input size:
- `2n` becomes `4n`
- `n` becomes `2n`

Both grow **linearly**.  
The constant multiplier (2, 1000, etc.) doesn’t change the *shape* of the growth.

### Analogy
Two cars drive in a straight line:
- One at 100 km/h  
- One at 120 km/h  

Both are still **linear**.  
The speed difference is a constant factor — irrelevant when analyzing long‑term growth.

---

## Why We Drop Non‑Dominant Terms

### Rule
O(n² + n) → O(n²)


### Reason
As `n` gets large:
- `n²` grows MUCH faster than `n`
- The smaller term becomes insignificant

Example:  
If `n = 1,000,000`:
- `n² = 1,000,000,000,000`
- `n = 1,000,000`

The linear term is irrelevant compared to the quadratic term.

---

## Common Time Complexities

| Big O | Name | Example |
|-------|-------|---------|
| **O(1)** | Constant | Accessing array index |
| **O(n)** | Linear | Loop through list |
| **O(log n)** | Logarithmic | Binary search |
| **O(n log n)** | Log-linear | Merge sort |
| **O(n²)** | Quadratic | Nested loops |
| **O(2ⁿ)** | Exponential | Subset generation |
| **O(n!)** | Factorial | Traveling salesman brute force |

---

# Classes (Python)

A **class** is a blueprint for creating objects.  
It defines:
- **attributes** (data)
- **methods** (functions that operate on that data)

Example idea:  
A `Car` class might define:
- attributes: `color`, `brand`, `speed`
- methods: `drive()`, `stop()`

Objects created from a class are called **instances**.

---

# Pointers (Python Perspective)

Python does **not** store values inside variables.  
Instead:
- Every value lives in memory as an **object**
- A variable is a **pointer/reference** to that object

### Example

n1 = 2
n2 = n1

Both variables point to the same integer object 2.

When you do:

python
n2 = 3
n2 now points to a new object.
n1 still points to 2.

## Mutable vs Immutable Types
### Immutable Types
Examples:

int

float

str

tuple

You cannot modify the object.
Any “change” creates a new object.

Example:

python
n1 = 2
n2 = n1
n2 = 5
Now:

n1 → 2

n2 → 5
Two different memory locations.

### Mutable Types
Examples:

list

dict

set

You can modify the object in place.

Example:
l1 = [0, 2]
l2 = l1
l2.append(3)
Both variables point to the same list:


l1 = [0, 2, 3]
l2 = [0, 2, 3]

### Garbage Collection
Python automatically removes objects from memory when no variable references them anymore.

Example:

python
x = [1, 2, 3]
x = [4, 5]
The list [1, 2, 3] has no references → Python deletes it.

This process is called garbage collection.
